from datetime import datetime, timezone
import statistics
from typing import Any, Dict, List, Optional
import numpy as np

from app.ml.calibration import ModelCalibrator
from app.ml.engine import analysis_engine
from app.rules.engine import rule_engine
from app.rules.risk import risk_engine
from app.verification.service import verification_service
from evaluation.golden_dataset import GOLDEN_TEST_CASES, GoldenTestCase


class SystemEvaluationHarness:
    """Automated Evaluation & Risk Calibration Harness for SentinelJob AI (Phase 6).
    Evaluates multi-factor performance, statistical calibration, adversarial resilience,
    and scoring weight balance across golden benchmark cohorts.
    """

    def __init__(self, test_cases: Optional[List[GoldenTestCase]] = None):
        self.test_cases = test_cases or GOLDEN_TEST_CASES
        self.calibrator = ModelCalibrator()

    def run_full_evaluation(self) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []

        y_true: List[int] = []
        y_pred: List[int] = []
        y_prob: List[float] = []
        risk_scores: List[int] = []

        cohort_scores: Dict[str, List[int]] = {}
        tier_counts: Dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        false_positives: List[Dict[str, Any]] = []
        false_negatives: List[Dict[str, Any]] = []
        explainability_violations: List[str] = []

        for case in self.test_cases:
            # 1. Run ML Engine
            ml_res = analysis_engine.analyze_text(
                case.text,
                metadata={"job_title": case.title, "company_name": case.company_name},
            )

            # 2. Run Rule Engine
            rule_res = rule_engine.evaluate(
                case.text,
                metadata={"job_title": case.title, "company_name": case.company_name},
            )

            # 3. Run Verification Engine
            ver_res = verification_service.verify_job_posting(
                text=case.text,
                claimed_company=case.company_name,
                job_title=case.title,
            )

            # 4. Synthesize Multi-Factor Risk
            risk_res = risk_engine.synthesize(
                ml_result=ml_res,
                rule_result=rule_res,
                verification_result=ver_res,
            )

            score = risk_res.final_score
            tier = risk_res.risk_level
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

            # Classification: Threshold at Score >= 50 for binary threat detection
            predicted_class = 1 if score >= 50 else 0
            predicted_prob = score / 100.0

            y_true.append(case.expected_ground_truth)
            y_pred.append(predicted_class)
            y_prob.append(predicted_prob)
            risk_scores.append(score)

            if case.cohort not in cohort_scores:
                cohort_scores[case.cohort] = []
            cohort_scores[case.cohort].append(score)

            # Explainability verification
            if tier in ["high", "critical"] and len(risk_res.triggered_indicators) == 0 and not ver_res.signals:
                explainability_violations.append(case.id)

            # False Positives / Negatives tracking
            if case.expected_ground_truth == 0 and predicted_class == 1:
                false_positives.append({
                    "id": case.id,
                    "title": case.title,
                    "score": score,
                    "tier": tier,
                    "explanation": risk_res.explanation,
                })
            elif case.expected_ground_truth == 1 and predicted_class == 0:
                false_negatives.append({
                    "id": case.id,
                    "title": case.title,
                    "score": score,
                    "tier": tier,
                    "explanation": risk_res.explanation,
                })

            results.append({
                "id": case.id,
                "cohort": case.cohort,
                "title": case.title,
                "ground_truth": case.expected_ground_truth,
                "predicted_class": predicted_class,
                "score": score,
                "risk_tier": tier,
                "ml_score": risk_res.score_breakdown.ml_contribution,
                "rule_score": risk_res.score_breakdown.rule_contribution,
                "domain_score": risk_res.score_breakdown.domain_penalty,
                "indicators_count": len(risk_res.triggered_indicators),
                "recommendations_count": len(risk_res.recommendations),
            })

        # Compute Statistical Metrics
        y_true_arr = np.array(y_true)
        y_pred_arr = np.array(y_pred)
        y_prob_arr = np.array(y_prob)

        tp = int(np.sum((y_true_arr == 1) & (y_pred_arr == 1)))
        tn = int(np.sum((y_true_arr == 0) & (y_pred_arr == 0)))
        fp = int(np.sum((y_true_arr == 0) & (y_pred_arr == 1)))
        fn = int(np.sum((y_true_arr == 1) & (y_pred_arr == 0)))

        accuracy = (tp + tn) / len(y_true) if len(y_true) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        # Calibration evaluation
        calibration = self.calibrator.evaluate_calibration(
            y_true=y_true_arr,
            y_prob=y_prob_arr,
            n_bins=5,
        )

        # Cohort summary statistics
        cohort_summary = {}
        for cohort, scores in cohort_scores.items():
            cohort_summary[cohort] = {
                "count": len(scores),
                "mean_score": round(statistics.mean(scores), 2),
                "min_score": min(scores),
                "max_score": max(scores),
                "std_dev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0.0,
            }

        return {
            "total_cases": len(self.test_cases),
            "confusion_matrix": {"TP": tp, "TN": tn, "FP": fp, "FN": fn},
            "metrics": {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "false_positive_rate": round(fpr, 4),
                "false_negative_rate": round(fnr, 4),
            },
            "tier_distribution": tier_counts,
            "cohort_summary": cohort_summary,
            "calibration": calibration,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "explainability_violations": explainability_violations,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "raw_case_results": results,
        }
