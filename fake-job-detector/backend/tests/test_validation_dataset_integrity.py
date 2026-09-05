"""Test Suite for Validation Dataset Integrity and Provenance Compliance (Phase 20)."""

import pandas as pd
import pytest
from app.ml.real_world_validation import RealWorldValidationPipeline


@pytest.fixture
def dataset_partitions():
    pipeline = RealWorldValidationPipeline()
    records, stats = pipeline.validate_and_ingest()
    return pipeline.create_leakage_free_partitions(records, val_ratio=0.20, holdout_ratio=0.20), stats


def test_dataset_integrity_non_empty(dataset_partitions):
    """Verify all dataset partitions contain valid non-empty rows."""
    partitions, stats = dataset_partitions
    for split_name in ["train", "validation", "holdout"]:
        df = partitions[split_name]
        assert len(df) > 0
        assert not df["text"].isnull().any()
        assert not df["label"].isnull().any()
        assert df["label"].isin([0, 1]).all()


def test_dataset_provenance_fields_present(dataset_partitions):
    """Verify mandatory provenance fields are present on every ingested record."""
    partitions, _ = dataset_partitions
    holdout_df = partitions["holdout"]
    required_cols = ["record_id", "text", "source", "collection_date", "label", "category", "content_hash", "license"]
    for col in required_cols:
        assert col in holdout_df.columns, f"Missing required column: {col}"


def test_content_hashes_unique_across_splits(dataset_partitions):
    """Verify strict partition boundary integrity with zero content hash overlap."""
    partitions, _ = dataset_partitions
    train_hashes = set(partitions["train"]["content_hash"])
    val_hashes = set(partitions["validation"]["content_hash"])
    holdout_hashes = set(partitions["holdout"]["content_hash"])

    assert len(train_hashes.intersection(val_hashes)) == 0
    assert len(train_hashes.intersection(holdout_hashes)) == 0
    assert len(val_hashes.intersection(holdout_hashes)) == 0
