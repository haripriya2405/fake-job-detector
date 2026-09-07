import pytest
from app.verification.pdf_forensics import pdf_forensics_inspector

def test_pdf_forensics_inspector_instantiation():
    assert pdf_forensics_inspector is not None
    assert hasattr(pdf_forensics_inspector, "inspect_pdf")

def test_pdf_forensics_dummy_bytes():
    result = pdf_forensics_inspector.inspect_pdf(b"%PDF-1.4 dummy content", filename="test_offer.pdf")
    assert "filename" in result
    assert result["filename"] == "test_offer.pdf"
    assert "tamper_score" in result
    assert "authenticity_verdict" in result
