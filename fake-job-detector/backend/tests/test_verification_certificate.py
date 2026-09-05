"""Test Suite for Phase 24 Feature 2: Public Shareable Verification Certificate & Trust Badges."""

from datetime import datetime, timezone
import pytest
from app.models.analysis import Analysis
from app.services.certificate_service import certificate_service


def test_generate_and_verify_signature_tamper_detection():
    """Verify HMAC-SHA256 signature validates original payload and rejects tampered data."""
    analysis_id = "123e4567-e89b-12d3-a456-426614174000"
    created_at = datetime(2026, 9, 5, 12, 0, 0, tzinfo=timezone.utc)
    risk_score = 12
    company = "Google LLC"

    sig = certificate_service.generate_signature(analysis_id, risk_score, company, created_at)
    assert isinstance(sig, str)
    assert len(sig) == 64

    # Verification of genuine payload
    assert certificate_service.verify_signature(sig, analysis_id, risk_score, company, created_at) is True

    # Tampering with risk_score or company must fail verification
    assert certificate_service.verify_signature(sig, analysis_id, 99, company, created_at) is False
    assert certificate_service.verify_signature(sig, analysis_id, risk_score, "Impostor Corp", created_at) is False


def test_get_certificate_safe_job(client, db_session):
    """Verify endpoint returns legitimate verification certificate with emerald badge."""
    analysis = Analysis(
        job_title="Staff Site Reliability Engineer",
        company_name="Datadog Inc.",
        source_type="url",
        raw_content="Staff SRE role. Experience with Kubernetes, Go, Terraform. Comprehensive benefits and 401(k).",
        risk_score=15,
        risk_level="low",
        explanation="Official enterprise job opening verified via Lever ATS.",
        analysis_engine="RuleEngine+ML",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    # Query public certificate API
    response = client.get(f"/api/v1/verify/{analysis.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["analysis_id"] == str(analysis.id)
    assert data["job_title"] == "Staff Site Reliability Engineer"
    assert data["company_name"] == "Datadog Inc."
    assert data["risk_score"] == 15
    assert data["legitimacy_verdict"] == "VERIFIED_SAFE"
    assert data["verdict_badge_color"] == "emerald"
    assert data["is_tamper_evident_valid"] is True
    assert len(data["digital_signature"]) == 64
    assert len(data["sha256_fingerprint"]) == 64
    assert "badge.svg" in data["embed_badge_svg_url"]
    assert "[![JobScamScore Verified]" in data["embed_badge_markdown"]


def test_get_certificate_scam_job(client, db_session):
    """Verify high-risk scam posting returns crimson warning certificate."""
    analysis = Analysis(
        job_title="Remote Typist - Urgent Deposit Required",
        company_name="Apex Global Logistics (Impostor)",
        source_type="text",
        raw_content="Send $150 Zelle registration fee to lock your interview on Telegram.",
        risk_score=95,
        risk_level="critical",
        explanation="Advance fee fraud detected with Telegram diversion.",
        analysis_engine="RuleEngine+ML",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    response = client.get(f"/api/v1/verify/{analysis.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["risk_score"] == 95
    assert data["legitimacy_verdict"] == "HIGH_RISK_SUSPICIOUS"
    assert data["verdict_badge_color"] == "crimson"
    assert "CRITICAL WARNING" in data["summary"]


def test_get_certificate_not_found(client):
    """Verify non-existent ID returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/verify/{fake_id}")
    assert response.status_code == 404


def test_get_verification_badge_svg(client, db_session):
    """Verify badge.svg streams clean image/svg+xml vector graphics."""
    analysis = Analysis(
        job_title="Backend Software Architect",
        company_name="Amazon Web Services",
        source_type="text",
        raw_content="Senior Principal Engineer job posting at Amazon.",
        risk_score=8,
        risk_level="low",
        explanation="Verified legitimate posting.",
        analysis_engine="RuleEngine+ML",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    response = client.get(f"/api/v1/verify/{analysis.id}/badge.svg")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/svg+xml"
    svg_text = response.text
    assert "<svg" in svg_text
    assert "JobScamScore" in svg_text
    assert "VERIFIED SAFE" in svg_text
