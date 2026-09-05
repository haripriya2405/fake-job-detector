"""Test Suite for Phase 24 Feature 4: Phone Carrier VoIP & Fraud Watchlists (FTC/BBB/IC3)."""

import pytest
from app.services.fraud_watchlist_service import fraud_watchlist_service
from app.services.phone_carrier_service import phone_carrier_service


def test_phone_extraction_and_voip_carrier_classification():
    """Verify phone numbers are parsed and virtual VoIP burner lines are detected."""
    sample_text = (
        "Contact hiring manager via SMS/WhatsApp at +1 (555) 432-8901. "
        "We also use TextNow virtual line (415) 800-1234 for quick screening."
    )
    res = phone_carrier_service.analyze_contact_phones(sample_text)

    assert res["detected"] is True
    assert res["phone_count"] >= 2
    assert res["has_voip_burner"] is True
    assert res["risk_penalty"] > 0

    # Verify individual phone classification
    phone_types = [p["line_type"] for p in res["phones"]]
    assert any("VOIP" in t for t in phone_types)


def test_toll_free_number_handling():
    """Verify enterprise toll-free 1-800 numbers are classified as TOLL_FREE."""
    sample_text = "Call official corporate customer service at 1-800-555-0199 or (888) 123-4567."
    res = phone_carrier_service.analyze_contact_phones(sample_text)

    assert res["detected"] is True
    assert all(p["line_type"] == "TOLL_FREE" for p in res["phones"])
    assert res["has_voip_burner"] is False


def test_fraud_watchlist_fake_check_match():
    """Verify text containing fake cashier check trap matches FTC alert."""
    text = (
        "We are mailing you an advance cashier check for $3,500. Deposit the check and "
        "forward the remaining amount to our certified equipment vendor."
    )
    match_res = fraud_watchlist_service.cross_reference_posting(text, company_name="Apex Impostor")

    assert match_res["has_watchlist_matches"] is True
    assert match_res["status_verdict"] == "MATCHED_WARNING"
    assert match_res["match_count"] >= 1
    assert "FTC" in match_res["agencies_flagged"]
    assert match_res["risk_penalty"] >= 20

    # Ensure FTC alert is present
    titles = [m["title"] for m in match_res["matches"]]
    assert any("Cashier Check" in t for t in titles)


def test_fraud_watchlist_crypto_task_match():
    """Verify crypto task recharge scam matches FTC / BBB alert."""
    text = (
        "Earn 300 USDT daily rating products. Deposit recharge to clear negative balance "
        "and unlock commission withdrawal."
    )
    match_res = fraud_watchlist_service.cross_reference_posting(text)

    assert match_res["has_watchlist_matches"] is True
    assert "FTC" in match_res["agencies_flagged"] or "BBB" in match_res["agencies_flagged"]
    assert match_res["risk_penalty"] >= 20


def test_fraud_watchlist_clean_posting():
    """Verify standard legitimate engineering posting yields clean pass."""
    text = (
        "Senior Backend Engineer: 5+ years experience in Python, FastAPI, Docker, and PostgreSQL. "
        "Comprehensive health benefits, 401(k) match, and remote flexibility."
    )
    match_res = fraud_watchlist_service.cross_reference_posting(text, company_name="Stripe Inc.")

    assert match_res["has_watchlist_matches"] is False
    assert match_res["status_verdict"] == "CLEAN_PASS"
    assert match_res["match_count"] == 0
    assert match_res["risk_penalty"] == 0


def test_analysis_api_includes_phone_and_watchlist_intelligence(client):
    """Verify AnalysisResponse payload contains phone_intelligence and fraud_watchlists objects."""
    payload = {
        "raw_content": "URGENT HIRING: Data entry. Call our TextNow line (347) 491-9988. We send cashier check for equipment.",
        "job_title": "Remote Data Entry Assistant",
        "company_name": "Apex Fraud Entity",
        "source_type": "text",
    }
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "phone_intelligence" in data
    assert data["phone_intelligence"]["detected"] is True
    assert data["phone_intelligence"]["has_voip_burner"] is True

    assert "fraud_watchlists" in data
    assert data["fraud_watchlists"]["has_watchlist_matches"] is True
    assert "FTC" in data["fraud_watchlists"]["agencies_flagged"]
