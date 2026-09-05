"""Test Suite for Model Comparative Benchmarking Engine (Phase 20)."""

import pandas as pd
import pytest
from app.ml.model_comparator import ModelComparator
from app.ml.predictor import MLPredictor


@pytest.fixture
def sample_holdout_df():
    return pd.DataFrame([
        {
            "record_id": "H-001",
            "text": "Senior Backend Developer: 5+ years experience in Python, FastAPI, and Kubernetes. Competitive salary, health benefits.",
            "label": 0,
        },
        {
            "record_id": "H-002",
            "text": "Data Entry Typist: Immediate home start. Send $150 refundable screening registration deposit via Zelle.",
            "label": 1,
        },
        {
            "record_id": "H-003",
            "text": "Congratulations on selection! We mail advance cashier check of $4,000. Deposit and transfer remainder to vendor.",
            "label": 1,
        },
        {
            "record_id": "H-004",
            "text": "Customer Support Representative: Inbound phone support, handle user accounts, 401(k) match. Apply via official site.",
            "label": 0,
        },
    ])


def test_model_comparator_evaluates_both_models(sample_holdout_df):
    """Verify comparator generates complete metrics and deltas for both models."""
    comparator = ModelComparator()
    results = comparator.compare_models(sample_holdout_df)

    assert "baseline" in results
    assert "candidate" in results
    assert "delta_metrics" in results
    assert "statistical_significance" in results

    base_m = results["baseline"]["metrics"]
    cand_m = results["candidate"]["metrics"]

    assert "f1_score" in base_m
    assert "pr_auc" in base_m
    assert "roc_auc" in base_m
    assert "brier_score" in base_m
    assert "expected_calibration_error" in base_m

    assert "f1_score" in cand_m
    assert "pr_auc" in cand_m

    # Delta sanity check
    assert "f1_score" in results["delta_metrics"]
    expected_delta_f1 = round(cand_m["f1_score"] - base_m["f1_score"], 4)
    assert results["delta_metrics"]["f1_score"] == expected_delta_f1


def test_model_comparator_confusion_matrix_structure(sample_holdout_df):
    """Verify confusion matrix returns valid integer counts."""
    comparator = ModelComparator()
    results = comparator.compare_models(sample_holdout_df)

    cm = results["baseline"]["confusion_matrix"]
    assert all(k in cm for k in ["tp", "tn", "fp", "fn"])
    assert sum(cm.values()) == len(sample_holdout_df)
