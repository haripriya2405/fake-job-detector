"""Model Comparative Benchmarking Engine (Phase 20).
Evaluates Active Production Baseline (logisticregression-v1.0.0) and Candidate (transformer-v1.0.0-candidate)
on the exact same untouched holdout dataset, generating a comprehensive side-by-side metric matrix.
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

from app.core.logging import logger
from app.ml.calibration import ModelCalibrator
from app.ml.predictor import MLPredictor
from app.ml.statistical_tests import StatisticalComparator


class ModelComparator:
    """Evaluates and compares baseline and candidate ML predictors on identical holdout samples."""

    def __init__(
        self,
        baseline_predictor: Optional[MLPredictor] = None,
        candidate_predictor: Optional[MLPredictor] = None,
    ):
        self.baseline = baseline_predictor or MLPredictor(artifact_path="artifacts/models/tfidf_logistic_regression_v1.0.0.joblib")
        # Load ONNX candidate if available, else default to candidate path
        self.candidate = candidate_predictor or MLPredictor(artifact_path="artifacts/models/transformer-cloud-1787075009.onnx")
        self.calibrator = ModelCalibrator()
        self.stats = StatisticalComparator()

    def evaluate_model_on_holdout(
        self,
        predictor: MLPredictor,
        holdout_df: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Compute all classification, ranking, and calibration metrics for a single predictor."""
        y_true = holdout_df["label"].values.astype(int)
        raw_texts = holdout_df["text"].tolist()

        probabilities = []
        latencies = []

        for text in raw_texts:
            t0 = time.perf_counter()
            pred_out = predictor.predict(text)
            lat_ms = (time.perf_counter() - t0) * 1000.0
            latencies.append(lat_ms)
            prob = pred_out.probability if pred_out else 0.0
            probabilities.append(prob)

        y_prob = np.array(probabilities)
        y_pred = (y_prob >= 0.50).astype(int)

        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

        # Classification Metrics
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        acc = float(accuracy_score(y_true, y_pred))
        bal_acc = float(balanced_accuracy_score(y_true, y_pred))
        mcc = float(matthews_corrcoef(y_true, y_pred)) if len(np.unique(y_pred)) > 1 else 0.0

        fpr = float(fp / (tn + fp)) if (tn + fp) > 0 else 0.0
        fnr = float(fn / (tp + fn)) if (tp + fn) > 0 else 0.0
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

        # AUC & Ranking Metrics
        has_both_classes = len(np.unique(y_true)) > 1
        roc_auc = float(roc_auc_score(y_true, y_prob)) if has_both_classes else 0.5
        pr_auc = float(average_precision_score(y_true, y_prob)) if has_both_classes else 0.0

        # Calibration
        calib = self.calibrator.evaluate_calibration(y_true, y_prob, n_bins=5)

        return {
            "model_version": predictor.model_version,
            "algorithm": predictor.algorithm,
            "sample_count": len(y_true),
            "confusion_matrix": {
                "tp": int(tp),
                "tn": int(tn),
                "fp": int(fp),
                "fn": int(fn),
            },
            "metrics": {
                "accuracy": round(acc, 4),
                "balanced_accuracy": round(bal_acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
                "specificity": round(specificity, 4),
                "false_positive_rate": round(fpr, 4),
                "false_negative_rate": round(fnr, 4),
                "matthews_correlation_coefficient": round(mcc, 4),
                "roc_auc": round(roc_auc, 4),
                "pr_auc": round(pr_auc, 4),
                "brier_score": round(calib["brier_score"], 4),
                "expected_calibration_error": round(calib["expected_calibration_error"], 4),
            },
            "latency": {
                "mean_ms": round(float(np.mean(latencies)), 2),
                "p50_ms": round(float(np.percentile(latencies, 50)), 2),
                "p95_ms": round(float(np.percentile(latencies, 95)), 2),
                "p99_ms": round(float(np.percentile(latencies, 99)), 2),
            },
            "raw_probabilities": y_prob.tolist(),
            "raw_predictions": y_pred.tolist(),
            "calibration_curve": {
                "prob_true": calib["prob_true"],
                "prob_pred": calib["prob_pred"],
            },
        }

    def compare_models(self, holdout_df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive side-by-side evaluation on identical holdout samples."""
        base_results = self.evaluate_model_on_holdout(self.baseline, holdout_df)
        cand_results = self.evaluate_model_on_holdout(self.candidate, holdout_df)

        y_true = holdout_df["label"].values.astype(int)
        base_probs = np.array(base_results["raw_probabilities"])
        cand_probs = np.array(cand_results["raw_probabilities"])
        base_preds = np.array(base_results["raw_predictions"])
        cand_preds = np.array(cand_results["raw_predictions"])

        # Delta metrics (Candidate - Baseline)
        delta_metrics = {}
        for k in base_results["metrics"]:
            b_val = base_results["metrics"][k]
            c_val = cand_results["metrics"][k]
            delta_metrics[k] = round(c_val - b_val, 4)

        # Statistical paired tests
        mcnemar = self.stats.perform_mcnemar_test(y_true, base_preds, cand_preds)
        prauc_diff = self.stats.compute_paired_metric_difference(y_true, base_probs, cand_probs, "pr_auc")
        f1_diff = self.stats.compute_paired_metric_difference(y_true, base_probs, cand_probs, "f1")
        recall_diff = self.stats.compute_paired_metric_difference(y_true, base_probs, cand_probs, "threat_recall")
        fpr_diff = self.stats.compute_paired_metric_difference(y_true, base_probs, cand_probs, "false_positive_rate")

        return {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "holdout_size": len(holdout_df),
            "baseline": base_results,
            "candidate": cand_results,
            "delta_metrics": delta_metrics,
            "statistical_significance": {
                "mcnemar_test": mcnemar,
                "paired_differences": {
                    "pr_auc": prauc_diff,
                    "f1": f1_diff,
                    "threat_recall": recall_diff,
                    "false_positive_rate": fpr_diff,
                },
            },
        }
