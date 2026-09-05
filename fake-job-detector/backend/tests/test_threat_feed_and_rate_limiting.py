"""Tests for Threat Feed Synchronization and Global Rate Limiting."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security_middleware import InMemoryRateLimiterMiddleware
from app.services.threat_feed_sync_service import ThreatFeedSyncService


@pytest.fixture
def client():
    return TestClient(app)


def test_threat_feed_sync_service():
    """Verify threat feed sync status and execution."""
    status = ThreatFeedSyncService.get_sync_status()
    assert status["status"] == "HEALTHY"
    assert status["advisories_indexed"] >= 5
    assert status["voip_carriers_tracked"] >= 4
    assert status["red_flag_heuristics"] == 25

    sync_result = ThreatFeedSyncService.trigger_threat_feed_sync(force=True)
    assert sync_result["status"] == "HEALTHY"
    assert len(sync_result["sources_synced"]) >= 4



def test_threat_feed_sync_endpoints(client):
    """Test GET /api/v1/community/sync/status and POST /api/v1/community/sync/refresh."""
    resp_get = client.get("/api/v1/community/sync/status")
    assert resp_get.status_code == 200
    data = resp_get.json()
    assert data["status"] == "HEALTHY"
    assert "sources_synced" in data

    resp_post = client.post("/api/v1/community/sync/refresh")
    assert resp_post.status_code == 200
    post_data = resp_post.json()
    assert post_data["status"] == "success"
    assert "details" in post_data


def test_rate_limiter_allows_normal_traffic(client):
    """Verify standard requests within limits are allowed without 429."""
    InMemoryRateLimiterMiddleware.reset()
    for _ in range(5):
        resp = client.get("/api/v1/educational/red-flags")
        assert resp.status_code == 200
