"""Phase 7C Statistical Strengthening & Evaluation Test Suite.
Tests:
1. 5-Fold Stratified Cross-Validation on development data
2. Non-parametric bootstrap confidence interval estimation (95% CI)
3. Statistical adequacy vs underpowered sample size flagging
4. Cost-sensitive validation threshold grid search & single-pass holdout evaluation
5. Promotion gate rejection under underpowered sample size and sub-95% recall
6. Model registry rollback and active baseline retention
"""

import pytest
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.ml.production_dataset import ProductionDatasetIngestion
from app.ml.promotion_gate import ModelPromotionGate, PromotionGateEvaluationResult
from app.ml.registry import ModelRegistry, ModelVersionMetadata, model_registry
from app.ml.statistics import ModelStatisticsEvaluator
from app.ml.thresholds import ThresholdAnalyzer


# -----------------------------------------------------------------------------
# 1. Stratified Cross-Validation
# -----------------------------------------------------------------------------
def test_stratified_cross_validation():
    """Verify 5-fold cross-validation computes mean and std for all key metrics."""
    evaluator = ModelStatisticsEvaluator(random_state=42)
    ingestion = ProductionDatasetIngestion()
    df, _ = ingestion.ingest_and_clean()

    def dummy_builder():
        return Pipeline([
            ("tfidf", TfidfVectorizer(max_features=500)),
            ("clf", LogisticRegression(max_iter=200)),
        ])

    cv_results = evaluator.compute_stratified_cv(
        dummy_builder,
        df["raw_text"].tolist(),
        df["label"].values,
        n_splits=5,
    )

    assert "accuracy" in cv_results
    assert "f1_score" in cv_results
    assert "recall" in cv_results
    assert "precision" in cv_results
    assert "roc_auc" in cv_results
    assert cv_results["k_folds"] == 5
    assert 0.0 <= cv_results["f1_score"]["mean"] <= 1.0
    assert cv_results["f1_score"]["std"] >= 0.0


# -----------------------------------------------------------------------------
# 2. Bootstrap Confidence Intervals
# -----------------------------------------------------------------------------
def test_bootstrap_confidence_intervals():
    """Verify bootstrap confidence intervals calculate point estimates and 95% CI bounds."""
    evaluator = ModelStatisticsEvaluator(n_bootstrap=200, random_state=42)

    y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 1, 0])
    y_pred = np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 0])
    y_prob = np.array([0.9, 0.8, 0.85, 0.4, 0.1, 0.2, 0.6, 0.15, 0.95, 0.05])

    ci_results = evaluator.compute_bootstrap_confidence_intervals(y_true, y_pred, y_prob)

    assert "f1_score" in ci_results
    assert "recall" in ci_results
    assert "precision" in ci_results
    assert "false_positive_rate" in ci_results
    assert "roc_auc" in ci_results

    f1_ci = ci_results["f1_score"]
    assert f1_ci["confidence_level"] == "95%"
    assert f1_ci["ci_lower"] <= f1_ci["point_estimate"] <= f1_ci["ci_upper"]
    assert f1_ci["ci_width"] >= 0.0


# -----------------------------------------------------------------------------
# 3. Statistical Adequacy & Power Assessment
# -----------------------------------------------------------------------------
def test_statistical_adequacy_power_assessment():
    """Verify statistical adequacy flags small holdout sets as underpowered."""
    evaluator = ModelStatisticsEvaluator()

    # Small holdout N=11
    small_assessment = evaluator.assess_statistical_adequacy(holdout_size=11, fraud_count=5, legit_count=6)
    assert small_assessment["is_adequately_powered"] is False
    assert small_assessment["status"] == "UNDERPOWERED (Sample Size Limited)"
    assert small_assessment["estimated_margin_of_error"] > 0.20

    # Adequately powered holdout N=400
    large_assessment = evaluator.assess_statistical_adequacy(holdout_size=400, fraud_count=200, legit_count=200)
    assert large_assessment["is_adequately_powered"] is True
    assert large_assessment["status"] == "ADEQUATE"
    assert large_assessment["estimated_margin_of_error"] <= 0.05


# -----------------------------------------------------------------------------
# 4. Validation Threshold Search & Holdout Evaluation
# -----------------------------------------------------------------------------
def test_validation_threshold_tuning():
    """Verify threshold analyzer finds optimal threshold on validation and evaluates once on holdout."""
    analyzer = ThresholdAnalyzer(fn_cost_weight=10.0, fp_cost_weight=1.0)

    y_val = np.array([1, 1, 0, 0, 1, 0])
    y_val_prob = np.array([0.85, 0.45, 0.20, 0.10, 0.90, 0.35])

    grid_res = analyzer.evaluate_threshold_grid(y_val, y_val_prob)
    assert "validation_grid" in grid_res
    assert len(grid_res["validation_grid"]) == 5
    assert grid_res["optimal_threshold"] in [0.30, 0.40, 0.50, 0.60, 0.70]

    y_holdout = np.array([1, 0, 1, 0])
    y_holdout_prob = np.array([0.80, 0.15, 0.75, 0.25])
    holdout_eval = analyzer.evaluate_on_holdout(y_holdout, y_holdout_prob, selected_threshold=grid_res["optimal_threshold"])
    assert "decision_loss" in holdout_eval
    assert holdout_eval["precision"] >= 0.0


# -----------------------------------------------------------------------------
# 5. Promotion Gate Underpowered & Sub-Target Rejection
# -----------------------------------------------------------------------------
def test_promotion_gate_underpowered_rejection():
    """Verify promotion gate explicitly rejects promotion when holdout is underpowered or recall < 0.95."""
    gate = ModelPromotionGate(registry=model_registry)

    cand_metrics = {
        "accuracy": 0.8182,
        "precision": 0.8000,
        "recall": 0.8000,
        "f1_score": 0.8000,
        "roc_auc": 0.9333,
        "false_positive_rate": 0.1667,
        "brier_score": 0.1409,
        "expected_calibration_error": 0.1681,
    }
    base_metrics = {
        "accuracy": 0.8182,
        "precision": 0.8000,
        "recall": 0.8000,
        "f1_score": 0.8000,
        "roc_auc": 0.9333,
        "false_positive_rate": 0.1667,
        "brier_score": 0.1917,
        "expected_calibration_error": 0.1697,
    }

    result = gate.evaluate_promotion(
        candidate_name="model-v2.0.0",
        baseline_name="logisticregression-v1.0.0",
        candidate_holdout_metrics=cand_metrics,
        baseline_holdout_metrics=base_metrics,
        holdout_size=11,
        fraud_count=5,
        legit_count=6,
    )

    assert result.should_promote is False
    assert result.all_gates_passed is False
    assert result.active_model_retained == "logisticregression-v1.0.0"
    assert result.statistical_power_assessment["status"] == "UNDERPOWERED (Sample Size Limited)"
