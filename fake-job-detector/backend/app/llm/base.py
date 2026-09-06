"""SentinelJob AI — LLM Provider Abstract Base Interface (Phase 22).

Defines the pluggable LLM provider contract for Google Gemini, OpenAI,
Anthropic Claude, and Local Ollama/vLLM endpoints.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.llm.schemas import LLMStructuredSynthesis, LLMTelemetryRecord


class BaseLLMProvider(ABC):
    """Abstract interface for all SentinelJob AI LLM providers."""

    def __init__(self, model_name: str, api_key: Optional[str] = None, timeout_seconds: float = 12.0):
        self.model_name = model_name
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'gemini', 'openai', 'anthropic', 'local')."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if mandatory credentials or connection settings are satisfied."""
        pass

    @abstractmethod
    async def synthesize(self, prompt: str) -> LLMStructuredSynthesis:
        """Execute structured JSON inference and return validated Pydantic synthesis."""
        pass
