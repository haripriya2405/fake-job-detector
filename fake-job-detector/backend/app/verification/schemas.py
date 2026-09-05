from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ExtractedURL(BaseModel):
    url: str
    hostname: str
    registrable_domain: str
    scheme: str = "https"
    path: str = ""
    is_safe: bool = True
    extraction_source: str = "text"


class DNSAnalysis(BaseModel):
    resolves: bool = False
    a_records: List[str] = Field(default_factory=list)
    aaaa_records: List[str] = Field(default_factory=list)
    mx_records: List[str] = Field(default_factory=list)
    has_mx: bool = False
    ns_records: List[str] = Field(default_factory=list)
    query_time_ms: float = 0.0
    status: str = "unresolved"  # "resolves", "nxdomain", "timeout", "ssrf_blocked"


class RDAPAnalysis(BaseModel):
    status: str = "unavailable"  # "available", "unavailable", "rate_limited", "error", "skipped"
    registration_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    domain_age_days: Optional[int] = None
    registrar_name: Optional[str] = None
    nameservers: List[str] = Field(default_factory=list)
    domain_status: List[str] = Field(default_factory=list)
    raw_rdap_url: Optional[str] = None


class RecruiterEmailAnalysis(BaseModel):
    email: str
    local_part: str
    email_domain: str
    is_free_webmail: bool = False
    is_disposable_email: bool = False
    matches_company_domain: Optional[bool] = None
    matches_job_domain: Optional[bool] = None


class VerificationSignal(BaseModel):
    signal_code: str
    name: str
    severity: str  # "high", "medium", "low", "advisory"
    weight: int
    description: str
    evidence: str


class CompanyConsistencyResult(BaseModel):
    claimed_name: Optional[str] = None
    website_domain: Optional[str] = None
    recruiter_email: Optional[str] = None
    email_domain_match: Optional[bool] = None
    status: str = "unverified"  # "verified", "partially_verified", "inconsistent", "unverified", "unavailable"
    consistency_notes: List[str] = Field(default_factory=list)


class DomainVerificationResult(BaseModel):
    url: str
    hostname: str
    registrable_domain: str
    dns: DNSAnalysis
    rdap: RDAPAnalysis
    is_recently_registered: bool = False  # e.g., < 90 days


class VerificationOutput(BaseModel):
    verification_version: str = "verification-v1.0.0"
    extracted_urls: List[ExtractedURL] = Field(default_factory=list)
    primary_domain: Optional[DomainVerificationResult] = None
    all_domains: List[DomainVerificationResult] = Field(default_factory=list)
    emails: List[RecruiterEmailAnalysis] = Field(default_factory=list)
    company: CompanyConsistencyResult
    signals: List[VerificationSignal] = Field(default_factory=list)
    domain_penalty_score: int = 0
    confidence: float = 0.0
    status_summary: str = "unverified"
