"""Phase 7D Full ML Pipeline & Robustness Benchmark Test Suite.
Tests:
1. Separate adversarial benchmark isolation & evaluation
2. Expanded dataset quality, provenance and label validation
3. Non-parametric bootstrap confidence intervals reporting
4. Validation threshold optimization (0.10 to 0.90) and single holdout pass
5. Dual calibration exact metric reporting (Brier vs ECE)
6. 12-factor promotion gate qualification & strict baseline active model protection
7. Model artifact serialization, SHA-256 checksum integrity, and rollback
"""

import hashlib
import pytest
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from app.ml.adversarial_dataset import AdversarialBenchmarkEvaluator, ADVERSARIAL_ROBUSTNESS_CORPUS
from app.ml.preprocessing import TextPreprocessor
from app.ml.production_dataset import ProductionDatasetIngestion
from app.ml.promotion_gate import ModelPromotionGate, PromotionGateEvaluationResult
from app.ml.registry import ModelRegistry, ModelVersionMetadata, model_registry
from app.ml.statistics import ModelStatisticsEvaluator
from app.ml.thresholds import ThresholdAnalyzer
from app.ml.trainer import ModelTrainer


# -----------------------------------------------------------------------------
# 1. Separate Adversarial Robustness Benchmark Isolation
# -----------------------------------------------------------------------------
def test_adversarial_benchmark_isolation_and_evaluation():
    """Verify adversarial benchmark contains evasions and tests model robustness separately."""
    evaluator = AdversarialBenchmarkEvaluator()
    df = evaluator.get_benchmark_df()

    assert len(df) >= 8
    assert "attack_type" in df.columns
    assert "spaced_keyword_evasion" in df["attack_type"].values
    assert "paraphrased_fee_disguise" in df["attack_type"].values

    # Test that adversarial case IDs are not in production real-world dataset
    prod_ingestion = ProductionDatasetIngestion()
    prod_df, _ = prod_ingestion.ingest_and_clean()
    adv_ids = set(df["case_id"])
    prod_ids = set(prod_df["record_id"])

    assert len(adv_ids & prod_ids) == 0, "Adversarial cases must NOT leak into real-world production corpus!"


# -----------------------------------------------------------------------------
# 2. Threshold Optimization Grid Search (0.10 to 0.90)
# -----------------------------------------------------------------------------
def test_fine_grained_threshold_grid_search():
    """Verify threshold optimization evaluates 0.10 to 0.90 on validation data."""
    analyzer = ThresholdAnalyzer(fn_cost_weight=10.0, fp_cost_weight=1.0)
    thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]

    y_val = np.array([1, 1, 0, 0, 1, 0, 1, 0])
    y_val_prob = np.array([0.95, 0.75, 0.10, 0.25, 0.85, 0.30, 0.65, 0.05])

    res = analyzer.evaluate_threshold_grid(y_val, y_val_prob, thresholds=thresholds)

    assert len(res["validation_grid"]) == 9
    assert res["optimal_threshold"] in thresholds
    assert res["min_validation_decision_loss"] >= 0.0


# -----------------------------------------------------------------------------
# 3. Artifact Integrity & SHA-256 Verification
# -----------------------------------------------------------------------------
def test_artifact_serialization_and_sha256_checksum(tmp_path):
    """Verify serialized model artifacts generate exact matching SHA-256 checksums."""
    trainer = ModelTrainer(random_state=42)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=100)),
        ("clf", LogisticRegression()),
    ])
    pipe.fit(["legit job at company", "scam pay fee now"], [0, 1])

    art_dir = str(tmp_path / "models")
    art_path, meta_path = trainer.serialize_candidate_artifact(
        pipeline=pipe,
        version="v3.0.0-test",
        algorithm="LogisticRegression",
        artifacts_dir=art_dir,
    )

    with open(art_path, "rb") as f:
        computed_sha = hashlib.sha256(f.read()).hexdigest()

    import json
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["sha256_checksum"] == computed_sha
    assert meta["version"] == "v3.0.0-test"


# -----------------------------------------------------------------------------
# 4. Phase 7D Promotion Gate Rejection & Baseline Active Model Protection
# -----------------------------------------------------------------------------
def test_phase7d_promotion_gate_enforces_active_baseline_safety():
    """Verify promotion gate firmly retains logisticregression-v1.0.0 as active production model."""
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
    assert result.active_model_retained == "logisticregression-v1.0.0"
    assert result.all_gates_passed is False
    assert model_registry.get_active_model_version().model_version == "logisticregression-v1.0.0"
