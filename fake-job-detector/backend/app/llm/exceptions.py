"""SentinelJob AI — LLM Intelligence Layer Exceptions.

Defines dedicated exceptions for LLM provider communication, schema validation,
rate limiting, prompt injection defenses, and fallback triggers.
"""

class LLMBaseException(Exception):
    """Base exception for all LLM intelligence layer errors."""
    pass


class LLMConfigurationError(LLMBaseException):
    """Raised when an LLM provider is misconfigured or lacks mandatory API keys."""
    pass


class LLMTimeoutError(LLMBaseException):
    """Raised when an LLM request exceeds configured timeout threshold."""
    pass


class LLMRateLimitError(LLMBaseException):
    """Raised when an LLM provider returns a 429 Rate Limit error."""
    pass


class LLMAuthenticationError(LLMBaseException):
    """Raised when an LLM provider rejects credentials (401/403)."""
    pass


class LLMOutputParsingError(LLMBaseException):
    """Raised when LLM output violates structured Pydantic schema contracts."""
    pass


class PromptInjectionDetectedError(LLMBaseException):
    """Raised when malicious adversarial prompt injection is intercepted."""
    pass
