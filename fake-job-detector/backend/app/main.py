from contextlib import asynccontextmanager
import uuid
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.api.v1.health import health_check, readiness_check
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.exceptions import AppError
from app.core.logging import logger, setup_logging
from app.core.security_middleware import (
    InMemoryRateLimiterMiddleware,
    RequestCorrelationMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.base import Base
from app.db.session import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup structured logging
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} in [{settings.ENVIRONMENT}] mode...")
    
    # Ensure tables exist in database
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema synchronized successfully.")

        # Seed default demo security analyst users if not exist
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.core.security import hash_password

        with SessionLocal() as db_session:
            demo_users = [
                ("demo@sentinel.ai", "Demo Security Analyst", "password123", "analyst"),
                ("security.analyst@sentinel.ai", "Alex Vance", "password123", "analyst"),
                ("analyst@company.com", "Google Workspace Analyst", "google-oauth-token", "analyst"),
            ]
            for email, name, pwd, role in demo_users:
                existing = db_session.query(User).filter(User.email == email).first()
                if not existing:
                    user_obj = User(
                        id=uuid.uuid4(),
                        email=email,
                        full_name=name,
                        hashed_password=hash_password(pwd),
                        role=role,
                        is_active=True,
                    )
                    db_session.add(user_obj)
            db_session.commit()
            logger.info("Default security analyst demo accounts initialized.")
    except Exception as e:
        logger.warning(f"Database schema auto-creation/seeding notice: {e}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="SentinelJob AI — Fraud Detection API",
        description=(
            "Explainable AI-powered backend API for detecting fake job and internship postings, "
            "scam offer letters, and fraudulent recruitment channels."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Middleware execution order:
    # 1. Security Headers (outermost on response)
    # 2. Rate Limiting (blocks abusive traffic early)
    # 3. Request Correlation ID & Structured Access Logging
    # 4. CORS Middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(InMemoryRateLimiterMiddleware)
    app.add_middleware(RequestCorrelationMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global Exception Handlers with correlation ID injection & error sanitization
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        headers = dict(exc.headers or {})
        headers["X-Request-ID"] = req_id
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "type": exc.__class__.__name__,
                "request_id": req_id,
            },
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation failed",
                "errors": exc.errors(),
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        logger.exception(f"[{req_id}] Unhandled internal exception on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error occurred",
                "type": "InternalServerError",
                "request_id": req_id,
            },
            headers={"X-Request-ID": req_id},
        )

    # Root Health & Readiness endpoints
    @app.get("/health", tags=["Health & Telemetry"], summary="Root liveness probe")
    def root_health(db: Session = Depends(get_db)):
        return health_check(db=db)

    @app.get("/ready", tags=["Health & Telemetry"], summary="Root readiness probe")
    def root_ready(response: Response, db: Session = Depends(get_db)):
        return readiness_check(response=response, db=db)

    # Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_app()
