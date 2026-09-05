"""Test Suite for Transformer Explainability, Character Offsets, and Span Attribution."""

import pytest
from app.ml.predictor import MLPredictor


@pytest.fixture
def predictor():
    return MLPredictor(artifacts_dir="artifacts/models")


def test_span_character_offsets_exact_matching(predictor):
    """Verify extracted token spans match the exact slice of original text."""
    text = (
        "Immediate opening! Deposit $3,200 cashier check into your account and transfer $2,800 "
        "to our supply coordinator on Telegram @Coord_2026."
    )
    features, highlights = predictor._extract_transformer_manipulation_spans(text, fraud_prob=0.98)

    assert len(highlights) >= 2
    for h in highlights:
        start, end, matched = h["start"], h["end"], h["matched_text"]
        assert text[start:end] == matched
        assert len(h["context_sentence"]) > 0
        assert matched in h["context_sentence"]
        assert 0.0 <= h["risk_weight"] <= 1.0


def test_explainability_categories_differentiate_scam_types(predictor):
    """Verify distinct scam patterns produce appropriate category classifications."""
    cases = [
        ("We mail you a cashier check to purchase home equipment.", "fake_check_reimbursement"),
        ("Compulsory registration fee of $120 must be paid before interview.", "upfront_fee_demand"),
        ("Contact our hiring manager on Telegram t.me/fast_hire.", "channel_diversion"),
        ("Recharge workstation wallet with 50 USDT to unlock daily tasks.", "crypto_task_trap"),
        ("Provide your netbanking password and verification pin.", "credential_harvesting"),
    ]

    for text, expected_category in cases:
        features, highlights = predictor._extract_transformer_manipulation_spans(text, fraud_prob=0.95)
        categories = [h["category"] for h in highlights]
        assert expected_category in categories, f"Expected {expected_category} in {categories} for '{text}'"


def test_feature_contributions_have_sentence_and_direction(predictor):
    """Verify top feature contributions include complete context sentence and direction."""
    text = "Urgent selection guaranteed. Send $200 onboarding fee via CashApp."
    features, _ = predictor._extract_transformer_manipulation_spans(text, fraud_prob=0.90)

    assert len(features) > 0
    for feat in features:
        assert feat.direction in ["suspicious", "legitimate"]
        assert feat.start_char is not None
        assert feat.end_char is not None
        assert feat.context_sentence is not None
        assert feat.weight > 0.0
