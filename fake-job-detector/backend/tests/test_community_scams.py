"""Test Suite for Phase 24 Feature 1: Public Community Scam Intelligence Database & Threat Feed."""

from app.ml.predictor import MLPredictor
from app.models.analysis import Analysis
from app.services.community_scam_service import community_scam_service


# ============================================================================
# 1. PII Redaction Unit Tests
# ============================================================================

def test_pii_redaction_removes_emails_phones_ssns():
    """Verify regex sanitization replaces personal information with secure placeholders."""
    raw_text = (
        "Applicant John Doe, email john.doe.2024@gmail.com, phone (555) 342-9812, "
        "SSN 123-45-6789. Send deposit to Chase account 4123 4567 8901 2345."
    )
    redacted = community_scam_service.redact_pii(raw_text)

    assert "john.doe.2024@gmail.com" not in redacted
    assert "j***@gmail.com" in redacted
    assert "(555) 342-9812" not in redacted
    assert "[REDACTED PHONE]" in redacted
    assert "123-45-6789" not in redacted
    assert "[REDACTED SSN]" in redacted
    assert "4123 4567 8901 2345" not in redacted
    assert "[REDACTED ACCOUNT/CARD]" in redacted


# ============================================================================
# 2. Feed & Pagination API Tests
# ============================================================================

def test_community_scams_feed_pagination_and_seeding(client):
    """Verify endpoint auto-seeds threat corpus and returns paginated feed."""
    response = client.get("/api/v1/community/scams?page=1&page_size=3")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] >= 5
    assert len(data["items"]) == 3
    assert data["page"] == 1
    assert "stats" in data
    assert data["stats"]["total_threats"] >= 5
    assert data["stats"]["avg_risk_score"] > 80.0

    # First item structure verification
    first = data["items"][0]
    assert first["public_id"].startswith("SCAM-2026-")
    assert first["risk_score"] >= 80
    assert isinstance(first["red_flags"], list)
    assert len(first["red_flags"]) > 0


def test_community_scams_search_and_category_filter(client):
    """Verify search by keyword and category filters return exact matches."""
    # Filter by Telegram category
    resp_cat = client.get("/api/v1/community/scams?category=TELEGRAM_INTERVIEW")
    assert resp_cat.status_code == 200
    cat_data = resp_cat.json()
    assert all(item["scam_category"] == "TELEGRAM_INTERVIEW" for item in cat_data["items"])

    # Search keyword
    resp_q = client.get("/api/v1/community/scams?query=cashier%20check")
    assert resp_q.status_code == 200
    q_data = resp_q.json()
    assert len(q_data["items"]) > 0
    assert any("check" in item["description_snippet"].lower() for item in q_data["items"])


# ============================================================================
# 3. Detail & Confirmation Tests
# ============================================================================

def test_community_scam_detail_by_public_id(client):
    """Verify fetching single threat dossier by public ID."""
    response = client.get("/api/v1/community/scams/SCAM-2026-1002")
    assert response.status_code == 200
    data = response.json()
    assert data["public_id"] == "SCAM-2026-1002"
    assert data["scam_category"] == "CHECK_FRAUD"
    assert data["impostor_company"] == "Vertex Healthcare Solutions"


def test_community_scam_confirm_threat(client):
    """Verify community confirmation upvote increments threat tally."""
    # Get initial count
    initial_res = client.get("/api/v1/community/scams/SCAM-2026-1001")
    initial_count = initial_res.json()["community_confirmations"]

    # Upvote
    confirm_res = client.post("/api/v1/community/scams/SCAM-2026-1001/confirm")
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()
    assert confirm_data["community_confirmations"] == initial_count + 1


# ============================================================================
# 4. Anonymized Scan Publishing Tests
# ============================================================================

def test_community_scam_publish_from_analysis(client, db_session):
    """Verify user scan report is anonymized and published to community threat database."""
    # Seed an analysis in test db
    test_analysis = Analysis(
        job_title="Urgent Remote Cryptography Task Rater",
        company_name="ScamCorp Global",
        source_type="text",
        raw_content="Contact recruiter Mary at mary.smith@gmail.com. Complete 20 tasks, deposit 50 USDT to unlock your $300 commission.",
        risk_score=94,
        risk_level="critical",
        explanation="Crypto task recharge scam detected requesting 50 USDT deposit.",
        analysis_engine="RuleEngine+ML",
    )
    db_session.add(test_analysis)
    db_session.commit()
    db_session.refresh(test_analysis)

    # Publish to community
    publish_payload = {
        "analysis_id": str(test_analysis.id),
        "consent_anonymize": True,
        "custom_notes": "Scammer reached out via WhatsApp offering task rating.",
    }
    pub_res = client.post("/api/v1/community/scams/publish", json=publish_payload)
    assert pub_res.status_code == 201
    pub_data = pub_res.json()

    assert pub_data["public_id"].startswith("SCAM-2026-")
    assert pub_data["job_title"] == "Urgent Remote Cryptography Task Rater"
    assert pub_data["scam_category"] == "CRYPTO_TASK"
    # Verify candidate email is masked
    assert "mary.smith@gmail.com" not in pub_data["description_snippet"]
    assert "m***@gmail.com" in pub_data["description_snippet"]


# ============================================================================
# 5. ML Model Inference on Community Threat Samples
# ============================================================================

def test_ml_models_classify_community_scams():
    """Verify baseline and active ML models detect elevated threat probability on community threats."""
    predictor = MLPredictor(artifact_path="artifacts/models/tfidf_logistic_regression_v1.0.0.joblib")

    for sample in community_scam_service.DEFAULT_THREAT_CORPUS:
        pred = predictor.predict(sample["description_snippet"])
        assert pred is not None
        # Community threat snippets must produce elevated threat confidence
        assert pred.probability >= 0.35, f"Failed on sample {sample['public_id']}"
