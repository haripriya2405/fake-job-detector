"""SentinelJob AI — LLM Provider Factory.

Instantiates configured LLM providers based on environment variables or explicit requests.
"""

import os
from typing import Optional

from app.llm.anthropic_provider import AnthropicLLMProvider
from app.llm.base import BaseLLMProvider
from app.llm.gemini_provider import GeminiLLMProvider
from app.llm.local_provider import LocalLLMProvider
from app.llm.openai_provider import OpenAILLMProvider


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
) -> BaseLLMProvider:
    """Factory returning configured LLM provider instance."""
    p_name = (provider_name or os.getenv("LLM_PROVIDER") or "gemini").lower().strip()
    m_name = model_name or os.getenv("LLM_MODEL")

    if p_name == "openai":
        return OpenAILLMProvider(model_name=m_name or "gpt-4o-mini")
    elif p_name == "anthropic":
        return AnthropicLLMProvider(model_name=m_name or "claude-3-5-sonnet-20241022")
    elif p_name in ("local", "ollama", "vllm"):
        return LocalLLMProvider(model_name=m_name or "llama3.2:latest")
    else:
        # Default to Google Gemini 1.5 Flash
        return GeminiLLMProvider(model_name=m_name or "gemini-1.5-flash")
