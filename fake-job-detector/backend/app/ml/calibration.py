from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import brier_score_loss


class ModelCalibrator:
    """Evaluates probability calibration quality (Expected Calibration Error,
    Brier Score, and Reliability Curve).
    
    Explicit Note:
    Raw model posterior probabilities output by Logistic Regression or Calibrated SVM
    reflect conditional likelihood on the training distribution, NOT absolute
    real-world fraud probability. Calibration must be evaluated before treating
    probability as an empirical confidence score.
    """

    def evaluate_calibration(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        n_bins: int = 5,
    ) -> Dict[str, Any]:
        """Compute Brier Score, Expected Calibration Error (ECE), and bin reliability."""
        y_true = np.asarray(y_true)
        y_prob = np.asarray(y_prob)

        # 1. Brier Score Loss (lower is better, 0 = perfect)
        brier = float(brier_score_loss(y_true, y_prob))

        # 2. Calibration Curve
        prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")

        # 3. Expected Calibration Error (ECE)
        # Weighted average difference between predicted and empirical accuracy per bin
        bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
        bin_assignments = np.digitize(y_prob, bin_edges) - 1
        bin_assignments = np.clip(bin_assignments, 0, n_bins - 1)

        ece = 0.0
        bin_metrics = []
        total_samples = len(y_true)

        for b in range(n_bins):
            mask = bin_assignments == b
            bin_count = int(np.sum(mask))
            if bin_count > 0:
                bin_acc = float(np.mean(y_true[mask]))
                bin_conf = float(np.mean(y_prob[mask]))
                weight = bin_count / total_samples
                bin_error = abs(bin_acc - bin_conf)
                ece += weight * bin_error
                bin_metrics.append({
                    "bin": b,
                    "count": bin_count,
                    "accuracy": round(bin_acc, 4),
                    "confidence": round(bin_conf, 4),
                    "error": round(bin_error, 4),
                })

        return {
            "brier_score": round(brier, 4),
            "expected_calibration_error": round(float(ece), 4),
            "n_bins": n_bins,
            "prob_true": [round(float(p), 4) for p in prob_true],
            "prob_pred": [round(float(p), 4) for p in prob_pred],
            "bin_metrics": bin_metrics,
            "calibration_status": "evaluated",
            "interpretation_warning": "Raw probability is a statistical model confidence score, not absolute real-world probability.",
        }
