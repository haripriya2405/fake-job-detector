from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class GoogleAuthRequest(BaseModel):
    id_token: str = Field(..., description="Google ID Token issued by Google Identity Services")


from app.schemas.user import UserResponse
TokenResponse.model_rebuild()
