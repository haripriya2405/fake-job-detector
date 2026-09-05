"""Statistical Significance & Paired Hypothesis Testing Engine (Phase 20).
Implements:
1. Bootstrap 95% Confidence Intervals for classification & calibration metrics.
2. McNemar's Paired Disagreement Test with exact binomial & continuity-corrected Chi-Square.
3. Paired metric difference evaluation with confidence bounds and significance thresholds.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


class StatisticalComparator:
    """Computes rigorous statistical comparisons between baseline and candidate models."""

    def __init__(self, n_bootstraps: int = 1000, alpha: float = 0.05, random_state: int = 42):
        self.n_bootstraps = n_bootstraps
        self.alpha = alpha
        self.random_state = random_state

    def compute_metric_bootstrap_ci(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        metric_name: str,
        threshold: float = 0.50,
    ) -> Dict[str, float]:
        """Compute bootstrap 95% confidence intervals for a single metric."""
        rng = np.random.RandomState(self.random_state)
        n = len(y_true)
        if n == 0:
            return {"point_estimate": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "std_error": 0.0}

        y_true = np.asarray(y_true)
        y_prob = np.asarray(y_prob)
        y_pred = (y_prob >= threshold).astype(int)

        def eval_metric(yt: np.ndarray, yp: np.ndarray, ypred: np.ndarray) -> float:
            if metric_name == "f1":
                return float(f1_score(yt, ypred, zero_division=0))
            elif metric_name == "precision":
                return float(precision_score(yt, ypred, zero_division=0))
            elif metric_name == "recall" or metric_name == "threat_recall":
                return float(recall_score(yt, ypred, zero_division=0))
            elif metric_name == "false_positive_rate":
                cm = confusion_matrix(yt, ypred, labels=[0, 1])
                tn, fp = cm[0, 0], cm[0, 1]
                return float(fp / (tn + fp)) if (tn + fp) > 0 else 0.0
            elif metric_name == "roc_auc":
                if len(np.unique(yt)) < 2:
                    return 0.5
                return float(roc_auc_score(yt, yp))
            elif metric_name == "pr_auc":
                if len(np.unique(yt)) < 2:
                    return 0.0
                return float(average_precision_score(yt, yp))
            elif metric_name == "brier_score":
                return float(brier_score_loss(yt, yp))
            return 0.0

        point_est = eval_metric(y_true, y_prob, y_pred)
        boot_scores = []

        for _ in range(self.n_bootstraps):
            indices = rng.randint(0, n, size=n)
            bs_yt = y_true[indices]
            bs_yp = y_prob[indices]
            bs_ypred = y_pred[indices]

            # Ensure both classes present if computing AUC
            if metric_name in ["roc_auc", "pr_auc"] and len(np.unique(bs_yt)) < 2:
                continue

            score = eval_metric(bs_yt, bs_yp, bs_ypred)
            boot_scores.append(score)

        if not boot_scores:
            return {"point_estimate": point_est, "ci_lower": point_est, "ci_upper": point_est, "std_error": 0.0}

        lower_p = (self.alpha / 2.0) * 100.0
        upper_p = (1.0 - self.alpha / 2.0) * 100.0
        ci_lower = float(np.percentile(boot_scores, lower_p))
        ci_upper = float(np.percentile(boot_scores, upper_p))
        std_error = float(np.std(boot_scores))

        return {
            "point_estimate": round(float(point_est), 4),
            "ci_lower": round(ci_lower, 4),
            "ci_upper": round(ci_upper, 4),
            "std_error": round(std_error, 4),
        }

    def compute_paired_metric_difference(
        self,
        y_true: np.ndarray,
        base_prob: np.ndarray,
        cand_prob: np.ndarray,
        metric_name: str,
        threshold: float = 0.50,
    ) -> Dict[str, Any]:
        """Compute point estimates, absolute & relative differences, and bootstrap CI of difference."""
        base_stats = self.compute_metric_bootstrap_ci(y_true, base_prob, metric_name, threshold)
        cand_stats = self.compute_metric_bootstrap_ci(y_true, cand_prob, metric_name, threshold)

        abs_diff = cand_stats["point_estimate"] - base_stats["point_estimate"]
        rel_diff = (abs_diff / (base_stats["point_estimate"] + 1e-8)) if base_stats["point_estimate"] > 0 else 0.0

        # Paired bootstrap for difference
        rng = np.random.RandomState(self.random_state)
        n = len(y_true)
        diff_scores = []

        for _ in range(self.n_bootstraps):
            indices = rng.randint(0, n, size=n)
            bs_yt = y_true[indices]
            bs_bp = base_prob[indices]
            bs_cp = cand_prob[indices]
            bs_bpred = (bs_bp >= threshold).astype(int)
            bs_cpred = (bs_cp >= threshold).astype(int)

            if metric_name in ["roc_auc", "pr_auc"] and len(np.unique(bs_yt)) < 2:
                continue

            if metric_name == "f1":
                b_s = float(f1_score(bs_yt, bs_bpred, zero_division=0))
                c_s = float(f1_score(bs_yt, bs_cpred, zero_division=0))
            elif metric_name in ["recall", "threat_recall"]:
                b_s = float(recall_score(bs_yt, bs_bpred, zero_division=0))
                c_s = float(recall_score(bs_yt, bs_cpred, zero_division=0))
            elif metric_name == "false_positive_rate":
                b_cm = confusion_matrix(bs_yt, bs_bpred, labels=[0, 1])
                c_cm = confusion_matrix(bs_yt, bs_cpred, labels=[0, 1])
                b_s = float(b_cm[0, 1] / (b_cm[0, 0] + b_cm[0, 1])) if (b_cm[0, 0] + b_cm[0, 1]) > 0 else 0.0
                c_s = float(c_cm[0, 1] / (c_cm[0, 0] + c_cm[0, 1])) if (c_cm[0, 0] + c_cm[0, 1]) > 0 else 0.0
            elif metric_name == "pr_auc":
                b_s = float(average_precision_score(bs_yt, bs_bp))
                c_s = float(average_precision_score(bs_yt, bs_cp))
            elif metric_name == "brier_score":
                b_s = float(brier_score_loss(bs_yt, bs_bp))
                c_s = float(brier_score_loss(bs_yt, bs_cp))
            else:
                b_s, c_s = 0.0, 0.0

            diff_scores.append(c_s - b_s)

        if diff_scores:
            lower_p = (self.alpha / 2.0) * 100.0
            upper_p = (1.0 - self.alpha / 2.0) * 100.0
            diff_ci_lower = float(np.percentile(diff_scores, lower_p))
            diff_ci_upper = float(np.percentile(diff_scores, upper_p))
        else:
            diff_ci_lower = abs_diff
            diff_ci_upper = abs_diff

        return {
            "metric": metric_name,
            "baseline": base_stats,
            "candidate": cand_stats,
            "absolute_difference": round(float(abs_diff), 4),
            "relative_difference": round(float(rel_diff), 4),
            "difference_95_ci": [round(diff_ci_lower, 4), round(diff_ci_upper, 4)],
            "is_statistically_significant": bool(diff_ci_lower > 0 if metric_name != "brier_score" else diff_ci_upper < 0),
        }

    def perform_mcnemar_test(
        self,
        y_true: np.ndarray,
        base_pred: np.ndarray,
        cand_pred: np.ndarray,
    ) -> Dict[str, Any]:
        """Perform McNemar's test for paired classification disagreement."""
        y_true = np.asarray(y_true)
        base_pred = np.asarray(base_pred)
        cand_pred = np.asarray(cand_pred)

        base_correct = (base_pred == y_true)
        cand_correct = (cand_pred == y_true)

        # Contingency Matrix:
        # a: both correct
        # b: base correct, cand wrong
        # c: base wrong, cand correct
        # d: both wrong
        a = int(np.sum(base_correct & cand_correct))
        b = int(np.sum(base_correct & (~cand_correct)))
        c = int(np.sum((~base_correct) & cand_correct))
        d = int(np.sum((~base_correct) & (~cand_correct)))

        contingency_matrix = [[a, b], [c, d]]
        discordant_total = b + c

        if discordant_total == 0:
            return {
                "contingency_matrix": contingency_matrix,
                "both_correct_count": a,
                "baseline_only_correct_count": b,
                "candidate_only_correct_count": c,
                "both_wrong_count": d,
                "statistic": 0.0,
                "p_value": 1.0,
                "test_type": "exact_binomial",
                "is_significant": False,
                "interpretation": "Identical predictions; no significant difference between models.",
            }

        # Exact binomial test for small sample discordant pairs (b + c < 25)
        if discordant_total < 25:
            # Binomial test with p=0.5
            k = min(b, c)
            binom_result = stats.binomtest(k, n=discordant_total, p=0.5, alternative="two-sided")
            p_val = float(binom_result.pvalue)
            stat = float((abs(b - c) - 1.0) ** 2 / discordant_total) if discordant_total > 0 else 0.0
            test_type = "exact_binomial"
        else:
            # Chi-square with Edwards continuity correction
            stat = float(((abs(b - c) - 1.0) ** 2) / discordant_total)
            p_val = float(1.0 - stats.chi2.cdf(stat, df=1))
            test_type = "continuity_corrected_chi2"

        is_significant = p_val < self.alpha
        if is_significant:
            if c > b:
                interp = f"Candidate model is significantly superior (p={p_val:.4f}, c={c} vs b={b})."
            else:
                interp = f"Baseline model is significantly superior (p={p_val:.4f}, b={b} vs c={c})."
        else:
            interp = f"No statistically significant difference in classification accuracy (p={p_val:.4f})."

        return {
            "contingency_matrix": contingency_matrix,
            "both_correct_count": a,
            "baseline_only_correct_count": b,
            "candidate_only_correct_count": c,
            "both_wrong_count": d,
            "statistic": round(stat, 4),
            "p_value": round(p_val, 4),
            "test_type": test_type,
            "is_significant": is_significant,
            "interpretation": interp,
        }
