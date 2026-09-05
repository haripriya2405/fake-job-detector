def test_user_registration_success(client):
    """Test POST /api/v1/auth/register creates user and returns token."""
    payload = {
        "email": "new.recruit@defense.gov",
        "password": "StrongPassword123!",
        "full_name": "Agent Hunter",
        "role": "analyst",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["full_name"] == payload["full_name"]
    assert "hashed_password" not in data["user"]


def test_user_registration_duplicate_email(client, test_user):
    """Test duplicate email registration returns 409 Conflict."""
    payload = {
        "email": test_user.email,
        "password": "AnotherPassword456!",
        "full_name": "Duplicate User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert "already exists" in data["detail"].lower()


def test_login_success(client, test_user):
    """Test POST /api/v1/auth/login with valid credentials."""
    payload = {
        "email": test_user.email,
        "password": "SecurePassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == test_user.email


def test_login_invalid_password(client, test_user):
    """Test POST /api/v1/auth/login with wrong password returns 401."""
    payload = {
        "email": test_user.email,
        "password": "WrongPassword999!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()


def test_get_me_authenticated(client, test_user):
    """Test GET /api/v1/auth/me with valid Authorization header."""
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "SecurePassword123!"},
    )
    token = login_res.json()["token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name


def test_get_me_unauthenticated(client):
    """Test GET /api/v1/auth/me without token returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_google_login_new_user(client, monkeypatch):
    """Test Google login auto-creates new user account on valid token."""
    from unittest.mock import MagicMock
    from app.services import auth_service

    mock_payload = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "email": "new.google.analyst@gmail.com",
        "email_verified": True,
        "name": "Sarah Connor",
        "sub": "google-sub-998877",
    }
    monkeypatch.setattr(auth_service.settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(auth_service.google_id_token, "verify_oauth2_token", MagicMock(return_value=mock_payload))

    response = client.post("/api/v1/auth/google", json={"id_token": "valid_google_id_token_sample"})
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "new.google.analyst@gmail.com"
    assert data["user"]["full_name"] == "Sarah Connor"


def test_google_login_existing_user(client, test_user, monkeypatch):
    """Test Google login authenticates pre-existing account by verified email."""
    from unittest.mock import MagicMock
    from app.services import auth_service

    mock_payload = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "email": test_user.email,
        "email_verified": True,
        "name": test_user.full_name,
        "sub": "google-sub-112233",
    }
    monkeypatch.setattr(auth_service.settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(auth_service.google_id_token, "verify_oauth2_token", MagicMock(return_value=mock_payload))

    response = client.post("/api/v1/auth/google", json={"id_token": "valid_google_id_token_existing"})
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == test_user.email


def test_google_login_invalid_token(client, monkeypatch):
    """Test Google login returns 401 when token verification fails."""
    from unittest.mock import MagicMock
    from app.services import auth_service

    monkeypatch.setattr(
        auth_service.google_id_token,
        "verify_oauth2_token",
        MagicMock(side_effect=ValueError("Invalid token signature")),
    )

    response = client.post("/api/v1/auth/google", json={"id_token": "invalid_signature_token"})
    assert response.status_code == 401
    assert "invalid or expired" in response.json()["detail"].lower()


def test_google_login_expired_token(client, monkeypatch):
    """Test Google login returns 401 when token is expired."""
    from unittest.mock import MagicMock
    from app.services import auth_service

    monkeypatch.setattr(
        auth_service.google_id_token,
        "verify_oauth2_token",
        MagicMock(side_effect=ValueError("Token has expired")),
    )

    response = client.post("/api/v1/auth/google", json={"id_token": "expired_token"})
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_google_login_wrong_audience(client, monkeypatch):
    """Test Google login returns 401 when token audience mismatches GOOGLE_CLIENT_ID."""
    from unittest.mock import MagicMock
    from app.services import auth_service
    from app.core.config import settings

    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "expected-client-id-123")
    mock_payload = {
        "iss": "https://accounts.google.com",
        "aud": "wrong-client-id-999",
        "email": "attacker@gmail.com",
        "email_verified": True,
        "name": "Wrong Audience User",
        "sub": "sub-111",
    }
    monkeypatch.setattr(auth_service.settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(auth_service.google_id_token, "verify_oauth2_token", MagicMock(return_value=mock_payload))

    response = client.post("/api/v1/auth/google", json={"id_token": "wrong_audience_token"})
    assert response.status_code == 401
    assert "audience mismatch" in response.json()["detail"].lower()


def test_google_login_unverified_email(client, monkeypatch):
    """Test Google login returns 401 when email_verified is False."""
    from unittest.mock import MagicMock
    from app.services import auth_service

    mock_payload = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "email": "unverified@gmail.com",
        "email_verified": False,
        "name": "Unverified User",
        "sub": "sub-222",
    }
    monkeypatch.setattr(auth_service.settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(auth_service.google_id_token, "verify_oauth2_token", MagicMock(return_value=mock_payload))

    response = client.post("/api/v1/auth/google", json={"id_token": "unverified_email_token"})
    assert response.status_code == 401
    assert "not verified" in response.json()["detail"].lower()


def test_google_login_jwt_protected_endpoint(client, monkeypatch):
    """Test JWT returned by Google login works seamlessly with protected endpoints (/auth/me)."""
    from unittest.mock import MagicMock
    from app.services import auth_service

    mock_payload = {
        "iss": "https://accounts.google.com",
        "aud": "test-client-id",
        "email": "protected.access@gmail.com",
        "email_verified": True,
        "name": "Protected Access User",
        "sub": "sub-333",
    }
    monkeypatch.setattr(auth_service.settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(auth_service.google_id_token, "verify_oauth2_token", MagicMock(return_value=mock_payload))

    # 1. Login via Google OAuth
    google_res = client.post("/api/v1/auth/google", json={"id_token": "valid_token_for_me"})
    assert google_res.status_code == 200
    token = google_res.json()["token"]

    # 2. Access /auth/me with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "protected.access@gmail.com"
    assert me_data["full_name"] == "Protected Access User"

