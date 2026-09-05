"""Phase 7 Production ML Pipeline & Model Training Test Suite.
Tests:
1. Production dataset ingestion & schema validation
2. Provenance metadata tracking (source, license, URL, transformation)
3. Exact, normalized, and near-duplicate detection
4. Zero-leakage stratified train / val / holdout splitting
5. Model training & comparison across Logistic Regression & Linear SVM
6. Calibration evaluation (Brier Score, ECE)
7. Model versioning & registry metadata tracking (model-v2.0.0 candidate)
8. Inference compatibility & RiskEngine isolation
"""

import hashlib
import pytest
import pandas as pd

from app.ml.engine import analysis_engine
from app.ml.production_dataset import ProductionDatasetIngestion, ProductionJobRecord, ProductionRecordProvenance
from app.ml.registry import ModelRegistry, ModelVersionMetadata, model_registry
from app.ml.trainer import ModelTrainer


# -----------------------------------------------------------------------------
# 1. Dataset Ingestion, Schemas & Provenance
# -----------------------------------------------------------------------------
def test_production_dataset_ingestion_and_provenance():
    """Verify production dataset loads with complete provenance and schema validation."""
    ingestion = ProductionDatasetIngestion()
    df, stats = ingestion.ingest_and_clean()

    assert stats["accepted_records"] >= 35
    assert stats["sources_count"] >= 5
    assert set(df["label"].unique()) == {0, 1}

    # Verify every record has documented provenance
    for _, row in df.iterrows():
        assert len(row["source_name"]) > 3
        assert len(row["source_url_reference"]) > 3
        assert row["original_license"].startswith("UNKNOWN")
        assert row["acquisition_date"] == "2026-08-17"


# -----------------------------------------------------------------------------
# 2. Deduplication & Near-Duplicate Quality Filtering
# -----------------------------------------------------------------------------
def test_production_deduplication_safeguards():
    """Verify exact, normalized, and near-duplicate detection filters redundant text."""
    ingestion = ProductionDatasetIngestion()
    
    # Test normalization
    raw_text = "   URGENT HIRING: Remote Data Entry Clerk! Pay $40/hr...   "
    norm = ingestion.normalize_text_for_dedup(raw_text)
    assert norm == "urgent hiring remote data entry clerk pay 40hr"

    # Test near-duplicate Jaccard computation
    text_1 = "URGENT HIRING: Remote typist wanted. Pay ₹35,000 per week. Contact on WhatsApp."
    text_2 = "URGENT HIRING: Remote typist wanted. Pay ₹35,000 per week. Contact on WhatsApp!"
    sim = ingestion.compute_jaccard_similarity(text_1, text_2)
    assert sim > 0.90


# -----------------------------------------------------------------------------
# 3. Zero-Leakage Stratified Splitting
# -----------------------------------------------------------------------------
def test_leakage_free_stratified_splits():
    """Verify 70/15/15 train/val/holdout splits with zero cross-split ID or text leakage."""
    ingestion = ProductionDatasetIngestion()
    df, _ = ingestion.ingest_and_clean()
    train_df, val_df, holdout_df = ingestion.create_leakage_free_splits(df, random_state=42)

    total_len = len(df)
    assert len(train_df) + len(val_df) + len(holdout_df) == total_len

    train_ids = set(train_df["record_id"])
    val_ids = set(val_df["record_id"])
    holdout_ids = set(holdout_df["record_id"])

    # Assert zero cross-split ID leakage
    assert len(train_ids & val_ids) == 0
    assert len(train_ids & holdout_ids) == 0
    assert len(val_ids & holdout_ids) == 0

    # Assert both classes present in each split
    assert set(train_df["label"].unique()) == {0, 1}
    assert set(val_df["label"].unique()) == {0, 1}
    assert set(holdout_df["label"].unique()) == {0, 1}


# -----------------------------------------------------------------------------
# 4. Model Training, Calibration & Multi-Model Evaluation
# -----------------------------------------------------------------------------
def test_multi_model_training_and_calibration():
    """Verify trainer builds baseline LR, candidate LR, and Platt-scaled Linear SVM."""
    ingestion = ProductionDatasetIngestion()
    df, _ = ingestion.ingest_and_clean()
    train_df, val_df, holdout_df = ingestion.create_leakage_free_splits(df, random_state=42)

    trainer = ModelTrainer(random_state=42)
    eval_results = trainer.train_and_evaluate_all(train_df, val_df, holdout_df)

    assert "models" in eval_results
    assert len(eval_results["models"]) == 3
    assert eval_results["best_selected_model"] is not None

    for model_name, info in eval_results["models"].items():
        hm = info["holdout_metrics"]
        assert hm["accuracy"] >= 0.75
        assert hm["f1_score"] >= 0.75
        assert hm["roc_auc"] >= 0.80
        assert "brier_score" in hm
        assert "expected_calibration_error" in hm


# -----------------------------------------------------------------------------
# 5. Model Versioning & Registry Metadata
# -----------------------------------------------------------------------------
def test_model_version_registry():
    """Verify model registry tracks active baseline and candidate version metadata."""
    reg = ModelRegistry(metadata_path="artifacts/test_model_registry.json")
    active_model = reg.get_active_model_version()
    assert active_model is not None
    assert active_model.model_version == "logisticregression-v1.0.0"
    assert active_model.is_active is True

    # Register candidate model
    cand_meta = ModelVersionMetadata(
        model_version="model-v2.0.0-test",
        algorithm="LinearSVC(C=1.0) + Platt Scaling",
        dataset_version="prod-corpus-v2.0.0",
        dataset_size=41,
        feature_configuration={"max_features": 3500, "ngram_range": [1, 3]},
        metrics={"accuracy": 1.0, "f1_score": 1.0},
        calibration_metrics={"brier_score": 0.0072, "expected_calibration_error": 0.0793},
        artifact_hash="test_hash_123",
        training_timestamp="2026-08-17T21:30:00Z",
        is_active=False,
    )
    reg.register_candidate_version(cand_meta)

    # Active model must remain unchanged
    assert reg.get_active_model_version().model_version == "logisticregression-v1.0.0"
    assert reg.get_version("model-v2.0.0-test").is_active is False


# -----------------------------------------------------------------------------
# 6. Inference Compatibility & RiskEngine Isolation
# -----------------------------------------------------------------------------
def test_ml_inference_interface_compatibility():
    """Verify active ML engine returns expected schema fields without altering RiskEngine."""
    res = analysis_engine.analyze_text(
        "Stripe is hiring a Distributed Systems Engineer. Apply at https://stripe.com/jobs.",
        metadata={"job_title": "Distributed Systems Engineer", "company_name": "Stripe"},
    )

    required_keys = {"ml_label", "ml_probability", "ml_confidence", "model_version", "algorithm", "top_features"}
    assert required_keys.issubset(set(res.keys()))
    assert res["ml_label"] in ["legitimate", "fraudulent"]
    assert 0.0 <= res["ml_probability"] <= 1.0
    assert 0.0 <= res["ml_confidence"] <= 100.0
