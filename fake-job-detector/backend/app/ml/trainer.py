"""Production Model Training, Calibration & Comparison Engine (Phase 7 & 7C).
Trains, calibrates, evaluates, and benchmarks:
- Model 1: Baseline Logistic Regression (logisticregression-v1.0.0)
- Model 2: Calibrated Logistic Regression (Tuned C, Sublinear TF-IDF, N-Gram 1-2)
- Model 3: Calibrated Linear SVM (LinearSVC + Platt Scaling via CalibratedClassifierCV)
Serializes verified model artifacts with SHA-256 integrity checksums.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from app.core.logging import logger
from app.ml.calibration import ModelCalibrator
from app.ml.preprocessing import TextPreprocessor
from app.ml.production_dataset import ProductionDatasetIngestion


class ModelTrainer:
    """Trains and compares candidate fraud detection classifiers across stratified splits."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.preprocessor = TextPreprocessor()
        self.calibrator = ModelCalibrator()

    def train_and_evaluate_all(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        holdout_df: pd.DataFrame,
        artifacts_dir: str = "artifacts",
    ) -> Dict[str, Any]:
        """Train baseline and candidate models, compute full metric suites, and rank performance."""
        os.makedirs(artifacts_dir, exist_ok=True)

        X_train_raw = train_df["raw_text"].tolist()
        y_train = train_df["label"].values

        X_val_raw = val_df["raw_text"].tolist()
        y_val = val_df["label"].values

        X_holdout_raw = holdout_df["raw_text"].tolist()
        y_holdout = holdout_df["label"].values

        # Preprocess texts using clean_text
        X_train = [self.preprocessor.clean_text(t) for t in X_train_raw]
        X_val = [self.preprocessor.clean_text(t) for t in X_val_raw]
        X_holdout = [self.preprocessor.clean_text(t) for t in X_holdout_raw]

        models_to_evaluate = {
            "logisticregression-v1.0.0 (Baseline)": Pipeline([
                ("tfidf", TfidfVectorizer(max_features=4000, ngram_range=(1, 2), sublinear_tf=True, stop_words="english")),
                ("clf", LogisticRegression(C=1.2, class_weight="balanced", random_state=self.random_state, max_iter=1000)),
            ]),
            "logisticregression-v2.0.0-candidate": Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words="english")),
                ("clf", LogisticRegression(C=1.8, class_weight="balanced", solver="lbfgs", random_state=self.random_state, max_iter=1000)),
            ]),
            "linearsvm-v2.0.0-candidate (Platt Scaled)": Pipeline([
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True, min_df=1, stop_words="english")),
                ("clf", CalibratedClassifierCV(
                    estimator=LinearSVC(C=1.0, class_weight="balanced", random_state=self.random_state, max_iter=3000),
                    method="sigmoid",
                    cv=3,
                )),
            ]),
        }

        evaluation_results: Dict[str, Any] = {}

        for model_name, pipeline in models_to_evaluate.items():
            start_t = time.perf_counter()
            pipeline.fit(X_train, y_train)
            train_duration_ms = round((time.perf_counter() - start_t) * 1000, 2)

            # Evaluate on Validation Split
            val_metrics = self._compute_metrics(pipeline, X_val, y_val)

            # Evaluate on Final Untouched Holdout Split
            holdout_metrics = self._compute_metrics(pipeline, X_holdout, y_holdout)

            # Cost Analysis: False Negative Cost (10x) vs False Positive Cost (1x)
            cm_holdout = holdout_metrics["confusion_matrix"]
            cost_fn = cm_holdout["FN"] * 10.0
            cost_fp = cm_holdout["FP"] * 1.0
            total_decision_loss = cost_fn + cost_fp

            # Extract Top Predictive Indicators if supported
            top_fraud_cues = self._extract_top_features(pipeline, n=8)

            evaluation_results[model_name] = {
                "model_name": model_name,
                "train_duration_ms": train_duration_ms,
                "validation_metrics": val_metrics,
                "holdout_metrics": holdout_metrics,
                "decision_loss": {
                    "fn_cost_weight": 10.0,
                    "fp_cost_weight": 1.0,
                    "total_holdout_decision_loss": total_decision_loss,
                },
                "top_features": top_fraud_cues,
                "pipeline_object": pipeline,
            }

        # Select Best Model Based on Multi-Factor Criteria
        best_candidate = self._select_best_model(evaluation_results)

        return {
            "models": evaluation_results,
            "best_selected_model": best_candidate,
            "train_set_size": len(train_df),
            "val_set_size": len(val_df),
            "holdout_set_size": len(holdout_df),
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }

    def serialize_candidate_artifact(
        self,
        pipeline: Pipeline,
        version: str = "v2.0.0",
        algorithm: str = "LinearSVC",
        metrics: Optional[Dict[str, Any]] = None,
        artifacts_dir: str = "artifacts/models",
    ) -> Tuple[str, str]:
        """Serialize candidate model pipeline and manifest metadata with SHA-256 checksum."""
        os.makedirs(artifacts_dir, exist_ok=True)
        filename = f"tfidf_{algorithm.lower()}_{version}.joblib"
        artifact_path = os.path.join(artifacts_dir, filename)
        meta_path = os.path.join(artifacts_dir, f"tfidf_{algorithm.lower()}_{version}.meta.json")

        joblib.dump(pipeline, artifact_path)

        with open(artifact_path, "rb") as f:
            checksum = hashlib.sha256(f.read()).hexdigest()

        meta_content = {
            "version": version,
            "algorithm": algorithm,
            "filename": filename,
            "sha256_checksum": checksum,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics or {},
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_content, f, indent=2)

        logger.info(f"Serialized model artifact to {artifact_path} (SHA-256: {checksum[:16]}...)")
        return artifact_path, meta_path

    def _compute_metrics(self, pipeline: Pipeline, X: List[str], y: np.ndarray) -> Dict[str, Any]:
        """Compute complete metric suite including ROC-AUC, PR-AUC, Brier score, ECE, and confusion matrix."""
        y_pred = pipeline.predict(X)

        if hasattr(pipeline, "predict_proba"):
            y_prob = pipeline.predict_proba(X)[:, 1]
        else:
            decision = pipeline.decision_function(X)
            y_prob = 1 / (1 + np.exp(-decision))

        acc = accuracy_score(y, y_pred)
        prec = precision_score(y, y_pred, zero_division=0)
        rec = recall_score(y, y_pred, zero_division=0)
        f1 = f1_score(y, y_pred, zero_division=0)

        try:
            roc_auc = roc_auc_score(y, y_prob)
        except Exception:
            roc_auc = 0.5

        try:
            pr_auc = average_precision_score(y, y_prob)
        except Exception:
            pr_auc = 0.5

        cm = confusion_matrix(y, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        cal_eval = self.calibrator.evaluate_calibration(y_true=y, y_prob=y_prob, n_bins=5)

        return {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "false_positive_rate": round(float(fpr), 4),
            "false_negative_rate": round(float(fnr), 4),
            "brier_score": cal_eval.get("brier_score", 0.0),
            "expected_calibration_error": cal_eval.get("expected_calibration_error", 0.0),
            "confusion_matrix": {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)},
        }

    def _extract_top_features(self, pipeline: Pipeline, n: int = 8) -> List[Dict[str, Any]]:
        """Extract top positive (fraud-indicative) n-grams from vectorizer/classifier coefficients."""
        try:
            tfidf = pipeline.named_steps["tfidf"]
            clf = pipeline.named_steps["clf"]
            feature_names = tfidf.get_feature_names_out()

            if hasattr(clf, "coef_"):
                coefs = clf.coef_[0]
            elif hasattr(clf, "calibrated_classifiers_"):
                coef_list = [c.estimator.coef_[0] for c in clf.calibrated_classifiers_ if hasattr(c.estimator, "coef_")]
                coefs = np.mean(coef_list, axis=0) if coef_list else None
            else:
                coefs = None

            if coefs is None:
                return []

            top_indices = np.argsort(coefs)[::-1][:n]
            return [
                {"feature": str(feature_names[idx]), "weight": round(float(coefs[idx]), 4)}
                for idx in top_indices
            ]
        except Exception:
            return []

    def _select_best_model(self, results: Dict[str, Any]) -> str:
        """Select champion model balancing F1, Recall, Generalization, and Calibration."""
        scored_candidates = []
        for name, data in results.items():
            h_metrics = data["holdout_metrics"]

            # Composite Score: Recall (0.35) + Precision (0.25) + F1 (0.25) - Brier Penalty (0.15)
            comp_score = (
                0.35 * h_metrics["recall"]
                + 0.25 * h_metrics["precision"]
                + 0.25 * h_metrics["f1_score"]
                - 0.15 * min(1.0, h_metrics["brier_score"])
            )
            scored_candidates.append((comp_score, name))

        scored_candidates.sort(reverse=True)
        best_name = scored_candidates[0][1]
        logger.info(f"Model Selection Champion: '{best_name}' (Composite Score: {scored_candidates[0][0]:.4f})")
        return best_name
