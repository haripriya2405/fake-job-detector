"""Test Suite for 12-Factor Model Promotion Gate and Safe Model Governance."""

import pytest
from app.ml.promotion_gate import ModelPromotionGate, PromotionGateEvaluationResult
from app.ml.registry import ModelRegistry, ModelVersionMetadata, model_registry


@pytest.fixture
def gate():
    return ModelPromotionGate(registry=model_registry)


def test_12_factor_gate_structure(gate):
    """Verify all 12 qualification factors are present in the evaluation output."""
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
        latency_p95_ms=32.5,
        explainability_verified=True,
    )

    assert isinstance(res, PromotionGateEvaluationResult)
    assert len(res.gate_checks) == 12
    assert "Gate 9: PR-AUC Superiority" in "".join(res.gate_checks.keys())
    assert "Gate 10: Multi-pattern Adversarial Robustness" in "".join(res.gate_checks.keys())
    assert "Gate 11: CPU Inference Latency Constraint" in "".join(res.gate_checks.keys())
    assert "Gate 12: Token & Span Explainability Quality" in "".join(res.gate_checks.keys())


def test_gate_blocks_candidate_with_high_fpr(gate):
    """Verify gate fails if candidate false positive rate exceeds 0.05."""
    cand_metrics = {
        "f1_score": 0.92,
        "recall": 0.96,
        "false_positive_rate": 0.08,  # Exceeds 0.05
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

    assert res.all_gates_passed is False
    assert res.should_promote is False
    assert res.active_model_retained == "logisticregression-v1.0.0"


def test_gate_blocks_candidate_with_slow_cpu_latency(gate):
    """Verify gate fails if candidate CPU p95 latency exceeds 50ms."""
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
        latency_p95_ms=95.0,  # Fails 50ms cap
    )

    assert res.all_gates_passed is False
    assert res.should_promote is False


def test_registry_rollback_capability(gate):
    """Verify rollback explicitly restores baseline model as active."""
    gate.rollback_to_baseline("logisticregression-v1.0.0")
    active = model_registry.get_active_model_version()
    assert active is not None
    assert active.model_version == "logisticregression-v1.0.0"
