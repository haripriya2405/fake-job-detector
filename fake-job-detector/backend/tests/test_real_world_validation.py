"""Test Suite for Real-World Dataset Validation Pipeline (Phase 20).
Tests:
- Provenance attachment and schema adherence
- Rejection of malformed / empty records
- Content-hash deduplication
- Zero-leakage partitioning between Train, Validation, and Holdout
- Statistical sample power adequacy assessment
"""

import pandas as pd
import pytest
from app.ml.real_world_validation import RealWorldRecord, RealWorldValidationPipeline


def test_real_world_record_validation():
    """Verify RealWorldRecord requires mandatory provenance metadata."""
    rec = RealWorldRecord(
        record_id="RW-0001",
        text="Valid legitimate engineering job with salary and 401(k) retirement benefits.",
        source="verified_corporate_board",
        source_url="https://jobs.example.com/posting/123",
        collection_date="2026-08-19",
        label=0,
        category="tech_enterprise",
        content_hash="abc123hash",
        license="CC-BY-4.0",
    )
    assert rec.record_id == "RW-0001"
    assert rec.label == 0
    assert rec.license == "CC-BY-4.0"


def test_pipeline_rejection_of_empty_and_short_records():
    """Verify pipeline rejects empty or very short strings."""
    raw_data = [
        {"text": "Too short", "label": 1},
        {"text": "", "label": 0},
        {"text": "   \n\t  ", "label": 1},
        {"text": "Valid software engineering job description with complete requirements and benefit packages.", "label": 0},
    ]
    pipeline = RealWorldValidationPipeline(raw_data=raw_data)
    valid_records, stats = pipeline.validate_and_ingest()

    assert len(valid_records) == 1
    assert stats["rejected_records_count"] == 3


def test_pipeline_content_hash_deduplication():
    """Verify duplicate text records are cleanly deduplicated."""
    raw_data = [
        {"text": "Identical posting text for customer support role.", "label": 0},
        {"text": "Identical posting text for customer support role.   ", "label": 0},
        {"text": "Distinct posting text for security analyst position.", "label": 0},
    ]
    pipeline = RealWorldValidationPipeline(raw_data=raw_data)
    valid_records, stats = pipeline.validate_and_ingest()

    assert len(valid_records) == 2
    assert stats["rejected_records_count"] == 1


def test_leakage_free_partitions_isolation():
    """Verify zero overlap in content hashes across Train, Val, and Holdout."""
    pipeline = RealWorldValidationPipeline()
    records, stats = pipeline.validate_and_ingest()
    partitions = pipeline.create_leakage_free_partitions(records, val_ratio=0.20, holdout_ratio=0.20)

    train_df = partitions["train"]
    val_df = partitions["validation"]
    holdout_df = partitions["holdout"]

    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(holdout_df) > 0

    train_h = set(train_df["content_hash"])
    val_h = set(val_df["content_hash"])
    holdout_h = set(holdout_df["content_hash"])

    assert len(train_h & val_h) == 0
    assert len(train_h & holdout_h) == 0
    assert len(val_h & holdout_h) == 0


def test_sample_power_assessment_adequacy():
    """Verify power assessment flags small sample sizes honestly."""
    pipeline = RealWorldValidationPipeline()

    # Small sample N=20
    small_power = pipeline.assess_sample_power(20)
    assert small_power["is_adequately_powered"] is False
    assert small_power["status"] == "INSUFFICIENT_STATISTICAL_EVIDENCE"

    # Adequate sample N=400
    large_power = pipeline.assess_sample_power(400)
    assert large_power["is_adequately_powered"] is True
    assert large_power["status"] == "SUFFICIENT_STATISTICAL_EVIDENCE"
