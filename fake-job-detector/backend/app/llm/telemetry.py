"""SentinelJob AI — LLM Inference Telemetry & Audit Logger.

Tracks LLM latency, token estimates, provider health, and fallback occurrences.
"""

from datetime import datetime, timezone
import logging
from typing import List
from app.llm.schemas import LLMTelemetryRecord

logger = logging.getLogger(__name__)

class LLMTelemetryTracker:
    """In-memory audit log and performance monitor for LLM calls."""

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._history: List[LLMTelemetryRecord] = []

    def record(self, record: LLMTelemetryRecord) -> None:
        self._history.append(record)
        if len(self._history) > self.max_history:
            self._history.pop(0)

        log_level = logging.WARNING if record.is_fallback else logging.INFO
        logger.log(
            log_level,
            f"[LLM-TELEMETRY] Provider: {record.provider} | Model: {record.model} | "
            f"Latency: {record.latency_ms:.2f}ms | Fallback: {record.is_fallback} | Status: {record.status}"
        )

    def get_recent_telemetry(self) -> List[LLMTelemetryRecord]:
        return list(self._history)


llm_telemetry_tracker = LLMTelemetryTracker()
