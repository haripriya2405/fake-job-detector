"""Test Suite for JobScamScore 8-Layer Signal Stack & Intelligence (Phase 21)."""

import pytest
from app.services.careers_page_service import careers_page_service
from app.services.reputation_intelligence_service import reputation_intelligence_service
from app.schemas.analysis import AnalysisCreate
from app.services.analysis_service import AnalysisService
from app.db.session import SessionLocal


def test_careers_page_greenhouse_verification():
    """Verify Greenhouse ATS URL is recognized as official corporate ATS."""
    res = careers_page_service.verify_careers_origin(url="https://boards.greenhouse.io/stripe/jobs/12345")
    assert res.is_official_ats is True
    assert res.ats_provider == "Greenhouse"
    assert res.verdict == "OFFICIAL_ATS_VERIFIED"
    assert res.risk_points == 0


def test_careers_page_lever_verification():
    """Verify Lever ATS URL is recognized as official corporate ATS."""
    res = careers_page_service.verify_careers_origin(url="https://jobs.lever.co/figma/abc-def")
    assert res.is_official_ats is True
    assert res.ats_provider == "Lever"
    assert res.verdict == "OFFICIAL_ATS_VERIFIED"


def test_reputation_intelligence_detects_fresh_domain_and_free_email():
    """Verify reputation engine flags brand new domain (< 30 days) and free email."""
    rep = reputation_intelligence_service.evaluate_reputation(
        domain="amazon-recruiter-portal-jobs.xyz",
        domain_age_days=14,
        is_free_email=True,
        salary_unrealistic=True,
        scam_rules_triggered=[{"rule_id": "REG_FEE", "name": "Registration Fee Trap", "severity": "CRITICAL"}],
    )

    assert rep.trust_score < 40
    assert rep.domain_reputation_level == "CRITICAL_THREAT"
    assert any("Domain registered only 14 days ago" in f for f in rep.red_flags)
    assert any("free email" in f for f in rep.red_flags)
    assert any("Registration Fee Trap" in f for f in rep.red_flags)


def test_end_to_end_8_layer_signal_stack_generation():
    """Verify AnalysisService returns complete 8-layer signal schemas and Red/Green flags."""
    db = SessionLocal()
    try:
        service = AnalysisService(db)
        posting = AnalysisCreate(
            raw_content="Stripe is seeking a Staff Backend Engineer. Must have 5+ years Go/Python experience. Comprehensive healthcare, 401(k) matching. Apply via https://boards.greenhouse.io/stripe/jobs/123.",
            job_title="Staff Backend Engineer",
            company_name="Stripe",
        )
        resp = service.create_text_analysis(posting)

        assert resp.signals_8_layer is not None
        assert resp.signals_8_layer.layer_1_company_authentication is not None
        assert resp.signals_8_layer.layer_2_careers_page_verification is not None
        assert resp.signals_8_layer.layer_3_recruiter_identity is not None
        assert resp.signals_8_layer.layer_4_salary_benchmarking is not None
        assert resp.signals_8_layer.layer_5_scam_pattern_detection is not None
        assert resp.signals_8_layer.layer_6_contact_validation is not None
        assert resp.signals_8_layer.layer_7_domain_ssl_intelligence is not None
        assert resp.signals_8_layer.layer_8_live_threat_intelligence is not None
        assert resp.verdict_category in ["SAFE", "CAUTION", "RISKY"]
        assert isinstance(resp.red_flags, list)
        assert isinstance(resp.green_flags, list)
    finally:
        db.close()
