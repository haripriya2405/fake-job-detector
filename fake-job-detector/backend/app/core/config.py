import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APPLICATION_ENV: str = "production"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "SentinelJob AI Backend"
    API_V1_STR: str = "/api/v1"

    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # CORS & Network Origins
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    FRONTEND_URL: str = "http://localhost:5173"

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
        else:
            origins = [origin.strip() for origin in v if origin.strip()]

        # Security check: Never permit wildcard origins with credential sharing
        if "*" in origins and len(origins) > 1:
            origins = [o for o in origins if o != "*"]
        return origins

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fake_job_detector"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # JWT Authentication
    SECRET_KEY: str = "sentinel_jwt_secret_development_key_change_in_production_948f1029ba30dce4"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Rate Limiting Settings (Single-Instance in-memory protection)
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AUTH_PER_MINUTE: int = 15
    RATE_LIMIT_ANALYSIS_PER_MINUTE: int = 20

    # Multi-Modal Uploads
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_UPLOAD_EXTENSIONS: str = ".pdf,.png,.jpg,.jpeg,.webp"
    ALLOWED_UPLOAD_MIME_TYPES: str = "application/pdf,image/png,image/jpeg,image/webp"

    # Timeouts
    OCR_TIMEOUT_SECONDS: int = 10
    URL_FETCH_TIMEOUT_SECONDS: int = 8

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )


settings = Settings()
