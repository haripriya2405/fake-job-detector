"""Test Suite for Model Error Analysis and PII Sanitization (Phase 20)."""

import pandas as pd
import pytest
from app.ml.error_analysis import ErrorAnalyzer


@pytest.fixture
def analyzer():
    return ErrorAnalyzer()


def test_pii_sanitization_redacts_sensitive_tokens(analyzer):
    """Verify analyzer strictly redacts emails, phone numbers, and crypto addresses."""
    raw_sample = (
        "Send verification to hr.recruiter_test@domain-service.com or call +1 (555) 234-5678. "
        "Deposit 50 USDT to wallet 0x71C7656EC7ab88b098defB751B7401B5f6d8976F with password: secretPassword123"
    )
    sanitized = analyzer.sanitize_pii(raw_sample)

    assert "[REDACTED_EMAIL]" in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "[REDACTED_WALLET]" in sanitized
    assert "secretPassword123" not in sanitized
    assert "hr.recruiter_test@domain-service.com" not in sanitized
    assert "+1 (555) 234-5678" not in sanitized


def test_disagreement_classification_cases(analyzer):
    """Verify analyzer accurately partitions case agreement and disagreement types."""
    df = pd.DataFrame([
        {"record_id": "R1", "text": "Clean corporate software engineering job posting.", "label": 0},
        {"record_id": "R2", "text": "Pay refundable registration fee of $150 before interview.", "label": 1},
        {"record_id": "R3", "text": "Ambiguous remote typing job with weekly stipend.", "label": 0},
        {"record_id": "R4", "text": "Deposit fake cashier check and wire remainder.", "label": 1},
    ])

    base_probs = [0.10, 0.90, 0.51, 0.20]  # R4 is wrongly predicted by baseline
    cand_probs = [0.05, 0.95, 0.49, 0.92]  # R4 is correctly predicted by candidate

    analysis = analyzer.analyze_disagreements(df, base_probs, cand_probs)

    assert analysis["total_analyzed"] == 4
    counts = analysis["summary_counts"]
    assert counts["BOTH_CORRECT"] >= 1
    assert counts["TRANSFORMER_CORRECT"] >= 1
    assert "fake_check_reimbursement" in analysis["category_error_distribution"]
