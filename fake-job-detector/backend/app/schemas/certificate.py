from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VerificationCertificateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    certificate_id: str
    analysis_id: str
    job_title: str
    company_name: str
    risk_score: int
    risk_level: str
    legitimacy_verdict: str  # "VERIFIED_SAFE", "CAUTION_ADVISED", "HIGH_RISK_SUSPICIOUS"
    verdict_badge_color: str  # "emerald", "amber", "crimson"
    is_tamper_evident_valid: bool
    digital_signature: str
    sha256_fingerprint: str
    analyzed_at: datetime
    verified_at: datetime
    summary: str
    key_indicators: List[str]
    shareable_url: str
    embed_badge_markdown: str
    embed_badge_html: str
    embed_badge_svg_url: str
