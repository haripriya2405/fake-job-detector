from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CommunityScamCreate(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=255)
    impostor_company: str = Field(..., min_length=2, max_length=255)
    impostor_domain: Optional[str] = Field(None, max_length=255)
    contact_platform: Optional[str] = Field(None, max_length=100)
    scam_category: str = Field(..., min_length=2, max_length=100)
    risk_score: int = Field(85, ge=0, le=100)
    risk_level: str = Field("high", max_length=50)
    description_snippet: str = Field(..., min_length=10, max_length=5000)
    red_flags: List[str] = Field(default_factory=list)
    evidence_summary: Optional[str] = Field(None, max_length=2000)
    source_dataset: str = Field("COMMUNITY", max_length=100)


class CommunityScamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    public_id: str
    job_title: str
    impostor_company: str
    impostor_domain: Optional[str] = None
    contact_platform: Optional[str] = None
    scam_category: str
    risk_score: int
    risk_level: str
    description_snippet: str
    red_flags: List[str]
    evidence_summary: Optional[str] = None
    community_confirmations: int
    flag_count: int
    is_verified_threat: bool
    source_dataset: str
    created_at: datetime
    updated_at: datetime


class CommunityScamFeedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    stats: Dict[str, Any]
    items: List[CommunityScamResponse]


class PublishScanToCommunityRequest(BaseModel):
    analysis_id: str
    consent_anonymize: bool = True
    custom_notes: Optional[str] = None
