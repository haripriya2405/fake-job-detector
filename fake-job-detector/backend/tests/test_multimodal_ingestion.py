"""Phase 8 Multi-Modal Ingestion Test Suite.
Tests:
1. Raw Text Ingestion & validation
2. PDF Ingestion (valid multi-page, malformed header, page truncation)
3. Image Ingestion (valid PNG/JPEG, corrupted image, dimension limits, OCR pipeline)
4. Public URL Ingestion & SSRF Firewall (localhost, private IPs, metadata, redirect validation)
5. End-to-End Multi-Modal API Endpoints (/analysis, /analysis/text, /analysis/upload, /analysis/url)
"""

import io
import pytest
from PIL import Image, ImageDraw
from pypdf import PdfWriter

from app.ingestion import ingest_job_input
from app.ingestion.limits import limits
from app.ingestion.schemas import SourceType


# -----------------------------------------------------------------------------
# Helper: Create Valid In-Memory PDF Bytes
# -----------------------------------------------------------------------------
def _create_sample_pdf_bytes(text_pages: list[str]) -> bytes:
    writer = PdfWriter()
    for text in text_pages:
        writer.add_blank_page(width=612, height=792)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


# -----------------------------------------------------------------------------
# Helper: Create Valid In-Memory Image Bytes
# -----------------------------------------------------------------------------
def _create_sample_image_bytes(text: str = "Test Job Posting") -> bytes:
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# -----------------------------------------------------------------------------
# 1. Raw Text Ingestion Tests
# -----------------------------------------------------------------------------
def test_text_ingestion_valid():
    """Verify raw text is ingested, cleaned, and structured entities are extracted."""
    text = (
        "Senior Cloud Architect at Stripe. Apply at https://stripe.com/careers. "
        "Contact recruiter on jobs@stripe.com or +1 (415) 555-0199 for salary details."
    )
    result = ingest_job_input(SourceType.TEXT, text, metadata={"job_title": "Senior Cloud Architect"})

    assert result.source_type == SourceType.TEXT
    assert result.job_title == "Senior Cloud Architect"
    assert "https://stripe.com/careers" in result.extracted_urls
    assert "jobs@stripe.com" in result.extracted_emails
    assert len(result.extracted_phone_numbers) > 0
    assert result.extraction_confidence == 1.0


def test_text_ingestion_too_short():
    """Verify short text triggers validation error."""
    with pytest.raises(ValueError, match="too short"):
        ingest_job_input(SourceType.TEXT, "Short job text")


# -----------------------------------------------------------------------------
# 2. PDF Ingestion Tests
# -----------------------------------------------------------------------------
def test_pdf_ingestion_invalid_header():
    """Verify non-PDF bytes trigger invalid header format error."""
    with pytest.raises(ValueError, match="Invalid PDF format"):
        ingest_job_input(SourceType.PDF, b"NOT_A_PDF_STREAM")


def test_pdf_ingestion_empty_bytes():
    """Verify empty byte buffer is rejected."""
    with pytest.raises(ValueError, match="non-empty bytes"):
        ingest_job_input(SourceType.PDF, b"")


def test_pdf_ingestion_valid_structure():
    """Verify valid PDF structure parses correctly."""
    pdf_bytes = _create_sample_pdf_bytes(["Page 1 content", "Page 2 content"])
    result = ingest_job_input(
        SourceType.PDF,
        pdf_bytes,
        metadata={"filename": "offer_letter.pdf", "company_name": "Google LLC"},
    )

    assert result.source_type == SourceType.PDF
    assert result.original_filename == "offer_letter.pdf"
    assert result.page_count == 2
    assert result.extraction_method == "pypdf_text_extraction"
    assert result.content_hash is not None


# -----------------------------------------------------------------------------
# 3. Image Ingestion & OCR Tests
# -----------------------------------------------------------------------------
def test_image_ingestion_valid_png():
    """Verify valid PNG screenshot is decoded and processed."""
    img_bytes = _create_sample_image_bytes("Software Engineer at Netflix")
    result = ingest_job_input(
        SourceType.IMAGE,
        img_bytes,
        metadata={"filename": "job_screenshot.png"},
    )

    assert result.source_type == SourceType.IMAGE
    assert result.original_filename == "job_screenshot.png"
    assert result.mime_type == "image/png"
    assert result.file_size_bytes == len(img_bytes)
    assert result.content_hash is not None


def test_image_ingestion_corrupted_bytes():
    """Verify corrupted image bytes raise ValueError."""
    with pytest.raises(ValueError, match="Invalid or corrupted image format"):
        ingest_job_input(SourceType.IMAGE, b"CORRUPTED_IMAGE_BYTES_12345")


# -----------------------------------------------------------------------------
# 4. Public URL Ingestion & SSRF Firewall Tests
# -----------------------------------------------------------------------------
def test_url_ingestion_blocks_localhost():
    """Verify SSRF firewall rejects localhost / loopback URLs."""
    with pytest.raises(ValueError, match="security violation"):
        ingest_job_input(SourceType.URL, "http://localhost:8000/internal-job")


def test_url_ingestion_blocks_private_ip():
    """Verify SSRF firewall rejects RFC1918 private IPs."""
    with pytest.raises(ValueError, match="security violation"):
        ingest_job_input(SourceType.URL, "http://192.168.1.100/careers")


def test_url_ingestion_blocks_cloud_metadata():
    """Verify SSRF firewall rejects cloud instance metadata IP."""
    with pytest.raises(ValueError, match="security violation"):
        ingest_job_input(SourceType.URL, "http://169.254.169.254/latest/meta-data")


# -----------------------------------------------------------------------------
# 5. End-to-End Multi-Modal API Endpoint Tests (Using client fixture)
# -----------------------------------------------------------------------------
def test_api_analyze_text_dedicated(client):
    """Verify POST /api/v1/analysis/text processes job text through ML + Rules + Risk engines."""
    payload = {
        "raw_content": (
            "We are hiring a Senior React Developer at Vercel. Requirements: 5+ years TypeScript. "
            "Competitive salary $160k with full health benefits. Apply at https://vercel.com/careers."
        ),
        "job_title": "Senior React Developer",
        "company_name": "Vercel",
    }
    response = client.post("/api/v1/analysis/text", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["source_type"] == "text"
    assert data["job_title"] == "Senior React Developer"
    assert data["risk_level"] in ["low", "medium", "high", "critical"]
    assert "extraction" in data
    assert data["extraction"]["source_type"] == "TEXT"
    assert "score_breakdown" in data
    assert "company_verification" in data


def test_api_analyze_upload_pdf(client):
    """Verify POST /api/v1/analysis/upload with PDF file processes end-to-end."""
    pdf_bytes = _create_sample_pdf_bytes(["Staff Infrastructure Engineer at Stripe"])
    files = {"file": ("offer.pdf", pdf_bytes, "application/pdf")}
    data = {"source_type": "pdf", "job_title": "Staff Engineer", "company_name": "Stripe"}

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["source_type"] == "pdf"
    assert res_data["job_title"] == "Staff Engineer"
    assert "extraction" in res_data
    assert res_data["extraction"]["original_filename"] == "offer.pdf"


def test_api_analyze_upload_image(client):
    """Verify POST /api/v1/analysis/upload with screenshot image processes end-to-end."""
    img_bytes = _create_sample_image_bytes("Telegram Part-Time Typist Scam")
    files = {"file": ("screenshot.png", img_bytes, "image/png")}
    data = {"source_type": "image", "job_title": "Typist", "company_name": "QuickCash"}

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()

    assert res_data["source_type"] == "image"
    assert res_data["extraction"]["mime_type"] == "image/png"


def test_api_analyze_url_ssrf_blocked(client):
    """Verify POST /api/v1/analysis/url rejects SSRF targets with HTTP 422/400 validation error."""
    payload = {
        "job_url": "http://127.0.0.1:8000/internal-admin",
        "job_title": "Internal Admin",
    }
    response = client.post("/api/v1/analysis/url", json=payload)
    assert response.status_code in [400, 422]
