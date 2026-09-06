"""SentinelJob AI — LLM Intelligence Orchestration Package."""

from app.llm.base import BaseLLMProvider
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMBaseException,
    LLMConfigurationError,
    LLMOutputParsingError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm.prompts import SENTINELJOB_LLM_PROMPT_VERSION, build_forensic_synthesis_prompt
from app.llm.provider import get_llm_provider
from app.llm.schemas import (
    LLMStructuredSynthesis,
    LLMTelemetryRecord,
    LLMVerdictEnum,
    ScamArchetypeEnum,
    StructuredEvidenceItem,
)
from app.llm.service import LLMOrchestrationService, llm_service
from app.llm.telemetry import LLMTelemetryTracker, llm_telemetry_tracker

__all__ = [
    "BaseLLMProvider",
    "LLMBaseException",
    "LLMConfigurationError",
    "LLMTimeoutError",
    "LLMRateLimitError",
    "LLMAuthenticationError",
    "LLMOutputParsingError",
    "LLMStructuredSynthesis",
    "LLMTelemetryRecord",
    "LLMVerdictEnum",
    "ScamArchetypeEnum",
    "StructuredEvidenceItem",
    "SENTINELJOB_LLM_PROMPT_VERSION",
    "build_forensic_synthesis_prompt",
    "get_llm_provider",
    "LLMOrchestrationService",
    "llm_service",
    "LLMTelemetryTracker",
    "llm_telemetry_tracker",
]
