"""SentinelJob AI — LLM Intelligence Structured Schemas & Contracts.

Strict Pydantic models governing LLM inputs, structured outputs, evidence traceability,
scam archetypes, and inference telemetry.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ScamArchetypeEnum(str, Enum):
    TASK_SCAM = "TASK_SCAM"
    FAKE_CHECK = "FAKE_CHECK"
    ADVANCE_FEE = "ADVANCE_FEE"
    IDENTITY_HARVEST = "IDENTITY_HARVEST"
    GHOST_JOB = "GHOST_JOB"
    RESHIPPING = "RESHIPPING"
    FAKE_RECRUITER = "FAKE_RECRUITER"
    IMPERSONATION = "IMPERSONATION"
    CRYPTO_SCAM = "CRYPTO_SCAM"
    PAYMENT_SCAM = "PAYMENT_SCAM"
    INVESTMENT_SCAM = "INVESTMENT_SCAM"
    OTHER = "OTHER"


class LLMVerdictEnum(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    RISKY = "RISKY"


class StructuredEvidenceItem(BaseModel):
    claim: str = Field(..., description="Specific finding or factual observation")
    source_signal: str = Field(..., description="Telemetry signal (e.g., RDAP, RuleEngine, SalaryMatrix, NLP)")
    quote: Optional[str] = Field(None, description="Exact substring from raw job content")
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    severity: str = Field("medium", description="Severity level: low, medium, high, critical")


class LLMStructuredSynthesis(BaseModel):
    """Pydantic contract for structured LLM forensic output."""
    verdict: LLMVerdictEnum = Field(..., description="Overall synthesized risk category: SAFE, CAUTION, RISKY")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    primary_archetype: ScamArchetypeEnum = Field(ScamArchetypeEnum.OTHER, description="Primary scam classification")
    secondary_archetypes: List[ScamArchetypeEnum] = Field(default_factory=list, description="Concurrent secondary threat vectors")
    executive_summary: str = Field(..., min_length=10, description="Concise forensic synthesis grounded on telemetry")
    red_flags: List[str] = Field(default_factory=list, description="List of concrete deceptive signals")
    green_flags: List[str] = Field(default_factory=list, description="List of authentic professional signals")
    evidence: List[StructuredEvidenceItem] = Field(default_factory=list, description="Traceable factual evidence items")
    recommended_actions: List[str] = Field(default_factory=list, description="Actionable candidate safety checklist")
    uncertainty_statement: Optional[str] = Field(None, description="Explicit boundaries of confidence or unverified signals")
    reasoning_summary: Optional[str] = Field(None, description="Concise high-level rationale without raw chain-of-thought")

    model_config = ConfigDict(use_enum_values=True)


class LLMTelemetryRecord(BaseModel):
    provider: str
    model: str
    prompt_version: str
    latency_ms: float
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    is_fallback: bool = False
    status: str = "SUCCESS"  # SUCCESS, FALLBACK, ERROR
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
