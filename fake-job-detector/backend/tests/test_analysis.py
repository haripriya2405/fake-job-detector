import io


def test_create_text_analysis_success(client):
    """Test POST /api/v1/analysis creates record and processes risk evaluation."""
    payload = {
        "raw_content": "URGENT HIRING: Remote Assistant needed immediately. Send photo ID and cashier check details to hr@gmail.com on Telegram.",
        "job_title": "Remote Data Entry Assistant",
        "company_name": "Apex Global Logistics",
        "source_type": "text",
    }
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["job_title"] == payload["job_title"]
    assert data["company_name"] == payload["company_name"]
    assert data["analysis_engine"] is not None
    assert data["risk_level"] in ["low", "medium", "high", "critical", "pending", "evaluated"]
    assert "recommendations" in data


def test_create_text_analysis_invalid_short_content(client):
    """Test POST /api/v1/analysis with less than 20 characters returns 422."""
    payload = {
        "raw_content": "Too short",
        "job_title": "Fake Job",
    }
    response = client.post("/api/v1/analysis", json=payload)
    assert response.status_code == 422


def test_get_analysis_by_id(client):
    """Test GET /api/v1/analysis/:id retrieves created analysis."""
    create_res = client.post(
        "/api/v1/analysis",
        json={
            "raw_content": "We are seeking a senior software engineer with 5+ years experience in Python and PostgreSQL.",
            "job_title": "Senior Python Engineer",
            "company_name": "Stripe, Inc.",
        },
    )
    analysis_id = create_res.json()["id"]

    response = client.get(f"/api/v1/analysis/{analysis_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == analysis_id
    assert data["job_title"] == "Senior Python Engineer"


def test_get_analysis_not_found(client):
    """Test GET /api/v1/analysis/:id with non-existent UUID returns 404."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/v1/analysis/{fake_uuid}")
    assert response.status_code == 404


def test_analysis_history(client):
    """Test GET /api/v1/analysis/history lists records."""
    client.post(
        "/api/v1/analysis",
        json={
            "raw_content": "Legitimate job posting description for QA automation specialist in distributed infrastructure.",
            "job_title": "QA Automation Engineer",
        },
    )
    response = client.get("/api/v1/analysis/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_delete_analysis_record(client):
    """Test DELETE /api/v1/analysis/:id removes record."""
    create_res = client.post(
        "/api/v1/analysis",
        json={
            "raw_content": "Job posting to be deleted during automated unit testing verification.",
            "job_title": "Temporary Posting",
        },
    )
    analysis_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/analysis/{analysis_id}")
    assert del_res.status_code == 200

    # Verify 404 on subsequent get
    get_res = client.get(f"/api/v1/analysis/{analysis_id}")
    assert get_res.status_code == 404


def test_upload_pdf_analysis_success(client):
    """Test POST /api/v1/analysis/upload with valid PDF file."""
    fake_pdf = io.BytesIO(b"%PDF-1.4 Mock PDF content for employment contract verification test.")
    files = {"file": ("offer_letter.pdf", fake_pdf, "application/pdf")}
    data = {"source_type": "pdf", "job_title": "Offer Letter Document"}

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["source_type"] == "pdf"
    assert res_data["analysis_engine"] is not None


def test_upload_unsupported_file_type(client):
    """Test POST /api/v1/analysis/upload with unsupported file extension / mime type returns 400."""
    fake_exe = io.BytesIO(b"MZ executable binary payload")
    files = {"file": ("malicious_installer.exe", fake_exe, "application/x-msdownload")}
    data = {"source_type": "binary"}

    response = client.post("/api/v1/analysis/upload", files=files, data=data)
    assert response.status_code == 400
    assert "unsupported" in response.json()["detail"].lower()
