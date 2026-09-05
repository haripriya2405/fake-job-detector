from datetime import datetime, timezone
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from app.ml.calibration import ModelCalibrator
from app.ml.schemas import ModelEvaluationMetrics


class ModelEvaluator:
    """Computes statistical metrics, confusion matrices, and probability calibration."""

    def __init__(self):
        self.calibrator = ModelCalibrator()

    def evaluate(
        self,
        model: Any,
        X_test: pd.Series,
        y_test: pd.Series,
        model_name: str,
        version: str,
        algorithm: str,
        dataset_name: str,
        train_samples: int,
        val_samples: int,
        test_samples: int,
    ) -> ModelEvaluationMetrics:
        y_pred = model.predict(X_test)
        
        roc_auc = None
        calibration_results = {}
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test)[:, 1]
            try:
                roc_auc = float(roc_auc_score(y_test, y_prob))
            except Exception:
                roc_auc = None

            try:
                calibration_results = self.calibrator.evaluate_calibration(
                    y_true=y_test.to_numpy(),
                    y_prob=y_prob,
                    n_bins=min(5, len(y_test)),
                )
            except Exception:
                calibration_results = {}

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))

        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

        clf_report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        clf_report["calibration"] = calibration_results
        clf_report["class_distribution"] = {
            "negative_samples": int(np.sum(y_test == 0)),
            "positive_samples": int(np.sum(y_test == 1)),
            "total_test_samples": int(len(y_test)),
        }

        return ModelEvaluationMetrics(
            model_name=model_name,
            version=version,
            algorithm=algorithm,
            accuracy=acc,
            precision=prec,
            recall=rec,
            f1_score=f1,
            roc_auc=roc_auc,
            confusion_matrix=cm.tolist(),
            dataset_name=dataset_name,
            train_samples=train_samples,
            val_samples=val_samples,
            test_samples=test_samples,
            classification_report=clf_report,
            false_positives=int(fp),
            false_negatives=int(fn),
            created_at=datetime.now(timezone.utc),
        )
