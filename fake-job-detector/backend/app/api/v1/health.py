from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health & Telemetry"])


@router.get("/health", response_model=HealthResponse, summary="Liveness Probe")
def health_check(db: Session = Depends(get_db)):
    """Liveness probe verifying API application availability."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "degraded"

    return HealthResponse(
        status="healthy" if db_status == "connected" else "degraded",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        database=db_status,
        timestamp=datetime.now(timezone.utc),
        system_telemetry={
            "engine": "FastAPI 0.115+",
            "database_driver": "SQLAlchemy 2.x",
            "phase": "Phase 18 Production Hardening",
        },
    )


@router.get("/ready", summary="Readiness Probe")
def readiness_check(response: Response, db: Session = Depends(get_db)):
    """Readiness probe verifying critical infrastructure dependencies (PostgreSQL database)."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "operational",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "database": "unavailable",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
