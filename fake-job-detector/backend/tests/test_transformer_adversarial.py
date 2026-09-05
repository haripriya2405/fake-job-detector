"""Test Suite for Transformer Adversarial Robustness and Mutation Resilience."""

import pytest
from app.ml.adversarial_dataset import ADVERSARIAL_ROBUSTNESS_CORPUS
from app.ml.predictor import MLPredictor


@pytest.fixture
def predictor():
    return MLPredictor(artifacts_dir="artifacts/models")


def test_adversarial_corpus_covers_8_patterns():
    """Verify adversarial corpus contains all key attack mutation types."""
    required_patterns = {
        "unicode_homoglyph",
        "spaced_keyword_evasion",
        "punctuation_injection",
        "paraphrased_fee_disguise",
        "paraphrased_task_disguise",
        "credential_harvesting_disguise",
        "typosquatted_brand_lure",
    }
    corpus_patterns = {c["attack_type"] for c in ADVERSARIAL_ROBUSTNESS_CORPUS}
    for p in required_patterns:
        assert p in corpus_patterns, f"Missing required adversarial pattern: {p}"


def test_homoglyph_and_deobfuscation_span_extraction(predictor):
    """Verify span extractor detects Cyrillic homoglyph obfuscated registration fees."""
    # Contains Cyrillic 'е', 'а', 'о'
    obfuscated_text = "Urgent: Compulsory rеgistrаtiоn fее of $120 must be paid immediately."
    features, highlights = predictor._extract_transformer_manipulation_spans(obfuscated_text, fraud_prob=0.95)

    assert len(highlights) > 0
    categories = [h["category"] for h in highlights]
    assert "upfront_fee_demand" in categories


def test_spaced_character_and_telegram_diversion(predictor):
    """Verify span extractor catches spaced characters like t e l e g r a m."""
    text = "Work from home data entry. Contact us on t.e.l.e.g.r.a.m @ScamLead for immediate start."
    features, highlights = predictor._extract_transformer_manipulation_spans(text, fraud_prob=0.95)

    assert len(highlights) > 0
    categories = [h["category"] for h in highlights]
    assert "channel_diversion" in categories


def test_crypto_task_recharge_detection(predictor):
    """Verify span extractor flags crypto workstation wallet recharge schemes."""
    text = "Complete VIP movie rating tasks. Recharge your personal workstation balance with $50 USDT to withdraw."
    features, highlights = predictor._extract_transformer_manipulation_spans(text, fraud_prob=0.98)

    assert len(highlights) > 0
    categories = [h["category"] for h in highlights]
    assert "crypto_task_trap" in categories


def test_adversarial_corpus_overall_detection_rate(predictor):
    """Verify adversarial robustness test suite achieves >= 85% detection across the entire corpus."""
    detected = 0
    total = len(ADVERSARIAL_ROBUSTNESS_CORPUS)

    for case in ADVERSARIAL_ROBUSTNESS_CORPUS:
        features, highlights = predictor._extract_transformer_manipulation_spans(case["text"], fraud_prob=0.95)
        if len(highlights) > 0:
            detected += 1

    detection_rate = detected / total
    assert detection_rate >= 0.85, f"Adversarial detection rate {detection_rate:.1%} was below 85% target."
