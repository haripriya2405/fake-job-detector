"""Statistical Evaluation, Cross-Validation & Bootstrap Confidence Intervals (Phase 7C).
Computes:
- 5-Fold Stratified Cross-Validation on development splits
- Non-parametric Percentile Bootstrap Confidence Intervals (B=1000, 95% CI)
- Statistical Power & Sample Size Adequacy Assessment
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline


class ModelStatisticsEvaluator:
    """Computes statistical metrics, bootstrap confidence intervals, and power adequacy."""

    def __init__(self, n_bootstrap: int = 1000, alpha: float = 0.05, random_state: int = 42):
        self.n_bootstrap = n_bootstrap
        self.alpha = alpha
        self.random_state = random_state

    def compute_stratified_cv(
        self,
        pipeline_builder: Callable[[], Pipeline],
        X: List[str],
        y: np.ndarray,
        n_splits: int = 5,
    ) -> Dict[str, Dict[str, float]]:
        """Perform Stratified K-Fold Cross-Validation on training/dev set."""
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=self.random_state)

        f1_scores = []
        rec_scores = []
        prec_scores = []
        roc_scores = []
        acc_scores = []

        X_arr = np.array(X, dtype=object)

        for train_idx, val_idx in skf.split(X_arr, y):
            X_tr, y_tr = X_arr[train_idx].tolist(), y[train_idx]
            X_va, y_va = X_arr[val_idx].tolist(), y[val_idx]

            pipe = pipeline_builder()
            pipe.fit(X_tr, y_tr)

            y_va_pred = pipe.predict(X_va)
            if hasattr(pipe, "predict_proba"):
                y_va_prob = pipe.predict_proba(X_va)[:, 1]
            else:
                y_va_prob = y_va_pred.astype(float)

            acc_scores.append(accuracy_score(y_va, y_va_pred))
            prec_scores.append(precision_score(y_va, y_va_pred, zero_division=0))
            rec_scores.append(recall_score(y_va, y_va_pred, zero_division=0))
            f1_scores.append(f1_score(y_va, y_va_pred, zero_division=0))

            try:
                roc_scores.append(roc_auc_score(y_va, y_va_prob))
            except Exception:
                roc_scores.append(0.5)

        return {
            "accuracy": {"mean": round(float(np.mean(acc_scores)), 4), "std": round(float(np.std(acc_scores)), 4)},
            "precision": {"mean": round(float(np.mean(prec_scores)), 4), "std": round(float(np.std(prec_scores)), 4)},
            "recall": {"mean": round(float(np.mean(rec_scores)), 4), "std": round(float(np.std(rec_scores)), 4)},
            "f1_score": {"mean": round(float(np.mean(f1_scores)), 4), "std": round(float(np.std(f1_scores)), 4)},
            "roc_auc": {"mean": round(float(np.mean(roc_scores)), 4), "std": round(float(np.std(roc_scores)), 4)},
            "k_folds": n_splits,
        }

    def compute_bootstrap_confidence_intervals(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray,
    ) -> Dict[str, Dict[str, Any]]:
        """Compute 95% bootstrap confidence intervals for classification metrics."""
        n_samples = len(y_true)
        rng = np.random.default_rng(self.random_state)

        boot_f1 = []
        boot_rec = []
        boot_prec = []
        boot_fpr = []
        boot_roc = []
        boot_pr = []
        boot_acc = []

        for _ in range(self.n_bootstrap):
            indices = rng.choice(n_samples, size=n_samples, replace=True)
            y_t_boot = y_true[indices]
            y_p_boot = y_pred[indices]
            y_pr_boot = y_prob[indices]

            # Check if both classes are present in bootstrap resample
            if len(np.unique(y_t_boot)) < 2:
                continue

            cm = confusion_matrix(y_t_boot, y_p_boot, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()

            boot_acc.append(accuracy_score(y_t_boot, y_p_boot))
            boot_prec.append(precision_score(y_t_boot, y_p_boot, zero_division=0))
            boot_rec.append(recall_score(y_t_boot, y_p_boot, zero_division=0))
            boot_f1.append(f1_score(y_t_boot, y_p_boot, zero_division=0))
            boot_fpr.append(fp / (fp + tn) if (fp + tn) > 0 else 0.0)

            try:
                boot_roc.append(roc_auc_score(y_t_boot, y_pr_boot))
            except Exception:
                boot_roc.append(0.5)

            try:
                boot_pr.append(average_precision_score(y_t_boot, y_pr_boot))
            except Exception:
                boot_pr.append(0.5)

        def get_ci_bounds(values: List[float], point_est: float) -> Dict[str, Any]:
            if not values:
                return {"point_estimate": point_est, "ci_lower": point_est, "ci_upper": point_est, "ci_width": 0.0}
            low_pct = 100 * (self.alpha / 2.0)
            high_pct = 100 * (1.0 - self.alpha / 2.0)
            ci_low = float(np.percentile(values, low_pct))
            ci_high = float(np.percentile(values, high_pct))
            return {
                "point_estimate": round(float(point_est), 4),
                "ci_lower": round(ci_low, 4),
                "ci_upper": round(ci_high, 4),
                "ci_width": round(ci_high - ci_low, 4),
                "confidence_level": "95%",
            }

        # Point estimates
        cm_full = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn_f, fp_f, fn_f, tp_f = cm_full.ravel()
        fpr_pt = fp_f / (fp_f + tn_f) if (fp_f + tn_f) > 0 else 0.0

        try:
            roc_pt = roc_auc_score(y_true, y_prob)
        except Exception:
            roc_pt = 0.5

        try:
            pr_pt = average_precision_score(y_true, y_prob)
        except Exception:
            pr_pt = 0.5

        return {
            "accuracy": get_ci_bounds(boot_acc, accuracy_score(y_true, y_pred)),
            "precision": get_ci_bounds(boot_prec, precision_score(y_true, y_pred, zero_division=0)),
            "recall": get_ci_bounds(boot_rec, recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": get_ci_bounds(boot_f1, f1_score(y_true, y_pred, zero_division=0)),
            "false_positive_rate": get_ci_bounds(boot_fpr, fpr_pt),
            "roc_auc": get_ci_bounds(boot_roc, roc_pt),
            "pr_auc": get_ci_bounds(boot_pr, pr_pt),
            "bootstrap_samples_effective": len(boot_f1),
        }

    def assess_statistical_adequacy(self, holdout_size: int, fraud_count: int, legit_count: int) -> Dict[str, Any]:
        """Assess whether the holdout evaluation is adequately powered or underpowered."""
        # Standard sample size formula for proportion with margin of error d=0.05, 95% CI: N = (1.96^2 * 0.5 * 0.5) / 0.05^2 = 384
        target_adequate_sample_size = 384
        is_adequately_powered = holdout_size >= target_adequate_sample_size

        # Estimated margin of error for current sample size
        p = 0.5  # Worst-case variance
        z = 1.96  # 95% confidence
        margin_of_error = z * np.sqrt((p * (1 - p)) / max(1, holdout_size))

        return {
            "holdout_size": holdout_size,
            "fraud_examples": fraud_count,
            "legitimate_examples": legit_count,
            "target_adequate_sample_size": target_adequate_sample_size,
            "is_adequately_powered": bool(is_adequately_powered),
            "status": "ADEQUATE" if is_adequately_powered else "UNDERPOWERED (Sample Size Limited)",
            "estimated_margin_of_error": round(float(margin_of_error), 4),
            "statistical_limitation_note": (
                f"Holdout N={holdout_size} has an estimated margin of error of ±{margin_of_error:.2%}. "
                f"Statistical power is limited; large-scale generalization claims require N >= {target_adequate_sample_size}."
            ),
        }
