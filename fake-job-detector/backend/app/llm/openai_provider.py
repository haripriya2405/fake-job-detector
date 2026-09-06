"""SentinelJob AI — OpenAI LLM Provider Implementation.

Supports GPT-4o, GPT-4o-mini with JSON schema output modes.
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


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI GPT-4o / GPT-4o-mini provider."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        timeout_seconds: float = 12.0,
    ):
        key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        super().__init__(model_name=model_name, api_key=key, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "openai"

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 8)

    async def synthesize(self, prompt: str) -> LLMStructuredSynthesis:
        if not self.is_configured():
            raise LLMConfigurationError("OpenAI API key is not configured in environment variables.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a cyber fraud forensic investigator. Output strictly valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(url, headers=headers, json=payload)

                if resp.status_code == 429:
                    raise LLMRateLimitError("OpenAI API rate limit exceeded (429).")
                elif resp.status_code in (401, 403):
                    raise LLMAuthenticationError(f"OpenAI authentication failed ({resp.status_code}).")
                elif resp.status_code != 200:
                    raise LLMOutputParsingError(f"OpenAI API returned error: {resp.status_code} - {resp.text[:200]}")

                data = resp.json()
                text_content = data["choices"][0]["message"]["content"]
                parsed_json = json.loads(text_content)
                return LLMStructuredSynthesis.model_validate(parsed_json)

        except httpx.TimeoutException as te:
            raise LLMTimeoutError(f"OpenAI request timed out after {self.timeout_seconds}s: {te}")
        except json.JSONDecodeError as je:
            raise LLMOutputParsingError(f"Failed to decode JSON from OpenAI output: {je}")
        except Exception as e:
            if isinstance(e, (LLMRateLimitError, LLMAuthenticationError, LLMTimeoutError, LLMOutputParsingError)):
                raise e
            raise LLMOutputParsingError(f"Unexpected error during OpenAI synthesis: {e}")
