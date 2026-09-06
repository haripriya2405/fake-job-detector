"""SentinelJob AI — Anthropic Claude LLM Provider Implementation.

Supports Claude 3.5 Sonnet / Claude 3 Haiku for structured forensic synthesis.
"""

import json
import logging
import os
import re
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


class AnthropicLLMProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None,
        timeout_seconds: float = 14.0,
    ):
        key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("LLM_API_KEY")
        super().__init__(model_name=model_name, api_key=key, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 8)

    async def synthesize(self, prompt: str) -> LLMStructuredSynthesis:
        if not self.is_configured():
            raise LLMConfigurationError("Anthropic API key is not configured in environment variables.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "max_tokens": 1500,
            "temperature": 0.1,
            "system": "You are a cyber fraud forensic investigator. Output strictly valid JSON without any markdown surrounding text or preamble.",
            "messages": [
                {"role": "user", "content": f"Output STRICT raw JSON:\n{prompt}"},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(url, headers=headers, json=payload)

                if resp.status_code == 429:
                    raise LLMRateLimitError("Anthropic API rate limit exceeded (429).")
                elif resp.status_code in (401, 403):
                    raise LLMAuthenticationError(f"Anthropic authentication failed ({resp.status_code}).")
                elif resp.status_code != 200:
                    raise LLMOutputParsingError(f"Anthropic API returned error: {resp.status_code} - {resp.text[:200]}")

                data = resp.json()
                text_content = data["content"][0]["text"]

                # Extract JSON block if surrounded by markdown fences
                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text_content)
                if json_match:
                    text_content = json_match.group(1)

                parsed_json = json.loads(text_content.strip())
                return LLMStructuredSynthesis.model_validate(parsed_json)

        except httpx.TimeoutException as te:
            raise LLMTimeoutError(f"Anthropic request timed out after {self.timeout_seconds}s: {te}")
        except json.JSONDecodeError as je:
            raise LLMOutputParsingError(f"Failed to decode JSON from Anthropic output: {je}")
        except Exception as e:
            if isinstance(e, (LLMRateLimitError, LLMAuthenticationError, LLMTimeoutError, LLMOutputParsingError)):
                raise e
            raise LLMOutputParsingError(f"Unexpected error during Anthropic synthesis: {e}")
