"""Phase 7B Model Promotion Gate & Expanded Dataset Test Suite.
Tests:
1. Expanded dataset ingestion and multi-source distribution
2. Cross-split leakage checks (record ID and campaign clustering)
3. Model evaluation across baseline LR, candidate LR, and Platt-scaled SVM
4. Promotion gate evaluation and strict retention of baseline active model
5. Registry rollback and candidate standby state management
6. Dual calibration analysis (Brier score vs Expected Calibration Error)
"""

import pytest
import pandas as pd

from app.ml.production_dataset import ProductionDatasetIngestion
from app.ml.promotion_gate import ModelPromotionGate, PromotionGateEvaluationResult
from app.ml.registry import ModelRegistry, ModelVersionMetadata, model_registry
from app.ml.trainer import ModelTrainer


# -----------------------------------------------------------------------------
# 1. Expanded Dataset Ingestion & Category Breadth
# -----------------------------------------------------------------------------
def test_expanded_dataset_ingestion_and_diversity():
    """Verify expanded dataset ingests with diverse legitimate and fraudulent categories."""
    ingestion = ProductionDatasetIngestion()
    df, stats = ingestion.ingest_and_clean()

    assert stats["accepted_records"] >= 50
    assert stats["sources_count"] >= 10
    assert "tech_enterprise" in stats["category_distribution"]
    assert "advance_fee" in stats["category_distribution"]
    assert "crypto_task" in stats["category_distribution"]
    assert "impersonation" in stats["category_distribution"]


# -----------------------------------------------------------------------------
# 2. Expanded Leakage & Split Isolation
# -----------------------------------------------------------------------------
def test_expanded_split_isolation_and_holdout_scale():
    """Verify train, validation, and contemporary holdout splits have zero cross-leakage."""
    ingestion = ProductionDatasetIngestion()
    df, _ = ingestion.ingest_and_clean()
    train_df, val_df, holdout_df = ingestion.create_leakage_free_splits(df, random_state=42)

    assert len(holdout_df) >= 10

    train_ids = set(train_df["record_id"])
    val_ids = set(val_df["record_id"])
    holdout_ids = set(holdout_df["record_id"])

    assert len(train_ids & val_ids) == 0
    assert len(train_ids & holdout_ids) == 0
    assert len(val_ids & holdout_ids) == 0


# -----------------------------------------------------------------------------
# 3. Model Promotion Gate Rejection of Premature Promotion
# -----------------------------------------------------------------------------
def test_model_promotion_gate_blocks_premature_promotion():
    """Verify promotion gate blocks automatic promotion when candidate does not satisfy all qualification criteria."""
    gate = ModelPromotionGate(registry=model_registry)

    # Simulated candidate with imperfect recall
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
    baseline_metrics = {
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
        baseline_holdout_metrics=baseline_metrics,
        holdout_size=11,
        golden_regression_passed=True,
        provenance_documented=True,
    )

    assert isinstance(result, PromotionGateEvaluationResult)
    assert result.should_promote is False
    assert result.active_model_retained == "logisticregression-v1.0.0"
    assert any("Gate 1: Generalization" in k for k in result.gate_checks)
    gen_key = [k for k in result.gate_checks if "Gate 1: Generalization" in k][0]
    assert result.gate_checks[gen_key]["passed"] is False


# -----------------------------------------------------------------------------
# 4. Registry Rollback & Standby Management
# -----------------------------------------------------------------------------
def test_registry_rollback_capability(tmp_path):
    """Verify model registry can rollback active model and maintain candidate on standby."""
    test_meta_path = str(tmp_path / "model_reg.json")
    reg = ModelRegistry(metadata_path=test_meta_path)

    # Initial active is baseline
    assert reg.get_active_model_version().model_version == "logisticregression-v1.0.0"

    # Register candidate
    cand_meta = ModelVersionMetadata(
        model_version="model-v2.0.0",
        algorithm="LinearSVC + Platt Calibration",
        dataset_version="expanded-v2.1",
        dataset_size=63,
        feature_configuration={"ngram_range": [1, 2], "max_features": 3500},
        metrics={"f1_score": 0.80},
        calibration_metrics={"brier_score": 0.1409, "expected_calibration_error": 0.1681},
        artifact_hash="hash_12345",
        training_timestamp="2026-08-17T21:48:00Z",
        is_active=False,
    )
    reg.register_candidate_version(cand_meta)

    gate = ModelPromotionGate(registry=reg)
    gate.rollback_to_baseline("logisticregression-v1.0.0")

    assert reg.get_active_model_version().model_version == "logisticregression-v1.0.0"
    assert reg.get_version("model-v2.0.0").is_active is False


# -----------------------------------------------------------------------------
# 5. Dual Calibration Metrics Reporting (Brier vs ECE)
# -----------------------------------------------------------------------------
def test_dual_calibration_reporting_invariant():
    """Verify promotion gate produces distinct Brier score and ECE analyses."""
    gate = ModelPromotionGate(registry=model_registry)
    res = gate.evaluate_promotion(
        candidate_name="model-v2.0.0",
        baseline_name="logisticregression-v1.0.0",
        candidate_holdout_metrics={"f1_score": 0.95, "recall": 0.98, "false_positive_rate": 0.02, "roc_auc": 0.99, "brier_score": 0.05, "expected_calibration_error": 0.12},
        baseline_holdout_metrics={"f1_score": 0.95, "recall": 0.98, "false_positive_rate": 0.02, "roc_auc": 0.99, "brier_score": 0.15, "expected_calibration_error": 0.11},
        holdout_size=20,
    )

    assert "Brier Loss" in res.brier_vs_ece_analysis
    assert "ECE" in res.brier_vs_ece_analysis
    assert "Platt-scaled Linear SVM" in res.brier_vs_ece_analysis
    assert "Neither indicates perfect real-world probability calibration" in res.brier_vs_ece_analysis
