"""Web Reputation, Public Sentiment & Threat Intelligence Service (Phase 21).
Calculates composite domain trust scores, checks external threat indicators,
and generates structured Red Flags & Green Flags evidence lists.
"""

from typing import Any, Dict, List, Optional
import re
from pydantic import BaseModel, Field


class ReputationIntelligenceInfo(BaseModel):
    trust_score: int = Field(..., ge=0, le=100, description="0 (Dangerous/Fake) to 100 (Highly Trusted)")
    domain_reputation_level: str = "TRUSTED"  # "TRUSTED" | "MODERATE" | "SUSPICIOUS" | "CRITICAL_THREAT"
    threat_intel_matches: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    green_flags: List[str] = Field(default_factory=list)
    scamdoc_equivalent_score: int = 85
    summary: str


class ReputationIntelligenceService:
    """Evaluates composite entity reputation and compiles cited evidence flags."""

    def evaluate_reputation(
        self,
        domain: Optional[str] = None,
        domain_age_days: Optional[int] = None,
        is_free_email: bool = False,
        is_disposable_email: bool = False,
        is_official_ats: bool = False,
        has_mx_records: bool = True,
        salary_unrealistic: bool = False,
        scam_rules_triggered: List[Dict[str, Any]] = None,
        text: str = "",
    ) -> ReputationIntelligenceInfo:
        rules = scam_rules_triggered or []
        red_flags: List[str] = []
        green_flags: List[str] = []
        threat_matches: List[str] = []

        base_trust = 95

        # Domain age evaluation
        if domain_age_days is not None:
            if domain_age_days < 30:
                base_trust -= 60
                red_flags.append(f"Domain registered only {domain_age_days} days ago (Brand new website created for temporary scam campaign)")
                threat_matches.append("Domain age < 30 days (High Fraud Correlation)")
            elif domain_age_days < 90:
                base_trust -= 35
                red_flags.append(f"Domain is under 90 days old ({domain_age_days} days old)")
            elif domain_age_days > 730:
                green_flags.append(f"Established corporate domain ({domain_age_days // 365}+ years online)")
        elif domain and not is_official_ats:
            red_flags.append("Domain age unverified / WHOIS privacy masked")

        # Free / Disposable email
        if is_free_email:
            base_trust -= 30
            red_flags.append("Recruiter uses free email provider (e.g. @gmail.com, @yahoo.com) instead of corporate domain")
        elif domain and has_mx_records:
            green_flags.append("Verified enterprise mail exchange (MX) DNS infrastructure")

        if is_disposable_email:
            base_trust -= 70
            red_flags.append("Temporary / burner email domain detected")
            threat_matches.append("Disposable email provider")

        # Official ATS
        if is_official_ats:
            base_trust += 10
            green_flags.append("Job hosted on authenticated Enterprise Applicant Tracking System")

        # Salary evaluation
        if salary_unrealistic:
            base_trust -= 30
            red_flags.append("Offered pay significantly exceeds real-world BLS industry benchmarks (High-salary lure trap)")

        # Scam rules triggered
        for r in rules:
            rule_id = r.get("rule_id", "")
            name = r.get("name", "Suspicious Pattern")
            desc = r.get("description", "")
            sev = r.get("severity", "MEDIUM")

            if sev in ["CRITICAL", "HIGH"]:
                base_trust -= 35
                red_flags.append(f"🚨 {name}: {desc}")
                threat_matches.append(f"FTC/IC3 Pattern: {name}")
            else:
                base_trust -= 15
                red_flags.append(f"⚠️ {name}: {desc}")

        # Check for standard positive legitimate markers
        if "401(k)" in text.lower() or "health insurance" in text.lower() or "medical dental vision" in text.lower():
            green_flags.append("Standard legitimate corporate benefits & compensation package outlined")
        if "equal opportunity employer" in text.lower() or "eeo" in text.lower():
            green_flags.append("EEO (Equal Employment Opportunity) statement included")

        final_trust = max(0, min(100, base_trust))

        if final_trust < 30:
            rep_level = "CRITICAL_THREAT"
            summary = "Entity exhibits severe scam patterns and high threat indicators. Do not share personal data or pay money."
        elif final_trust < 60:
            rep_level = "SUSPICIOUS"
            summary = "Suspicious attributes detected. Exercise caution and verify identity directly with the company."
        elif final_trust < 80:
            rep_level = "MODERATE"
            summary = "Moderate trust level. Standard checks passed with minor observations."
        else:
            rep_level = "TRUSTED"
            summary = "Strong trust profile. Established domain, verified infrastructure, and realistic job description."

        return ReputationIntelligenceInfo(
            trust_score=final_trust,
            domain_reputation_level=rep_level,
            threat_intel_matches=threat_matches,
            red_flags=red_flags,
            green_flags=green_flags,
            scamdoc_equivalent_score=final_trust,
            summary=summary,
        )


# Singleton instance
reputation_intelligence_service = ReputationIntelligenceService()
