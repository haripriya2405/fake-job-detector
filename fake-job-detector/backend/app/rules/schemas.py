from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TriggeredRule(BaseModel):
    rule_code: str
    name: str
    category: str
    severity: str  # "critical", "high", "medium", "low"
    matched: bool = True
    score_contribution: int
    confidence: float
    evidence_text: str
    explanation: str
    recommendation: str
    rule_version: str = "rules-v1.0.0"


class RuleEngineResult(BaseModel):
    rule_version: str = "rules-v1.0.0"
    triggered_rules: List[TriggeredRule] = Field(default_factory=list)
    category_scores: Dict[str, int] = Field(default_factory=dict)
    raw_score: int = 0
    capped_score: int = 0


class RiskScoreBreakdown(BaseModel):
    ml_contribution: int = 0
    ml_probability: float = 0.0
    rule_contribution: int = 0
    category_breakdown: Dict[str, int] = Field(default_factory=dict)
    domain_penalty: int = 0
    total_score: int = 0


class RiskEngineResult(BaseModel):
    final_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(..., description="'low', 'medium', 'high', or 'critical'")
    score_breakdown: RiskScoreBreakdown
    triggered_indicators: List[TriggeredRule] = Field(default_factory=list)
    explanation: str
    recommendations: List[Dict[str, str]] = Field(default_factory=list)
    engine_version: str = "risk-engine-v1.0.0"
