"""Test Suite for Phase 20 12-Factor Promotion Gate and Governance Verdicts."""

import pytest
from app.ml.promotion_gate import ModelPromotionGate, PromotionGateEvaluationResult
from app.ml.registry import ModelRegistry, model_registry


@pytest.fixture
def gate():
    return ModelPromotionGate(registry=model_registry)


def test_gate_returns_insufficient_evidence_for_small_holdout(gate):
    """Verify gate returns INSUFFICIENT_EVIDENCE when sample size is below statistical power adequacy."""
    cand_metrics = {
        "f1_score": 0.98,
        "recall": 0.98,
        "false_positive_rate": 0.01,
        "roc_auc": 0.99,
        "pr_auc": 0.99,
        "brier_score": 0.02,
        "expected_calibration_error": 0.03,
    }
    baseline_metrics = {
        "f1_score": 0.85,
        "recall": 0.88,
        "false_positive_rate": 0.06,
        "roc_auc": 0.90,
        "pr_auc": 0.88,
        "brier_score": 0.08,
        "expected_calibration_error": 0.07,
    }

    res = gate.evaluate_promotion(
        candidate_name="transformer-v1.0.0-candidate",
        baseline_name="logisticregression-v1.0.0",
        candidate_holdout_metrics=cand_metrics,
        baseline_holdout_metrics=baseline_metrics,
        holdout_size=25,  # Below N=384
        fraud_count=10,
        legit_count=15,
        golden_regression_passed=True,
        provenance_documented=True,
        adversarial_accuracy=0.96,
        latency_p95_ms=30.0,
        explainability_verified=True,
    )

    assert isinstance(res, PromotionGateEvaluationResult)
    assert res.verdict == "INSUFFICIENT_EVIDENCE"
    assert res.eligible_for_promotion is False
    assert res.active_model_unchanged is True
    assert res.active_model_retained == "logisticregression-v1.0.0"


def test_gate_returns_fail_on_high_false_positive_rate(gate):
    """Verify gate returns FAIL when a safety criterion like FPR exceeds limit."""
    cand_metrics = {
        "f1_score": 0.92,
        "recall": 0.96,
        "false_positive_rate": 0.12,  # Exceeds 0.05
        "roc_auc": 0.95,
        "pr_auc": 0.95,
        "brier_score": 0.04,
        "expected_calibration_error": 0.04,
    }
    baseline_metrics = {
        "f1_score": 0.85,
        "brier_score": 0.08,
        "expected_calibration_error": 0.07,
    }

    res = gate.evaluate_promotion(
        candidate_name="transformer-v1.0.0-candidate",
        baseline_name="logisticregression-v1.0.0",
        candidate_holdout_metrics=cand_metrics,
        baseline_holdout_metrics=baseline_metrics,
        holdout_size=400,
        fraud_count=180,
        legit_count=220,
    )

    assert res.verdict == "FAIL"
    assert res.eligible_for_promotion is False
    assert res.active_model_retained == "logisticregression-v1.0.0"


def test_gate_returns_pass_and_eligible_when_fully_powered_and_qualified(gate):
    """Verify gate returns PASS and marks candidate eligible when all 12 criteria pass with N >= 384."""
    cand_metrics = {
        "f1_score": 0.98,
        "recall": 0.98,
        "false_positive_rate": 0.01,
        "roc_auc": 0.99,
        "pr_auc": 0.99,
        "brier_score": 0.02,
        "expected_calibration_error": 0.03,
    }
    baseline_metrics = {
        "f1_score": 0.85,
        "recall": 0.88,
        "false_positive_rate": 0.06,
        "roc_auc": 0.90,
        "pr_auc": 0.88,
        "brier_score": 0.08,
        "expected_calibration_error": 0.07,
    }

    res = gate.evaluate_promotion(
        candidate_name="transformer-v1.0.0-candidate",
        baseline_name="logisticregression-v1.0.0",
        candidate_holdout_metrics=cand_metrics,
        baseline_holdout_metrics=baseline_metrics,
        holdout_size=400,
        fraud_count=180,
        legit_count=220,
        golden_regression_passed=True,
        provenance_documented=True,
        adversarial_accuracy=0.96,
        latency_p95_ms=32.0,
        explainability_verified=True,
    )

    assert res.verdict == "PASS"
    assert res.eligible_for_promotion is True
    assert res.active_model_unchanged is True
