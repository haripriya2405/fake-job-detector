"""Test Suite for Statistical Significance and Paired Hypothesis Testing (Phase 20)."""

import numpy as np
import pytest
from app.ml.statistical_tests import StatisticalComparator


@pytest.fixture
def stat_comparator():
    return StatisticalComparator(n_bootstraps=200, random_state=42)


def test_bootstrap_ci_computation(stat_comparator):
    """Verify bootstrap CI generates valid bounds containing the point estimate."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.15, 0.3, 0.85, 0.9, 0.75, 0.95])

    f1_ci = stat_comparator.compute_metric_bootstrap_ci(y_true, y_prob, "f1")
    assert "point_estimate" in f1_ci
    assert "ci_lower" in f1_ci
    assert "ci_upper" in f1_ci
    assert f1_ci["ci_lower"] <= f1_ci["point_estimate"] <= f1_ci["ci_upper"]


def test_mcnemar_test_identical_predictions(stat_comparator):
    """Verify McNemar test returns p=1.0 for identical prediction vectors."""
    y_true = np.array([0, 1, 0, 1, 0])
    base_pred = np.array([0, 1, 0, 1, 0])
    cand_pred = np.array([0, 1, 0, 1, 0])

    res = stat_comparator.perform_mcnemar_test(y_true, base_pred, cand_pred)
    assert res["p_value"] == 1.0
    assert res["is_significant"] is False
    assert res["both_correct_count"] == 5
    assert res["baseline_only_correct_count"] == 0
    assert res["candidate_only_correct_count"] == 0


def test_mcnemar_test_discordant_pairs(stat_comparator):
    """Verify McNemar test detects discordant pairs and computes exact/chi2 p-value."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    base_pred = np.array([0, 0, 1, 1, 1, 1, 0, 0])  # 4 correct
    cand_pred = np.array([0, 0, 0, 0, 1, 1, 1, 1])  # 8 correct

    res = stat_comparator.perform_mcnemar_test(y_true, base_pred, cand_pred)
    assert res["candidate_only_correct_count"] == 4
    assert res["baseline_only_correct_count"] == 0
    assert 0.0 <= res["p_value"] <= 1.0


def test_paired_metric_difference_computation(stat_comparator):
    """Verify paired difference outputs difference point estimate and 95% CI."""
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    base_prob = np.array([0.4, 0.4, 0.4, 0.4, 0.6, 0.6, 0.6, 0.6])
    cand_prob = np.array([0.1, 0.1, 0.1, 0.1, 0.9, 0.9, 0.9, 0.9])

    diff_res = stat_comparator.compute_paired_metric_difference(y_true, base_prob, cand_prob, "pr_auc")
    assert "absolute_difference" in diff_res
    assert "relative_difference" in diff_res
    assert "difference_95_ci" in diff_res
    assert len(diff_res["difference_95_ci"]) == 2
