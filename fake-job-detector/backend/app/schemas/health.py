from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    environment: str = "development"
    database: str = "connected"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    system_telemetry: Optional[Dict[str, str]] = None
