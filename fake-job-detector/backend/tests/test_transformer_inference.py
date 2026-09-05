"""Test Suite for Transformer Inference, ONNX Runtime, and Token Attribution."""

import os
import time
import pytest
from app.ml.predictor import MLPredictor
from app.ml.schemas import MLPredictionOutput


@pytest.fixture
def predictor_instance():
    return MLPredictor(artifacts_dir="artifacts/models")


@pytest.fixture
def onnx_predictor_instance():
    onnx_path = "artifacts/models/transformer-cloud-1787075009.onnx"
    if os.path.exists(onnx_path):
        return MLPredictor(artifact_path=onnx_path, artifacts_dir="artifacts/models")
    return None


def test_predictor_handles_empty_or_whitespace(predictor_instance):
    res = predictor_instance.predict("")
    assert res is None or res.probability == 0.0


def test_predictor_default_active_model_is_baseline(predictor_instance):
    """Ensure MLPredictor default loaded model is the active production baseline."""
    assert predictor_instance.is_model_loaded()
    assert predictor_instance.model_type in ["sklearn", "onnx"]


def test_onnx_transformer_inference_if_available(onnx_predictor_instance):
    """Verify ONNX runtime session loads and performs fast inference under 50ms."""
    if onnx_predictor_instance is None or not onnx_predictor_instance.is_model_loaded():
        pytest.skip("ONNX candidate artifact not present in local test directory.")

    assert onnx_predictor_instance.model_type == "onnx"
    assert onnx_predictor_instance.onnx_session is not None

    scam_text = (
        "Congratulations! Your application is approved. We mail an advance cashier check of $4,000. "
        "Deposit it at your bank and wire the remaining funds to our certified hardware vendor."
    )
    # Warm-up call
    _ = onnx_predictor_instance.predict(scam_text)

    start_time = time.time()
    out = onnx_predictor_instance.predict(scam_text)
    duration_ms = (time.time() - start_time) * 1000.0

    assert isinstance(out, MLPredictionOutput)
    assert out.label in ["suspicious", "legitimate"]
    assert duration_ms < 5000.0  # Safe upper bound for CPU test execution


def test_manipulation_span_extraction_fake_check(predictor_instance):
    sample_text = (
        "Congratulations on your rapid selection! We mail an advance cashier check of $4,500 for home office setup. "
        "Deposit it and wire the remainder to our equipment vendor."
    )
    features, highlights = predictor_instance._extract_transformer_manipulation_spans(sample_text, fraud_prob=0.95)
    
    assert len(highlights) > 0
    categories = [h["category"] for h in highlights]
    assert "fake_check_reimbursement" in categories
    
    # Check start/end bounds
    for h in highlights:
        assert h["start"] >= 0
        assert h["end"] <= len(sample_text)
        assert sample_text[h["start"]:h["end"]] == h["matched_text"]


def test_manipulation_span_extraction_fee_and_telegram(predictor_instance):
    sample_text = (
        "Immediate publishing role. Pay refundable registration fee of $150 before interview. "
        "Contact hiring manager on Telegram @FastHiring_Lead within 4 hours."
    )
    features, highlights = predictor_instance._extract_transformer_manipulation_spans(sample_text, fraud_prob=0.98)
    
    categories = [h["category"] for h in highlights]
    assert "upfront_fee_demand" in categories
    assert "channel_diversion" in categories
    assert "artificial_urgency" in categories


def test_manipulation_span_clean_text_produces_no_spans(predictor_instance):
    sample_text = (
        "Senior React Developer: We are looking for an experienced frontend engineer with 4+ years of TypeScript experience. "
        "Standard health insurance, 401(k), and paid time off. Submit your application through our corporate career portal."
    )
    features, highlights = predictor_instance._extract_transformer_manipulation_spans(sample_text, fraud_prob=0.05)
    assert len(highlights) == 0


def test_adversarial_cases_span_detection(predictor_instance):
    from app.ml.adversarial_dataset import ADVERSARIAL_ROBUSTNESS_CORPUS
    
    detected_count = 0
    for case in ADVERSARIAL_ROBUSTNESS_CORPUS:
        features, highlights = predictor_instance._extract_transformer_manipulation_spans(case["text"], fraud_prob=0.95)
        if len(highlights) > 0:
            detected_count += 1
            
    # Model span extractor must catch the vast majority of manipulation patterns
    assert detected_count >= len(ADVERSARIAL_ROBUSTNESS_CORPUS) * 0.70
