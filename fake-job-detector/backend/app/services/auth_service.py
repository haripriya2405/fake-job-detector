import secrets
import uuid
from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRegister, UserResponse

security_scheme = HTTPBearer(auto_error=False)


def verify_google_id_token(token: str) -> dict:
    """Verifies Google ID Token signature, issuer, audience, expiration, and email claims."""
    if not token or not isinstance(token, str):
        raise AuthenticationError(detail="Google ID token is required")

    try:
        target_audience = settings.GOOGLE_CLIENT_ID if settings.GOOGLE_CLIENT_ID else None
        request = google_requests.Request()
        
        # Verify token via Google OAuth2 library
        payload = google_id_token.verify_oauth2_token(
            token,
            request,
            audience=target_audience,
            clock_skew_in_seconds=10,
        )

        # Validate Issuer
        issuer = payload.get("iss", "")
        if issuer not in ["accounts.google.com", "https://accounts.google.com"]:
            raise AuthenticationError(detail="Invalid token issuer")

        # Validate Audience if configured
        if settings.GOOGLE_CLIENT_ID and payload.get("aud") != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationError(detail="Google Client ID audience mismatch")

        # Validate Email Claim
        email = payload.get("email")
        if not email:
            raise AuthenticationError(detail="Google token missing email claim")

        # Validate Email Verification Status
        email_verified = payload.get("email_verified")
        if email_verified is not True:
            raise AuthenticationError(detail="Google account email is not verified")

        return payload

    except ValueError as ve:
        raise AuthenticationError(detail=f"Invalid or expired Google OAuth token: {str(ve)}")
    except Exception as exc:
        if isinstance(exc, AuthenticationError):
            raise exc
        raise AuthenticationError(detail=f"Google token verification failed: {str(exc)}")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_in: UserRegister) -> TokenResponse:
        # Check if email is already taken
        existing_user = self.db.query(User).filter(User.email == user_in.email).first()
        if existing_user:
            raise ConflictError(detail="User with this email already exists")

        new_user = User(
            id=uuid.uuid4(),
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=hash_password(user_in.password),
            role=user_in.role or "user",
            is_active=True,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        token = create_access_token(
            subject=str(new_user.id),
            extra_claims={"email": new_user.email, "role": new_user.role},
        )
        return TokenResponse(
            token=token,
            token_type="bearer",
            user=UserResponse.model_validate(new_user),
        )

    def login_user(self, login_in: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.email == login_in.email).first()
        
        if not user:
            raise AuthenticationError(detail="Invalid email or password")

        if not verify_password(login_in.password, user.hashed_password):
            raise AuthenticationError(detail="Invalid email or password")

        if not user.is_active:
            raise AuthenticationError(detail="User account is deactivated")

        token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "role": user.role},
        )
        return TokenResponse(
            token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    def google_login_user(self, google_in: GoogleAuthRequest) -> TokenResponse:
        """Authenticate user via verified Google ID Token, auto-provisioning new accounts securely."""
        payload = verify_google_id_token(google_in.id_token)

        email = payload.get("email")
        name_claim = payload.get("name") or payload.get("given_name")
        if not name_claim:
            email_prefix = email.split("@")[0]
            name_claim = email_prefix.replace(".", " ").replace("_", " ").title()

        user = self.db.query(User).filter(User.email == email).first()

        if not user:
            # Auto-provision new user with secure high-entropy random password
            random_password = secrets.token_urlsafe(32)
            user = User(
                id=uuid.uuid4(),
                email=email,
                full_name=name_claim,
                hashed_password=hash_password(random_password),
                role="user",
                is_active=True,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        if not user.is_active:
            raise AuthenticationError(detail="User account is deactivated")

        token = create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email, "role": user.role},
        )
        return TokenResponse(
            token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )


    def get_user_by_id(self, user_id: uuid.UUID) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError(detail="User not found")
        return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Dependency to retrieve the authenticated user if Bearer token is provided."""
    if not credentials or not credentials.credentials:
        return None

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None

    try:
        user_uuid = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        return None

    user = db.query(User).filter(User.id == user_uuid).first()
    return user if user and user.is_active else None


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency requiring valid authentication."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError(detail="Authentication token required")

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise AuthenticationError(detail="Invalid or expired token")

    try:
        user_uuid = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise AuthenticationError(detail="Invalid token subject payload")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user or not user.is_active:
        raise AuthenticationError(detail="User not found or inactive")

    return user
