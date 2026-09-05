"""Tests for 25 Red Flags Matrix and Interactive Scam Simulator."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.educational_service import EducationalService, RED_FLAGS_25, SIMULATOR_SCENARIOS


@pytest.fixture
def client():
    return TestClient(app)


def test_25_red_flags_integrity():
    """Verify that all 25 Red Flags are present with required attributes."""
    red_flags = EducationalService.get_red_flags()
    assert len(red_flags) == 25
    
    categories = set(rf["category"] for rf in red_flags)
    assert len(categories) >= 4  # At least 4 distinct categories
    
    for rf in red_flags:
        assert "id" in rf
        assert "number" in rf
        assert "title" in rf
        assert "severity" in rf
        assert rf["severity"] in ["CRITICAL", "HIGH", "MEDIUM"]
        assert len(rf["indicators"]) >= 2
        assert len(rf["real_scam_snippet"]) > 10
        assert len(rf["safety_protocol"]) > 10


def test_red_flags_filtering():
    """Verify filtering by category, search, and severity."""
    financial = EducationalService.get_red_flags(category="Financial")
    assert len(financial) > 0
    assert all("Financial" in rf["category"] for rf in financial)

    critical = EducationalService.get_red_flags(severity="CRITICAL")
    assert len(critical) > 0
    assert all(rf["severity"] == "CRITICAL" for rf in critical)

    search_check = EducationalService.get_red_flags(search="check")
    assert len(search_check) > 0


def test_get_red_flags_api(client):
    """Test API endpoint for retrieving red flags."""
    resp = client.get("/api/v1/educational/red-flags")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_red_flags"] == 25
    assert data["count"] == 25
    assert len(data["red_flags"]) == 25


def test_simulator_scenarios_api(client):
    """Test API endpoint for retrieving simulator scenarios."""
    resp = client.get("/api/v1/educational/simulator/scenarios")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 6
    for s in data["scenarios"]:
        # Verify answers are hidden in scenario list
        assert "is_scam" not in s
        assert "verdict" not in s
        assert "clue_phrases" not in s
        assert "title" in s
        assert "body" in s


def test_simulator_evaluation_scam_correct(client):
    """Test evaluating a correct scam guess."""
    payload = {
        "scenario_id": "sim-01",
        "user_choice_is_scam": True,
        "user_flagged_clues": ["sarah.hr.recruiter.google@gmail.com", "Telegram"]
    }
    resp = client.post("/api/v1/educational/simulator/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is True
    assert data["actual_verdict"] == "SCAM"
    assert data["total_xp"] >= 100
    assert len(data["red_flags"]) > 0


def test_simulator_evaluation_legitimate_correct(client):
    """Test evaluating a correct legitimate scenario guess."""
    payload = {
        "scenario_id": "sim-03",
        "user_choice_is_scam": False,
        "user_flagged_clues": []
    }
    resp = client.post("/api/v1/educational/simulator/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is True
    assert data["actual_verdict"] == "LEGITIMATE"
    assert data["actual_is_scam"] is False


def test_simulator_evaluation_incorrect(client):
    """Test evaluating an incorrect guess."""
    payload = {
        "scenario_id": "sim-01",
        "user_choice_is_scam": False,  # Wrong guess
        "user_flagged_clues": []
    }
    resp = client.post("/api/v1/educational/simulator/evaluate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_correct"] is False
    assert data["actual_verdict"] == "SCAM"
    assert data["base_xp"] == 25  # Consolation XP
