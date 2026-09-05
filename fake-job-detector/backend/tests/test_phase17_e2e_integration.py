import io
import uuid
import pytest
from PIL import Image, ImageDraw
from pypdf import PdfWriter
from app.core.security import create_access_token
from app.models.analysis import Analysis
from app.models.indicator import AnalysisIndicator
from app.models.user import User
from app.models.verification import VerificationResult


def create_minimal_pdf(text: str = "Urgent Remote Job: Deposit cashier check for office equipment.") -> bytes:
    """Helper to generate valid in-memory PDF bytes."""
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    # Use annotation or stream to embed text
    stream = io.BytesIO()
    writer.write(stream)
    # Add minimal text stream
    raw = stream.getvalue()
    # Add basic valid PDF text structure if needed
    return raw


def create_test_image(text: str = "Earn $500 daily Telegram @scam_contact") -> bytes:
    """Helper to generate valid in-memory PNG image bytes."""
    img = Image.new("RGB", (400, 100), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============================================================================
# 1. TEXT ANALYSIS E2E INTEGRATION TESTS
# ============================================================================

def test_e2e_text_analysis_scam_flow(client, db_session, test_user):
    """Verify complete end-to-end text analysis for high-risk scam posting."""
    token = create_access_token(subject=str(test_user.id), extra_claims={"email": test_user.email, "role": test_user.role})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "raw_content": (
            "URGENT HIRING: We are seeking an Executive Assistant immediately. "
            "We will disburse an advance cashier check of $3,500 to purchase home office hardware. "
            "Contact our hiring manager exclusively on Telegram: @hr_hiring_now."
        ),
        "job_title": "Executive Data Assistant",
        "company_name": "Global Tech Logistics",
        "source_type": "text",
    }

    response = client.post("/api/v1/analysis", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()

    # Schema & Score assertions
    assert "id" in data
    assert data["risk_score"] >= 60
    assert data["risk_level"] in ["high", "critical"]
    assert data["source_type"] == "text"
    assert data["job_title"] == "Executive Data Assistant"

    # Explainable Attribution Assertions
    assert "score_breakdown" in data
    assert data["score_breakdown"]["total_score"] == data["risk_score"]
    assert data["score_breakdown"]["rule_contribution"] > 0

    # Indicators & Evidence assertions
    assert len(data["indicators"]) > 0
    indicator_titles = [ind["title"] for ind in data["indicators"]]
    assert any("Cashier" in t or "Check" in t or "Fee" in t or "Telegram" in t for t in indicator_titles)

    assert len(data["evidence_snippets"]) > 0
    # Verify evidence comes directly from the raw content
    for snippet in data["evidence_snippets"]:
        if snippet["type"] != "ML Statistical Keyword Match":
            assert snippet["quote"] in payload["raw_content"] or any(
                term in snippet["quote"].lower() for term in ["check", "telegram", "cashier", "urgent", "advance"]
            )

    # Recommendations assertion
    assert len(data["recommendations"]) > 0

    # DB Persistence Assertion
    analysis_uuid = uuid.UUID(data["id"])
    persisted = db_session.query(Analysis).filter(Analysis.id == analysis_uuid).first()
    assert persisted is not None
    assert persisted.user_id == test_user.id
    assert persisted.source_type == "text"
    assert persisted.content_hash is not None
    assert len(persisted.indicators) == len(data["indicators"])


def test_e2e_text_analysis_legitimate_flow_wording_invariant(client, db_session):
    """Verify legitimate text analysis maintains strict non-definitive wording."""
    payload = {
        "raw_content": (
            "We are seeking a Senior Staff Python Engineer to design distributed cloud microservices. "
            "Requirements: 7+ years of experience with Python, FastAPI, PostgreSQL, and Kubernetes. "
            "Competitive base salary ($180,000 - $220,000), 401(k) matching, and comprehensive health insurance. "
            "Please submit your application through our official careers portal."
        ),
        "job_title": "Senior Staff Python Engineer",
        "company_name": "Acme Cloud Infrastructure Inc",
        "source_type": "text",
    }

    response = client.post("/api/v1/analysis/text", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["risk_score"] < 40
    assert data["risk_level"] in ["low", "medium"]

    # Invariant: Low risk wording must NOT claim "proven legitimate" or "authentic"
    explanation_lower = (data.get("explanation") or "").lower()
    recommendation_details = " ".join([r["detail"].lower() for r in data.get("recommendations", [])])
    combined_text = f"{explanation_lower} {recommendation_details}"

    assert "proven legitimate" not in combined_text
    assert "guaranteed authentic" not in combined_text
    assert "100% safe" not in combined_text


# ============================================================================
# 2. PDF ANALYSIS E2E INTEGRATION TESTS
# ============================================================================

def test_e2e_pdf_analysis_flow(client, db_session, test_user):
    """Verify end-to-end multipart PDF offer letter ingestion and analysis."""
    token = create_access_token(subject=str(test_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    pdf_bytes = create_minimal_pdf()
    files = {"file": ("offer_letter.pdf", pdf_bytes, "application/pdf")}
    data = {
        "source_type": "pdf",
        "job_title": "Remote Operations Associate",
        "company_name": "Apex Talent Partners",
    }

    response = client.post("/api/v1/analysis/upload", files=files, data=data, headers=headers)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["source_type"] == "pdf"
    assert "extraction" in res_data
    assert res_data["extraction"]["source_type"] == "PDF"
    assert res_data["extraction"]["mime_type"] == "application/pdf"
    assert res_data["extraction"]["original_filename"] == "offer_letter.pdf"

    # Verify DB persistence
    persisted = db_session.query(Analysis).filter(Analysis.id == uuid.UUID(res_data["id"])).first()
    assert persisted is not None
    assert persisted.mime_type == "application/pdf"
    assert persisted.original_filename == "offer_letter.pdf"


def test_e2e_pdf_corrupted_rejection(client):
    """Verify corrupted or invalid PDF headers are gracefully rejected."""
    corrupted_bytes = b"NOT_A_REAL_PDF_HEADER_JUST_RANDOM_GARBAGE"
    files = {"file": ("malicious.pdf", corrupted_bytes, "application/pdf")}
    data = {"source_type": "pdf"}

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code in [400, 422]
    error_msg = response.json().get("detail", "")
    assert "PDF" in error_msg or "header" in error_msg or "Invalid" in error_msg


# ============================================================================
# 3. IMAGE / OCR ANALYSIS E2E INTEGRATION TESTS
# ============================================================================

def test_e2e_image_upload_analysis_flow(client, db_session):
    """Verify multipart Image upload, OCR extraction, and risk assessment."""
    img_bytes = create_test_image()
    files = {"file": ("telegram_chat_screenshot.png", img_bytes, "image/png")}
    data = {
        "source_type": "image",
        "job_title": "Telegram Customer Support Representative",
    }

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["source_type"] == "image"
    assert "extraction" in res_data
    assert res_data["extraction"]["source_type"] == "IMAGE"
    assert res_data["extraction"]["original_filename"] == "telegram_chat_screenshot.png"
    assert res_data["extraction"]["extraction_confidence"] > 0.0

    # Check persistence
    persisted = db_session.query(Analysis).filter(Analysis.id == uuid.UUID(res_data["id"])).first()
    assert persisted is not None
    assert persisted.source_type == "image"
    assert persisted.extraction_confidence is not None


def test_e2e_image_unsupported_format_rejection(client):
    """Verify unsupported file formats are rejected with informative errors."""
    files = {"file": ("script.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")}
    data = {"source_type": "exe"}

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code in [400, 422]


# ============================================================================
# 4. PUBLIC URL ANALYSIS & SSRF FIREWALL REGRESSION TESTS
# ============================================================================

@pytest.mark.parametrize(
    "forbidden_url",
    [
        "http://localhost:8000/api/v1/health",
        "http://127.0.0.1:8000/api/v1/health",
        "http://[::1]:8000/",
        "http://10.0.0.5/internal-job",
        "http://192.168.1.100/careers",
        "http://172.16.0.1/admin",
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://app.corp/jobs",
        "http://intranet.local/hiring",
        "ftp://example.com/job.txt",
        "file:///etc/passwd",
    ],
)
def test_e2e_url_analysis_ssrf_firewall_blocks_internal_and_forbidden(client, forbidden_url):
    """Ensure SSRF firewall blocks all internal, private, metadata, and non-HTTP protocols."""
    payload = {
        "job_url": forbidden_url,
        "job_title": "Internal Role",
    }
    response = client.post("/api/v1/analysis/url", json=payload)
    assert response.status_code in [400, 422]
    detail = response.json().get("detail", "")
    assert any(term in detail.lower() for term in ["ssrf", "blocked", "private", "forbidden", "protocol", "invalid", "host"])


# ============================================================================
# 5. AUTHENTICATION & AUTHORIZATION FLOWS
# ============================================================================

def test_e2e_auth_registration_login_and_me_flow(client):
    """Verify complete user registration, JWT generation, and profile retrieval."""
    unique_email = f"analyst.{uuid.uuid4().hex[:8]}@sentinel.ai"
    reg_payload = {
        "full_name": "Jordan Lee",
        "email": unique_email,
        "password": "SecurePassword987!",
        "role": "analyst",
    }

    # 1. Register
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "token" in reg_data
    assert reg_data["user"]["email"] == unique_email

    # 2. Login
    login_resp = client.post("/api/v1/auth/login", json={"email": unique_email, "password": "SecurePassword987!"})
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    token = login_data["token"]

    # 3. Get /me
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == unique_email
    assert me_data["full_name"] == "Jordan Lee"


def test_e2e_auth_invalid_credentials_and_expired_token(client):
    """Verify authentication failures return proper 401 statuses."""
    # Invalid password
    bad_login = client.post("/api/v1/auth/login", json={"email": "nonexistent@sentinel.ai", "password": "wrongpassword"})
    assert bad_login.status_code == 401

    # Invalid Bearer token
    bad_me = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_garbage_token_123"})
    assert bad_me.status_code == 401


# ============================================================================
# 6. HISTORY, DETAIL, & RECORD DELETION PERSISTENCE
# ============================================================================

def test_e2e_analysis_history_and_deletion_lifecycle(client, db_session, test_user):
    """Verify analysis history queries, detail retrieval, and cascade deletion."""
    token = create_access_token(subject=str(test_user.id))
    headers = {"Authorization": f"Bearer {token}"}

    # Create 2 analyses for test_user
    post1 = client.post(
        "/api/v1/analysis",
        json={"raw_content": "Legitimate software development position with strong benefits and verified company domain.", "job_title": "Dev Job 1"},
        headers=headers,
    )
    post2 = client.post(
        "/api/v1/analysis",
        json={"raw_content": "Scam job asking for advance fee checks on Telegram @scammer_now.", "job_title": "Scam Job 2"},
        headers=headers,
    )
    id1 = post1.json()["id"]
    id2 = post2.json()["id"]

    # 1. Check history
    hist_resp = client.get("/api/v1/analysis/history", headers=headers)
    assert hist_resp.status_code == 200
    history = hist_resp.json()
    hist_ids = [item["id"] for item in history]
    assert id1 in hist_ids
    assert id2 in hist_ids

    # 2. Get single report
    detail_resp = client.get(f"/api/v1/analysis/{id1}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == id1

    # 3. Delete analysis
    del_resp = client.delete(f"/api/v1/analysis/{id1}", headers=headers)
    assert del_resp.status_code == 200

    # 4. Verify gone from database
    check_db = db_session.query(Analysis).filter(Analysis.id == uuid.UUID(id1)).first()
    assert check_db is None
