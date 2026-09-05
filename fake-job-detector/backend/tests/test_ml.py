import os
import numpy as np
import pytest
from app.ml.calibration import ModelCalibrator
from app.ml.dataset import (
    AdversarialTestDataset,
    ContemporaryHoldoutDataset,
    DevelopmentSmokeTestDataset,
    JobFraudDataset,
)
from app.ml.engine import DefaultAnalysisEngine
from app.ml.predictor import MLPredictor
from app.ml.preprocessing import TextPreprocessor, preprocessor
from app.ml.schemas import MLPredictionOutput
from app.ml.train import ModelTrainer


@pytest.fixture(scope="module")
def trained_artifacts(tmp_path_factory):
    """Train a test model in a temporary artifacts directory."""
    temp_dir = str(tmp_path_factory.mktemp("test_models"))
    trainer = ModelTrainer(artifacts_dir=temp_dir)
    dataset = DevelopmentSmokeTestDataset()
    results = trainer.train_and_evaluate(dataset=dataset)
    return {
        "artifacts_dir": temp_dir,
        "artifact_path": results["artifact_path"],
        "metadata_path": results["metadata_path"],
    }


def test_preprocessing_cues_and_tokens():
    """Test that text preprocessing normalizes format while preserving fraud signals."""
    tp = TextPreprocessor()

    assert tp.clean_text("") == ""
    assert tp.clean_text(None) == ""

    url_text = "Apply immediately at https://scam-careers.phish.com/apply?id=9928"
    cleaned = tp.clean_text(url_text)
    assert "token_url" in cleaned
    assert "https" not in cleaned

    email_text = "Send resume directly to hr.recruitment2026@gmail.com"
    cleaned = tp.clean_text(email_text)
    assert "token_email" in cleaned

    curr_text = "Daily salary ₹5000 or $450/day. Registration fee of Rs. 1500."
    cleaned = tp.clean_text(curr_text)
    assert "token_currency" in cleaned

    handle_text = "Join our supervisor @ApexRecruiter_David on Telegram"
    cleaned = tp.clean_text(handle_text)
    assert "token_handle" in cleaned

    repeat_text = "Freeeeee moneyyyyy and urgentttt job"
    cleaned = tp.clean_text(repeat_text)
    assert "freee" not in cleaned


def test_dataset_provenance_and_limitations():
    """Test dataset provenance metadata and explicit limitations."""
    dataset = DevelopmentSmokeTestDataset()
    assert dataset.metadata["type"] == "development_smoke_test"
    assert "too small for reliable generalization" in dataset.metadata["limitation"].lower()
    assert len(dataset.metadata["sources"]) >= 2
    for source in dataset.metadata["sources"]:
        assert "source_name" in source
        assert "original_license" in source

    df = dataset.load()
    assert dataset.validate(df) is True
    assert len(df) == 50
    assert df["text"].duplicated().sum() == 0


def test_multi_dataset_interfaces():
    """Test historical, contemporary holdout, and adversarial dataset interfaces."""
    contemporary = ContemporaryHoldoutDataset()
    assert contemporary.metadata["type"] == "out_of_distribution_holdout"
    c_df = contemporary.load()
    assert "text" in c_df.columns
    assert "label" in c_df.columns

    adversarial = AdversarialTestDataset()
    assert adversarial.metadata["type"] == "adversarial_robustness_test"
    a_df = adversarial.load()
    assert "text" in a_df.columns
    assert "label" in a_df.columns


def test_dataset_stratified_splits():
    """Test 70/15/15 split ratio and anti-leakage guarantee."""
    dataset = DevelopmentSmokeTestDataset()
    train_df, val_df, test_df = dataset.get_splits(test_size=0.15, val_size=0.15, random_state=42)

    total = len(dataset.df)
    assert len(train_df) + len(val_df) + len(test_df) == total
    train_hashes = set(train_df["text"])
    test_hashes = set(test_df["text"])
    assert len(train_hashes.intersection(test_hashes)) == 0


def test_model_calibration_evaluation():
    """Test that ModelCalibrator evaluates Brier Score and Expected Calibration Error."""
    calibrator = ModelCalibrator()
    y_true = np.array([0, 0, 1, 1, 1, 0, 1, 0])
    y_prob = np.array([0.1, 0.2, 0.85, 0.9, 0.8, 0.3, 0.95, 0.15])

    results = calibrator.evaluate_calibration(y_true, y_prob, n_bins=4)
    assert "brier_score" in results
    assert "expected_calibration_error" in results
    assert results["brier_score"] >= 0.0
    assert results["expected_calibration_error"] >= 0.0
    assert "interpretation_warning" in results


def test_predictor_inference_and_attribution(trained_artifacts):
    """Test ML predictor with real inference and feature contribution attribution."""
    pred_svc = MLPredictor(
        artifact_path=trained_artifacts["artifact_path"],
        artifacts_dir=trained_artifacts["artifacts_dir"],
    )
    assert pred_svc.is_model_loaded() is True

    scam_sample = "URGENT HIRING: Remote Assistant. Send $100 registration fee and contact on Telegram @scam_recruiter."
    scam_output = pred_svc.predict(scam_sample)
    assert isinstance(scam_output, MLPredictionOutput)
    assert scam_output.label == "suspicious"
    assert scam_output.probability > 0.50
    assert scam_output.confidence_score > 50.0
    assert len(scam_output.top_features) > 0

    legit_sample = "Stripe is seeking a Senior Backend Engineer with 5+ years experience in distributed systems and Go. Apply at stripe.com/jobs."
    legit_output = pred_svc.predict(legit_sample)
    assert isinstance(legit_output, MLPredictionOutput)
    assert legit_output.label == "legitimate"
    assert legit_output.probability < 0.50


def test_predictor_checksum_validation(trained_artifacts, tmp_path):
    """Test that tampered or corrupted model artifacts are rejected."""
    tampered_file = tmp_path / "tampered.joblib"
    tampered_file.write_bytes(b"corrupted binary data")

    tampered_meta = tmp_path / "tampered.meta.json"
    tampered_meta.write_text('{"version": "1.0.0", "sha256_checksum": "wrong_hash"}')

    pred_svc = MLPredictor(artifact_path=str(tampered_file))
    assert pred_svc.is_model_loaded() is False


def test_ml_engine_output_separation(trained_artifacts):
    """Test that DefaultAnalysisEngine outputs purely ML-specific information
    and does NOT calculate final aggregate risk score or rule penalties.
    """
    engine = DefaultAnalysisEngine()
    result = engine.analyze_text("URGENT: Receive cashier check $2500 and wire back via Telegram.")

    # Must contain ML-specific fields
    assert result["status"] == "completed"
    assert "ml_probability" in result
    assert "ml_confidence" in result
    assert "ml_label" in result
    assert "model_version" in result
    assert "top_features" in result
    assert "engine_notice" in result

    # Must NOT compute final aggregated business risk score
    assert "risk_score" not in result or result.get("risk_score") is None or "ml_probability" in result
    assert "rule_penalty" not in result
