import uuid
import pytest
from app.core.config import settings
from app.core.security import create_access_token
from app.core.security_middleware import InMemoryRateLimiterMiddleware


# ============================================================================
# 1. SECURITY HEADERS VERIFICATION
# ============================================================================

def test_security_headers_applied_to_responses(client):
    """Verify production security headers are attached to all API responses."""
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "geolocation=()" in headers.get("Permissions-Policy", "")
    assert "default-src" in headers.get("Content-Security-Policy", "")


# ============================================================================
# 2. REQUEST CORRELATION ID VERIFICATION
# ============================================================================

def test_request_correlation_id_generation_and_propagation(client):
    """Verify X-Request-ID correlation headers are generated and client IDs are preserved."""
    # Test 1: Generated ID
    resp1 = client.get("/health")
    assert resp1.status_code == 200
    req_id_1 = resp1.headers.get("X-Request-ID")
    assert req_id_1 is not None
    assert len(req_id_1) > 10

    # Test 2: Custom Client-provided ID preserved
    custom_id = f"sentinel-test-{uuid.uuid4().hex[:12]}"
    resp2 = client.get("/health", headers={"X-Request-ID": custom_id})
    assert resp2.status_code == 200
    assert resp2.headers.get("X-Request-ID") == custom_id


# ============================================================================
# 3. HEALTH & READINESS PROBES VERIFICATION
# ============================================================================

def test_readiness_probe_endpoints(client):
    """Verify both root /ready and /api/v1/ready return operational status."""
    # Root /ready
    r1 = client.get("/ready")
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1.get("status") == "ready"
    assert data1.get("database") == "operational"

    # API v1 /api/v1/ready
    r2 = client.get("/api/v1/ready")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2.get("status") == "ready"


# ============================================================================
# 4. RATE LIMITING MIDDLEWARE VERIFICATION
# ============================================================================

def test_rate_limiting_enforcement_on_auth(client):
    """Verify in-memory sliding-window rate limiter triggers 429 on excessive requests."""
    # Temporarily set a very small limit and enable force test flag
    orig_limit = settings.RATE_LIMIT_AUTH_PER_MINUTE
    settings.RATE_LIMIT_AUTH_PER_MINUTE = 3
    settings.RATE_LIMIT_ENABLED = True
    settings.TESTING_RATE_LIMIT = True
    InMemoryRateLimiterMiddleware.reset()

    try:
        results = []
        for i in range(5):
            res = client.post(
                "/api/v1/auth/login",
                json={"email": f"test{i}@sentinel.ai", "password": "wrongpassword123"},
            )
            results.append(res.status_code)

        # First 3 should fail authentication (401), subsequent should be rate limited (429)
        assert 429 in results
        last_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "blocked@sentinel.ai", "password": "wrongpassword123"},
        )
        assert last_resp.status_code == 429
        assert last_resp.headers.get("Retry-After") is not None
        assert "Rate limit exceeded" in last_resp.json().get("detail", "") or "Too many requests" in last_resp.json().get("detail", "")
    finally:
        settings.RATE_LIMIT_AUTH_PER_MINUTE = orig_limit
        settings.TESTING_RATE_LIMIT = False
        InMemoryRateLimiterMiddleware.reset()


# ============================================================================
# 5. ERROR SANITIZATION & EXCEPTION MASKING
# ============================================================================

def test_error_response_sanitization(client):
    """Verify error responses are structured and do not expose stack traces or secrets."""
    # Test 404
    r_404 = client.get(f"/api/v1/analysis/{uuid.uuid4()}")
    assert r_404.status_code == 404
    data_404 = r_404.json()
    assert "detail" in data_404
    assert "request_id" in data_404
    assert "Traceback" not in str(data_404)
    assert "password" not in str(data_404).lower()

    # Test 422 validation
    r_422 = client.post("/api/v1/analysis", json={"raw_content": "short"})
    assert r_422.status_code == 422
    data_422 = r_422.json()
    assert "detail" in data_422
    assert "request_id" in data_422


# ============================================================================
# 6. CONFIGURATION & POOLING INTEGRITY
# ============================================================================

def test_database_pool_configuration_integrity():
    """Verify connection pooling parameters are loaded and configured."""
    assert settings.DB_POOL_SIZE >= 5
    assert settings.DB_MAX_OVERFLOW >= 5
    assert settings.DB_POOL_TIMEOUT >= 10
    assert settings.DB_POOL_RECYCLE >= 300


def test_cors_configuration_production_standards():
    """Verify CORS origins list is non-empty and properly parsed."""
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) > 0
    # Invariant: Never allow '*' as the only origin in production
    if settings.ENVIRONMENT == "production":
        assert "*" not in settings.CORS_ORIGINS
