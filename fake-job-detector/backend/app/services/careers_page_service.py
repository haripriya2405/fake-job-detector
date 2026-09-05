"""Official Careers Page & ATS Live Verification Service (Phase 21).
Validates whether a job posting originates from a verified corporate Applicant Tracking System (ATS)
(e.g., Greenhouse, Lever, Workday, SmartRecruiters, Ashby, BambooHR) or an unverified free/ghost job syndicator.
"""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel, Field


class CareersVerificationInfo(BaseModel):
    is_official_ats: bool = False
    ats_provider: Optional[str] = None  # "Greenhouse" | "Lever" | "Workday" | "Ashby" | "SmartRecruiters" | "BambooHR" | "Custom Corporate"
    detected_careers_domain: Optional[str] = None
    is_syndicated_board: bool = False
    is_suspicious_redirect: bool = False
    risk_points: int = 0
    verdict: str = "UNVERIFIED_SOURCE"  # "OFFICIAL_ATS_VERIFIED" | "OFFICIAL_CAREERS_PAGE" | "TRUSTED_JOB_BOARD" | "UNVERIFIED_SOURCE" | "SUSPICIOUS_DOMAIN"
    explanation: str


KNOWN_ATS_DOMAINS = {
    "boards.greenhouse.io": "Greenhouse",
    "job-boards.greenhouse.io": "Greenhouse",
    "jobs.lever.co": "Lever",
    "myworkdayjobs.com": "Workday",
    "workday.com": "Workday",
    "smartrecruiters.com": "SmartRecruiters",
    "jobs.ashbyhq.com": "Ashby",
    "bamboohr.com": "BambooHR",
    "icims.com": "iCIMS",
    "applytojob.com": "JazzHR",
    "recruitee.com": "Recruitee",
    "rippling-ats.com": "Rippling",
    "apply.workable.com": "Workable",
    "workable.com": "Workable",
    "jobs.jobvite.com": "Jobvite",
    "jobvite.com": "Jobvite",
    "taleo.net": "Oracle Taleo",
    "successfactors.com": "SAP SuccessFactors",
    "jobs2web.com": "SAP SuccessFactors",
    "csod.com": "Cornerstone OnDemand",
    "cornerstoneondemand.com": "Cornerstone OnDemand",
    "phenompeople.com": "Phenom",
    "phenom.com": "Phenom",
    "eightfold.ai": "Eightfold.ai",
    "pinpointhq.com": "Pinpoint",
    "bullhornreach.com": "Bullhorn",
    "bullhorn.com": "Bullhorn",
    "avature.net": "Avature",
}

KNOWN_ATS_QUERY_PARAMS = {
    "gh_jid": "Greenhouse",
    "lever-origin": "Lever",
    "jobvite_id": "Jobvite",
    "ashby_jid": "Ashby",
    "workable_id": "Workable",
}

TRUSTED_JOB_BOARDS = [
    "linkedin.com",
    "indeed.com",
    "glassdoor.com",
    "dice.com",
    "builtin.com",
    "wellfound.com",
    "angel.co",
    "remoteok.com",
    "weworkremotely.com",
]


class CareersPageService:
    """Evaluates posting origin and official ATS listing presence."""

    def verify_careers_origin(self, url: Optional[str] = None, text: Optional[str] = None, company_name: Optional[str] = None) -> CareersVerificationInfo:
        if not url:
            # Check text for ATS or careers references
            if text:
                for domain, provider in KNOWN_ATS_DOMAINS.items():
                    if domain in text.lower():
                        return CareersVerificationInfo(
                            is_official_ats=True,
                            ats_provider=provider,
                            detected_careers_domain=domain,
                            risk_points=0,
                            verdict="OFFICIAL_ATS_VERIFIED",
                            explanation=f"Posting references official {provider} enterprise ATS portal ({domain}).",
                        )

            return CareersVerificationInfo(
                is_official_ats=False,
                ats_provider=None,
                detected_careers_domain=None,
                risk_points=5,
                verdict="UNVERIFIED_SOURCE",
                explanation="No official corporate careers URL or ATS link provided. Job authenticity cannot be verified through official channels.",
            )

        try:
            parsed = urlparse(url)
            netloc = (parsed.netloc or "").lower().split(":")[0]
            query = (parsed.query or "").lower()
        except Exception:
            netloc = ""
            query = ""

        # 1. Check known ATS providers in netloc
        for ats_domain, provider in KNOWN_ATS_DOMAINS.items():
            if netloc == ats_domain or netloc.endswith("." + ats_domain):
                return CareersVerificationInfo(
                    is_official_ats=True,
                    ats_provider=provider,
                    detected_careers_domain=netloc,
                    is_syndicated_board=False,
                    risk_points=0,
                    verdict="OFFICIAL_ATS_VERIFIED",
                    explanation=f"Job posting hosted directly on verified {provider} Applicant Tracking System ({netloc}).",
                )

        # 1b. Check known ATS embedded query tokens (e.g., custom site embedding Greenhouse/Lever)
        for param, provider in KNOWN_ATS_QUERY_PARAMS.items():
            if param in query:
                return CareersVerificationInfo(
                    is_official_ats=True,
                    ats_provider=provider,
                    detected_careers_domain=netloc,
                    is_syndicated_board=False,
                    risk_points=0,
                    verdict="OFFICIAL_ATS_VERIFIED",
                    explanation=f"Job posting references embedded {provider} ATS identifier parameter ('{param}').",
                )

        # 2. Check trusted major job syndication boards
        for board in TRUSTED_JOB_BOARDS:
            if netloc == board or netloc.endswith("." + board):
                return CareersVerificationInfo(
                    is_official_ats=False,
                    ats_provider=None,
                    detected_careers_domain=netloc,
                    is_syndicated_board=True,
                    risk_points=5,
                    verdict="TRUSTED_JOB_BOARD",
                    explanation=f"Job posting found on major syndicated board ({board}). Ensure posting is also cross-verified on company's direct careers page.",
                )

        # 3. Check direct corporate careers subdomain
        if "careers" in netloc or "jobs" in netloc:
            return CareersVerificationInfo(
                is_official_ats=True,
                ats_provider="Custom Corporate",
                detected_careers_domain=netloc,
                is_syndicated_board=False,
                risk_points=0,
                verdict="OFFICIAL_CAREERS_PAGE",
                explanation=f"Job URL is hosted on official corporate careers subdomain ({netloc}).",
            )

        # 4. Unknown domain / potentially suspicious
        return CareersVerificationInfo(
            is_official_ats=False,
            ats_provider=None,
            detected_careers_domain=netloc,
            is_syndicated_board=False,
            risk_points=15,
            verdict="UNVERIFIED_SOURCE",
            explanation=f"Job URL domain '{netloc}' is not a recognized corporate ATS or verified job platform.",
        )


# Singleton instance
careers_page_service = CareersPageService()
