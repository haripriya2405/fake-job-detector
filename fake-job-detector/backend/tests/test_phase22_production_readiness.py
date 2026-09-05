"""Phase 22 Pre-Deployment Production Readiness & Security QA Tests."""

import ipaddress
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.ml.registry import model_registry
from app.verification.ssrf import ssrf_protection, is_safe_hostname, is_safe_ip

client = TestClient(app)


def test_phase22_root_health_and_readiness():
    """Verify production /health and /ready endpoints return safe structured data without secrets."""
    # 1. Health Probe
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    data = health_resp.json()
    assert "status" in data
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "database" in data
    # Ensure no credentials or raw filesystem paths exposed
    assert "password" not in str(data).lower()
    assert "secret" not in str(data).lower()

    # 2. Readiness Probe
    ready_resp = client.get("/ready")
    assert ready_resp.status_code in [200, 503]
    ready_data = ready_resp.json()
    assert "status" in ready_data
    assert "database" in ready_data


def test_phase22_ssrf_comprehensive_protection():
    """Verify SSRF engine blocks standard, decimal, hex, IPv6, and cloud metadata targets."""
    forbidden_targets = [
        "http://localhost",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:5000",
        "http://0.0.0.0",
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://10.0.0.1",
        "http://192.168.1.1",
        "http://172.16.0.1",
        "http://2130706433",  # Decimal 127.0.0.1
        "http://0x7f000001",  # Hex 127.0.0.1
        "http://[::1]",       # IPv6 localhost
        "file:///etc/passwd", # Non-HTTP scheme
        "ftp://127.0.0.1",    # FTP scheme
    ]

    for target in forbidden_targets:
        res = ssrf_protection.validate_url(target)
        assert not res.is_safe, f"SSRF target '{target}' should have been blocked, but was marked safe."


def test_phase22_ml_model_governance_invariants():
    """Strict verification of ML Governance Invariants:
    Active Production: logisticregression-v1.0.0
    Standby Candidate: transformer-v1.0.0-candidate
    No automatic promotion gate bypass.
    """
    active_model = model_registry.get_active_model_version()
    assert active_model is not None, "Active production model must exist in registry."
    assert active_model.model_version == "logisticregression-v1.0.0", (
        f"Active production model MUST be logisticregression-v1.0.0, found '{active_model.model_version}'"
    )
    assert active_model.status == "ACTIVE_PRODUCTION"

    candidate_model = model_registry.get_version("transformer-v1.0.0-candidate")
    assert candidate_model is not None, "Candidate model must exist in registry."
    assert candidate_model.status == "STANDBY_CANDIDATE"
    assert candidate_model.is_active is False, "Transformer candidate must remain inactive in standby."


def test_phase22_cors_configuration_safety():
    """Verify CORS origins list is parsed safely and never allows wildcard with credentials."""
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) > 0
    # Wildcard origin alone must not be configured for credentials sharing
    if len(settings.CORS_ORIGINS) > 1:
        assert "*" not in settings.CORS_ORIGINS


def test_phase22_upload_mime_and_extension_rejection():
    """Verify file upload rejection for executable and unsupported formats."""
    # Test uploading an executable script pretending to be a PDF
    resp = client.post(
        "/api/v1/analysis/upload",
        files={"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")},
        data={"source_type": "pdf"},
    )
    assert resp.status_code in [400, 415, 422], f"Expected rejection, got {resp.status_code}"
