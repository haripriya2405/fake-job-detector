"""Validation Threshold Analysis & Cost-Sensitive Tuning Engine (Phase 7C).
Evaluates decision thresholds on VALIDATION DATA ONLY to prevent holdout contamination.
Selected threshold is evaluated once on the untouched contemporary holdout.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


class ThresholdAnalyzer:
    """Performs threshold search on validation split and single-pass evaluation on holdout."""

    DEFAULT_THRESHOLDS = [0.30, 0.40, 0.50, 0.60, 0.70]

    def __init__(self, fn_cost_weight: float = 10.0, fp_cost_weight: float = 1.0):
        self.fn_cost_weight = fn_cost_weight
        self.fp_cost_weight = fp_cost_weight

    def evaluate_threshold_grid(
        self,
        y_val: np.ndarray,
        y_val_prob: np.ndarray,
        thresholds: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Evaluate grid of decision thresholds on VALIDATION DATA ONLY."""
        thresholds = thresholds or self.DEFAULT_THRESHOLDS
        grid_results = []

        best_loss = float("inf")
        optimal_threshold = 0.50

        for tau in thresholds:
            y_pred_tau = (y_val_prob >= tau).astype(int)

            prec = precision_score(y_val, y_pred_tau, zero_division=0)
            rec = recall_score(y_val, y_pred_tau, zero_division=0)
            f1 = f1_score(y_val, y_pred_tau, zero_division=0)

            cm = confusion_matrix(y_val, y_pred_tau, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()

            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

            loss = (fn * self.fn_cost_weight) + (fp * self.fp_cost_weight)

            res_entry = {
                "threshold": round(float(tau), 2),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "f1_score": round(float(f1), 4),
                "false_positive_rate": round(float(fpr), 4),
                "false_negative_rate": round(float(fnr), 4),
                "decision_loss": round(float(loss), 2),
                "confusion_matrix": {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)},
            }
            grid_results.append(res_entry)

            if loss < best_loss:
                best_loss = loss
                optimal_threshold = tau

        return {
            "validation_grid": grid_results,
            "optimal_threshold": optimal_threshold,
            "min_validation_decision_loss": best_loss,
        }

    def evaluate_on_holdout(
        self,
        y_holdout: np.ndarray,
        y_holdout_prob: np.ndarray,
        selected_threshold: float,
    ) -> Dict[str, Any]:
        """Evaluate the pre-selected threshold ONCE on the untouched holdout."""
        y_pred = (y_holdout_prob >= selected_threshold).astype(int)

        prec = precision_score(y_holdout, y_pred, zero_division=0)
        rec = recall_score(y_holdout, y_pred, zero_division=0)
        f1 = f1_score(y_holdout, y_pred, zero_division=0)

        cm = confusion_matrix(y_holdout, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
        loss = (fn * self.fn_cost_weight) + (fp * self.fp_cost_weight)

        return {
            "evaluated_threshold": round(float(selected_threshold), 2),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "false_positive_rate": round(float(fpr), 4),
            "false_negative_rate": round(float(fnr), 4),
            "decision_loss": round(float(loss), 2),
            "confusion_matrix": {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)},
        }
