from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class ScoreBreakdownSchema(BaseModel):
    ml_contribution: int = 0
    rule_contribution: int = 0
    domain_penalty: int = 0
    total_score: int = 0


class IndicatorSchema(BaseModel):
    id: Optional[str] = None
    title: str
    severity: str = "medium"  # "low", "medium", "high", "critical"
    category: Optional[str] = "General Risk"
    description: str
    recommendation: Optional[str] = None
    risk_weight: Optional[str] = None


class EvidenceSnippetSchema(BaseModel):
    quote: str
    type: str = "Suspicious Pattern"
    risk_weight: Optional[str] = None
    page_number: Optional[int] = None
    confidence: Optional[float] = None
    source_type: Optional[str] = None


class CompanyVerificationSchema(BaseModel):
    status: str = "unverified"  # "verified", "partially_verified", "inconsistent", "unverified", "unavailable"
    domain_checked: Optional[str] = "Unspecified"
    domain_age_days: Optional[int] = 0
    whois_age_days: Optional[int] = Field(0, description="Deprecated alias for domain_age_days")
    registration_date: Optional[datetime] = None
    rdap_status: Optional[str] = "available"
    mx_record_valid: Optional[bool] = False
    linkedin_match: Optional[bool] = False
    notes: Optional[str] = None


class UrlAnalysisSchema(BaseModel):
    status: str = "clean"  # "clean", "warning", "suspicious", "flagged"
    extracted_urls: List[str] = Field(default_factory=list)
    has_phishing_signals: bool = False
    has_shortened_links: bool = False


class SafetyRecommendationSchema(BaseModel):
    priority: str = "advisory"  # "urgent", "advisory", "safe"
    action: str
    detail: str


class MultiModalExtractionSchema(BaseModel):
    source_type: str = "TEXT"
    extraction_method: str = "direct"
    extraction_confidence: float = 1.0
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    content_hash: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    extracted_urls: List[str] = Field(default_factory=list)
    extracted_emails: List[str] = Field(default_factory=list)
    extracted_phone_numbers: List[str] = Field(default_factory=list)
    extracted_messaging_handles: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 21: JobScamScore 8-Layer Signal Schemas
# ---------------------------------------------------------------------------

class SalaryBenchmarkSchema(BaseModel):
    detected_salary_text: Optional[str] = None
    currency: str = "USD"
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    frequency: Optional[str] = None
    annualized_min: Optional[float] = None
    annualized_max: Optional[float] = None
    matched_job_family: str = "general_corporate"
    market_median_annual: float = 60000.0
    market_p25_annual: float = 42000.0
    market_p90_annual: float = 110000.0
    market_p90_hourly: Optional[float] = None
    discrepancy_ratio: float = 1.0
    is_unrealistic_high: bool = False
    is_unrealistic_low: bool = False
    risk_points: int = 0
    verdict: str = "REALISTIC_MARKET_RATE"
    explanation: str = "Compensation within standard market bounds."


class CareersVerificationSchema(BaseModel):
    is_official_ats: bool = False
    ats_provider: Optional[str] = None
    detected_careers_domain: Optional[str] = None
    is_syndicated_board: bool = False
    is_suspicious_redirect: bool = False
    risk_points: int = 0
    verdict: str = "UNVERIFIED_SOURCE"
    explanation: str = "Careers origin verified."


class ReputationIntelligenceSchema(BaseModel):
    trust_score: int = 85
    domain_reputation_level: str = "TRUSTED"
    threat_intel_matches: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    green_flags: List[str] = Field(default_factory=list)
    scamdoc_equivalent_score: int = 85
    summary: str = "Established reputation."


class SignalLayerSchema(BaseModel):
    layer_id: int
    name: str
    status: str = "PASS"  # "PASS" | "WARN" | "FAIL"
    score: int = 100
    description: str
    detail: str


class Signals8LayerSchema(BaseModel):
    layer_1_company_authentication: SignalLayerSchema
    layer_2_careers_page_verification: SignalLayerSchema
    layer_3_recruiter_identity: SignalLayerSchema
    layer_4_salary_benchmarking: SignalLayerSchema
    layer_5_scam_pattern_detection: SignalLayerSchema
    layer_6_contact_validation: SignalLayerSchema
    layer_7_domain_ssl_intelligence: SignalLayerSchema
    layer_8_live_threat_intelligence: SignalLayerSchema
    checks_total: int = 50
    checks_passed: int = 50


class AnalysisCreate(BaseModel):
    raw_content: str = Field(..., min_length=20, description="Raw job posting text (minimum 20 characters)")
    job_title: Optional[str] = Field(None, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    source_type: Optional[str] = Field("text", description="Source modality: text, pdf, image, url")


class UrlAnalysisCreate(BaseModel):
    job_url: str = Field(..., description="Public HTTP/HTTPS URL of the job posting")
    job_title: Optional[str] = Field(None, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)


# ---------------------------------------------------------------------------
# Phase 24 Feature 4: Phone Carrier & Fraud Watchlist Schemas
# ---------------------------------------------------------------------------

class PhoneDetailSchema(BaseModel):
    phone_number: str
    area_code: Optional[str] = None
    line_type: str = "MOBILE_CELLULAR"
    carrier_name: str = "Standard Cellular Network"
    is_voip: bool = False
    risk_contribution: int = 0
    risk_flags: List[str] = Field(default_factory=list)


class PhoneIntelligenceSchema(BaseModel):
    detected: bool = False
    phone_count: int = 0
    phones: List[PhoneDetailSchema] = Field(default_factory=list)
    has_voip_burner: bool = False
    risk_penalty: int = 0


class WatchlistMatchSchema(BaseModel):
    id: str
    agency: str
    agency_code: str
    title: str
    threat_type: str
    summary: str
    severity: str
    matched_keywords: List[str] = Field(default_factory=list)
    reference_url: str


class FraudWatchlistSchema(BaseModel):
    has_watchlist_matches: bool = False
    status_verdict: str = "CLEAN_PASS"
    match_count: int = 0
    agencies_checked: List[str] = Field(default_factory=lambda: ["FTC", "BBB", "FBI_IC3"])
    agencies_flagged: List[str] = Field(default_factory=list)
    matches: List[WatchlistMatchSchema] = Field(default_factory=list)
    risk_penalty: int = 0


class AnalysisResponse(BaseModel):
    id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    claimed_company: Optional[str] = None
    source_type: str = "text"
    raw_content: str
    risk_score: int = 0
    risk_level: str = "pending"
    verdict_category: str = "SAFE"  # "SAFE" | "CAUTION" | "RISKY"
    created_at: datetime
    explanation: Optional[str] = None
    analysis_engine: str = "pending"
    
    score_breakdown: Optional[ScoreBreakdownSchema] = None
    indicators: List[IndicatorSchema] = Field(default_factory=list)
    evidence_snippets: List[EvidenceSnippetSchema] = Field(default_factory=list)
    company_verification: Optional[CompanyVerificationSchema] = None
    url_analysis: Optional[UrlAnalysisSchema] = None
    recommendations: List[SafetyRecommendationSchema] = Field(default_factory=list)
    extraction: Optional[MultiModalExtractionSchema] = None

    # Phase 21 JobScamScore Signal Stack
    salary_benchmark: Optional[SalaryBenchmarkSchema] = None
    careers_verification: Optional[CareersVerificationSchema] = None
    reputation_intelligence: Optional[ReputationIntelligenceSchema] = None
    signals_8_layer: Optional[Signals8LayerSchema] = None
    red_flags: List[str] = Field(default_factory=list)
    green_flags: List[str] = Field(default_factory=list)

    # Phase 24 Feature 4 Contact & Watchlist Intelligence
    phone_intelligence: Optional[PhoneIntelligenceSchema] = None
    fraud_watchlists: Optional[FraudWatchlistSchema] = None

    # Phase 22 Enterprise LLM, Archetype & Multi-Stage Pipeline
    primary_archetype: Optional[str] = "OTHER"
    secondary_archetypes: List[str] = Field(default_factory=list)
    llm_synthesis: Optional[Dict[str, Any]] = None
    pipeline_audit: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class AnalysisHistoryItem(BaseModel):
    id: str
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    source_type: str
    risk_score: int
    risk_level: str
    verdict_category: str = "SAFE"
    created_at: datetime
    explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Phase 22: Batch Analysis & Reporting Schemas
# ---------------------------------------------------------------------------

class BatchAnalysisCreate(BaseModel):
    items: List[AnalysisCreate] = Field(
        ...,
        min_length=1,
        max_length=25,
        description="List of 1 to 25 job postings to analyze concurrently in batch",
    )


class BatchRiskSummary(BaseModel):
    total_jobs: int = 0
    safe_count: int = 0
    caution_count: int = 0
    risky_count: int = 0
    average_risk_score: float = 0.0
    highest_risk_score: int = 0
    critical_flags_found: int = 0


class BatchAnalysisResponse(BaseModel):
    batch_id: str
    total_analyzed: int
    summary: BatchRiskSummary
    results: List[AnalysisResponse]
