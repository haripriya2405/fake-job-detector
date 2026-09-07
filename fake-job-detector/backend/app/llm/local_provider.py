"""SentinelJob AI — Local LLM Provider Implementation (Ollama / vLLM).

Supports local offline execution via OpenAI-compatible endpoints (e.g. Llama-3.2, Qwen2.5).
"""

import json
import logging
import os
import re
from typing import Optional
import httpx

from app.llm.base import BaseLLMProvider
from app.llm.exceptions import (
    LLMConfigurationError,
    LLMOutputParsingError,
    LLMTimeoutError,
)
from app.llm.schemas import LLMStructuredSynthesis

logger = logging.getLogger(__name__)


class LocalLLMProvider(BaseLLMProvider):
    """Local OpenAI-compatible LLM endpoint (Ollama / vLLM / LocalAI)."""

    def __init__(
        self,
        model_name: str = "qwen2.5:7b",
        endpoint_url: Optional[str] = None,
        timeout_seconds: float = 45.0,
    ):
        self.endpoint_url = endpoint_url or os.getenv("LOCAL_LLM_URL", "http://localhost:11434/v1/chat/completions")
        super().__init__(model_name=model_name, api_key=None, timeout_seconds=timeout_seconds)

    @property
    def provider_name(self) -> str:
        return "local"

    def is_configured(self) -> bool:
        return bool(self.endpoint_url and len(self.endpoint_url) > 5)

    async def synthesize(self, prompt: str) -> LLMStructuredSynthesis:
        if not self.is_configured():
            raise LLMConfigurationError("Local LLM endpoint URL is not configured.")

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a cyber fraud forensic investigator. Output strictly valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "format": "json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                resp = await client.post(self.endpoint_url, json=payload)

                if resp.status_code != 200:
                    raise LLMOutputParsingError(f"Local LLM returned status {resp.status_code}: {resp.text[:200]}")

                data = resp.json()
                text_content = data["choices"][0]["message"]["content"]

                json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text_content)
                if json_match:
                    text_content = json_match.group(1)

                parsed_json = json.loads(text_content.strip())
                return LLMStructuredSynthesis.model_validate(parsed_json)

        except httpx.TimeoutException as te:
            raise LLMTimeoutError(f"Local LLM request timed out after {self.timeout_seconds}s: {te}")
        except json.JSONDecodeError as je:
            raise LLMOutputParsingError(f"Failed to decode JSON from local LLM output: {je}")
        except Exception as e:
            if isinstance(e, (LLMTimeoutError, LLMOutputParsingError)):
                raise e
            raise LLMOutputParsingError(f"Unexpected error during Local LLM synthesis: {e}")
