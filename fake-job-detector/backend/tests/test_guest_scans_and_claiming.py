"""Test Suite for Phase 24 Feature 3: Frictionless Guest Scanning & Account Claiming."""

import pytest
from app.models.analysis import Analysis
from app.models.user import User


def test_anonymous_guest_scan_creation(client):
    """Verify unauthenticated guest users can perform instant real-time scan."""
    payload = {
        "raw_content": "URGENT HIRING: Remote Customer Support Rep. $35/hr. Apply with your resume and contact hr@legitcompany.com.",
        "job_title": "Customer Support Representative",
        "company_name": "Legit Company Inc.",
        "source_type": "text",
    }
    # No auth header passed
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["job_title"] == "Customer Support Representative"
    assert data["risk_level"] in ["low", "medium", "high", "critical", "evaluated", "pending"]


def test_claim_guest_analysis_to_user_account(client, db_session, test_user):
    """Verify logged-in user can claim an anonymous guest analysis report."""
    # 1. Create guest analysis (user_id is None)
    guest_analysis = Analysis(
        job_title="Remote Billing Analyst",
        company_name="Apex Logistics",
        source_type="text",
        raw_content="Remote billing role. Send resume and references.",
        risk_score=20,
        risk_level="low",
        analysis_engine="RuleEngine+ML",
        user_id=None,
    )
    db_session.add(guest_analysis)
    db_session.commit()
    db_session.refresh(guest_analysis)

    assert guest_analysis.user_id is None

    # 2. Authenticate as test_user via JSON body
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "test.analyst@sentinel.ai", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Claim the analysis
    claim_res = client.post(f"/api/v1/analysis/{guest_analysis.id}/claim", headers=headers)
    assert claim_res.status_code == 200
    claim_data = claim_res.json()
    assert claim_data["id"] == str(guest_analysis.id)

    # 4. Verify in DB that user_id is now test_user.id
    db_session.refresh(guest_analysis)
    assert guest_analysis.user_id == test_user.id


def test_claim_guest_analysis_unauthenticated_fails(client, db_session):
    """Verify unauthenticated user cannot claim an analysis without login."""
    guest_analysis = Analysis(
        job_title="Data Entry Assistant",
        company_name="Random Corp",
        source_type="text",
        raw_content="Data entry role with competitive pay.",
        risk_score=10,
        risk_level="low",
        analysis_engine="RuleEngine+ML",
        user_id=None,
    )
    db_session.add(guest_analysis)
    db_session.commit()
    db_session.refresh(guest_analysis)

    # Attempt claim with no Authorization header
    response = client.post(f"/api/v1/analysis/{guest_analysis.id}/claim")
    assert response.status_code in [401, 422]
