from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRegister, UserResponse
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication & User Session"])



@router.post(
    "/google",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate via Google OAuth ID Token",
)
def google_auth(
    google_in: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    return service.google_login_user(google_in)



@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
)
def register_user(
    user_in: UserRegister,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    return service.register_user(user_in)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT token",
)
def login_user(
    login_in: LoginRequest,
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    return service.login_user(login_in)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user profile",
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)
