"""SentinelJob AI — Google Gemini LLM Provider Implementation.

Leverages Gemini 1.5 Flash with native JSON mode and low temperature.
"""

import json
import logging
import os
from typing import Optional
import httpx

from app.llm.base import BaseLLMProvider
from app.llm.exceptions import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMOutputParsingError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from app.llm.schemas import LLMStructuredSynthesis

logger = logging.getLogger(__name__)


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini 1.5 Flash / Pro provider."""

    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        api_key: Optional[str] = None,
        timeout_seconds: float = 12.0,
    ):
        key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        super().__init__(model_name=model_name, api_key=key, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "gemini"

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 8)

    async def synthesize(self, prompt: str) -> LLMStructuredSynthesis:
        if not self.is_configured():
            raise LLMConfigurationError("Gemini API key is not configured in environment variables.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(url, json=payload)

                if resp.status_code == 429:
                    raise LLMRateLimitError("Gemini API rate limit exceeded (429).")
                elif resp.status_code in (401, 403):
                    raise LLMAuthenticationError(f"Gemini authentication failed ({resp.status_code}).")
                elif resp.status_code != 200:
                    raise LLMOutputParsingError(f"Gemini API returned unexpected HTTP status: {resp.status_code} - {resp.text[:200]}")

                data = resp.json()
                text_content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed_json = json.loads(text_content)
                return LLMStructuredSynthesis.model_validate(parsed_json)

        except httpx.TimeoutException as te:
            raise LLMTimeoutError(f"Gemini API request timed out after {self.timeout_seconds}s: {te}")
        except json.JSONDecodeError as je:
            raise LLMOutputParsingError(f"Failed to decode JSON from Gemini output: {je}")
        except Exception as e:
            if isinstance(e, (LLMRateLimitError, LLMAuthenticationError, LLMTimeoutError, LLMOutputParsingError)):
                raise e
            raise LLMOutputParsingError(f"Unexpected error during Gemini synthesis: {e}")
