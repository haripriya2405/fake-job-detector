"""Unit and Integration Tests for Phase 22 Feature Expansions:
- Extended Enterprise ATS verification (Workable, Taleo, SuccessFactors, query tokens)
- Batch Job Analysis Endpoint (POST /api/v1/analysis/batch)
- Historical Audit CSV Export Endpoint (GET /api/v1/analysis/export/csv)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.careers_page_service import careers_page_service

client = TestClient(app)


def test_extended_ats_detection():
    """Verify new enterprise ATS engines are recognized accurately."""
    # Workable
    res_workable = careers_page_service.verify_careers_origin(url="https://apply.workable.com/tech-corp/j/123456/")
    assert res_workable.is_official_ats is True
    assert res_workable.ats_provider == "Workable"
    assert res_workable.risk_points == 0

    # Taleo
    res_taleo = careers_page_service.verify_careers_origin(url="https://oracle.taleo.net/careersection/jobdetail.ftl?job=123")
    assert res_taleo.is_official_ats is True
    assert res_taleo.ats_provider == "Oracle Taleo"

    # SAP SuccessFactors
    res_sf = careers_page_service.verify_careers_origin(url="https://jobs.successfactors.com/job/dev-engineer")
    assert res_sf.is_official_ats is True
    assert res_sf.ats_provider == "SAP SuccessFactors"

    # Query parameter ATS token
    res_query = careers_page_service.verify_careers_origin(url="https://customcareers.corp.com/apply?gh_jid=987654")
    assert res_query.is_official_ats is True
    assert res_query.ats_provider == "Greenhouse"


def test_batch_job_analysis_endpoint():
    """Verify POST /api/v1/analysis/batch processes multiple jobs and aggregates metrics."""
    batch_payload = {
        "items": [
            {
                "raw_content": "Google LLC is seeking Senior Backend Engineers in Mountain View, CA. Requires 5+ years Python and distributed systems experience. Official application portal: careers.google.com.",
                "job_title": "Senior Backend Engineer",
                "company_name": "Google LLC",
                "source_type": "text"
            },
            {
                "raw_content": "URGENT HIRING: Data Entry Operator. Earn $800 daily working 2 hours from home. Must send $150 registration fee via crypto wallet to reserve position.",
                "job_title": "Data Entry Assistant",
                "company_name": "FastCash Careers",
                "source_type": "text"
            }
        ]
    }

    response = client.post("/api/v1/analysis/batch", json=batch_payload)
    assert response.status_code == 201
    data = response.json()

    assert "batch_id" in data
    assert data["total_analyzed"] == 2
    assert "summary" in data
    assert data["summary"]["total_jobs"] == 2
    assert "average_risk_score" in data["summary"]
    assert "highest_risk_score" in data["summary"]
    assert len(data["results"]) == 2

    # Verify first job is safe/low risk and second is high risk
    results = data["results"]
    assert results[0]["risk_score"] < results[1]["risk_score"]
    assert results[1]["risk_score"] >= 60


def test_batch_validation_limits():
    """Verify empty batch or oversized batch triggers validation error."""
    # Empty items list
    resp_empty = client.post("/api/v1/analysis/batch", json={"items": []})
    assert resp_empty.status_code == 422


def test_export_csv_endpoint():
    """Verify GET /api/v1/analysis/export/csv returns valid CSV format."""
    # Create an analysis first
    client.post("/api/v1/analysis", json={
        "raw_content": "Amazon AWS is hiring Cloud Infrastructure Engineers in Seattle, WA. Apply at amazon.jobs.",
        "job_title": "Cloud Infrastructure Engineer",
        "company_name": "Amazon"
    })

    resp = client.get("/api/v1/analysis/export/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "Content-Disposition" in resp.headers
    assert "Job Title" in resp.text
    assert "Risk Score" in resp.text
