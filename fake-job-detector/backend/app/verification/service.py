import re
from typing import Any, Dict, List, Optional, Tuple
from app.verification.dns_client import dns_resolver
from app.verification.rdap_client import rdap_client
from app.verification.schemas import (
    CompanyConsistencyResult,
    DomainVerificationResult,
    ExtractedURL,
    RDAPAnalysis,
    RecruiterEmailAnalysis,
    VerificationOutput,
    VerificationSignal,
)
from app.verification.url_extractor import get_registrable_domain, url_extractor

FREE_MAIL_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "rediffmail.com", "protonmail.com", "yopmail.com", "mail.com",
    "zoho.com", "icloud.com", "aol.com",
}

def _load_disposable_domains() -> set:
    import os
    domains = {"mailinator.com", "guerrillamail.com", "tempmail.com", "10minutemail.com", "trashmail.com"}
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
    list_path = os.path.join(data_dir, "disposable_email_blocklist.conf.txt")
    if not os.path.exists(list_path):
        list_path = os.path.join(data_dir, "disposable_email_blocklist.conf")
    if os.path.exists(list_path):
        try:
            with open(list_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    dom = line.strip().lower()
                    if dom and not dom.startswith("#"):
                        domains.add(dom)
        except Exception:
            pass
    return domains

DISPOSABLE_EMAIL_PROVIDERS = _load_disposable_domains()

KNOWN_ENTERPRISE_ATS_DOMAINS = {
    "greenhouse.io", "lever.co", "myworkdayjobs.com", "workday.com",
    "smartrecruiters.com", "ashbyhq.com", "taleo.net", "bamboohr.com",
    "workable.com", "icims.com", "jobvite.com", "successfactors.com",
    "jazzhr.com", "rippling.com", "breezy.hr", "recruitee.com",
    "workdayjobs.com", "pinpointhq.com", "join.com"
}

EMAIL_REGEX = re.compile(
    r'\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,12})\b',
    re.IGNORECASE,
)


class VerificationService:
    """Multi-layer Domain, Email, and Company Consistency Verification Service.
    Uses RDAP, DNS resolution, MX validation, ATS identification, and recruiter email cross-referencing.
    """

    VERSION = "verification-v2.0.0"

    # Configurable Signal Weights (Max Domain Penalty Cap: 35)
    SIGNAL_WEIGHTS = {
        "LOOKALIKE_BRAND_DOMAIN": 25,
        "DOMAIN_NOT_RESOLVING": 15,
        "DOMAIN_RECENT_REGISTRATION": 10,
        "EMAIL_DOMAIN_MISMATCH": 10,
        "EMAIL_DISPOSABLE_PROVIDER": 20,
        "EMAIL_FREE_WEBMAIL": 8,
        "DOMAIN_NO_MX": 5,
        "COMPANY_DOMAIN_INCONSISTENCY": 14,
        "DOMAIN_REGISTRATION_UNAVAILABLE": 3,
        "ATS_PORTAL_VERIFIED": -10,  # Negative weight reduces risk
    }
    MAX_DOMAIN_PENALTY: int = 35

    def verify_job_posting(
        self,
        text: str,
        claimed_company: Optional[str] = None,
        job_title: Optional[str] = None,
    ) -> VerificationOutput:
        """Perform full domain, email, and company consistency checks on job text."""
        # 1. Extract URLs
        extracted_urls = url_extractor.extract_urls(text)

        # 2. Extract Recruiter Emails
        emails = self._extract_emails(text)

        # 3. Verify Extracted Domains
        domain_results: List[DomainVerificationResult] = []
        seen_domains = set()

        for u in extracted_urls:
            reg_domain = u.registrable_domain
            if reg_domain and reg_domain not in seen_domains:
                seen_domains.add(reg_domain)
                d_res = self._verify_single_domain(u.url, u.hostname, reg_domain)
                domain_results.append(d_res)

        primary_domain = domain_results[0] if domain_results else None

        # 4. Perform Company Consistency Check
        company_result = self._check_company_consistency(
            claimed_company=claimed_company,
            extracted_domains=domain_results,
            emails=emails,
        )

        # 5. Generate Verification Signals
        signals, penalty_score = self._generate_signals(
            domain_results=domain_results,
            emails=emails,
            company_result=company_result,
        )

        # 6. Compute Confidence Score
        confidence = self._compute_confidence(domain_results, emails, company_result)

        # 7. Compute Summary Status
        status_summary = company_result.status

        return VerificationOutput(
            verification_version=self.VERSION,
            extracted_urls=extracted_urls,
            primary_domain=primary_domain,
            all_domains=domain_results,
            emails=emails,
            company=company_result,
            signals=signals,
            domain_penalty_score=penalty_score,
            confidence=confidence,
            status_summary=status_summary,
        )

    def _extract_emails(self, text: str) -> List[RecruiterEmailAnalysis]:
        if not text:
            return []

        matches = EMAIL_REGEX.findall(text)
        results: List[RecruiterEmailAnalysis] = []
        seen_emails = set()

        for local, domain in matches:
            email_clean = f"{local}@{domain}".lower()
            if email_clean not in seen_emails:
                seen_emails.add(email_clean)
                dom_clean = domain.lower()
                is_free = dom_clean in FREE_MAIL_PROVIDERS
                is_disposable = dom_clean in DISPOSABLE_EMAIL_PROVIDERS
                results.append(
                    RecruiterEmailAnalysis(
                        email=email_clean,
                        local_part=local.lower(),
                        email_domain=dom_clean,
                        is_free_webmail=is_free,
                        is_disposable_email=is_disposable,
                    )
                )
        return results

    def _verify_single_domain(self, url: str, hostname: str, registrable_domain: str) -> DomainVerificationResult:
        dns_res = dns_resolver.resolve_domain(registrable_domain)
        rdap_res = rdap_client.lookup_domain(registrable_domain)

        is_recent = False
        if rdap_res.domain_age_days is not None and rdap_res.domain_age_days < 90:
            is_recent = True

        return DomainVerificationResult(
            url=url,
            hostname=hostname,
            registrable_domain=registrable_domain,
            dns=dns_res,
            rdap=rdap_res,
            is_recently_registered=is_recent,
        )

    def _check_company_consistency(
        self,
        claimed_company: Optional[str],
        extracted_domains: List[DomainVerificationResult],
        emails: List[RecruiterEmailAnalysis],
    ) -> CompanyConsistencyResult:
        notes: List[str] = []
        primary_domain_str = extracted_domains[0].registrable_domain if extracted_domains else None
        first_email = emails[0] if emails else None
        email_match = None

        has_verified_ats = any(
            any(ats in d.hostname or ats in d.registrable_domain for ats in KNOWN_ENTERPRISE_ATS_DOMAINS)
            for d in extracted_domains
        )

        if claimed_company:
            notes.append(f"Claimed company: '{claimed_company}'")

        if has_verified_ats:
            notes.append("Application hosted on verified Enterprise Applicant Tracking System (ATS)")

        if first_email and primary_domain_str:
            email_domain = get_registrable_domain(first_email.email_domain)
            if email_domain == primary_domain_str:
                email_match = True
                first_email.matches_job_domain = True
                first_email.matches_company_domain = True
                notes.append(f"Recruiter email '{first_email.email}' matches job domain '{primary_domain_str}'")
            elif first_email.is_free_webmail:
                email_match = False
                first_email.matches_job_domain = False
                notes.append(f"Recruiter uses personal webmail ('{first_email.email_domain}') rather than corporate domain")
            else:
                email_match = False
                first_email.matches_job_domain = False
                notes.append(f"Recruiter email domain '{first_email.email_domain}' does not match job domain '{primary_domain_str}'")

        # Determine verification tier
        if has_verified_ats:
            status = "verified"
        elif extracted_domains and extracted_domains[0].dns.resolves:
            if extracted_domains[0].rdap.domain_age_days and extracted_domains[0].rdap.domain_age_days > 365 and email_match:
                status = "verified"
            elif email_match is False and not first_email.is_free_webmail:
                status = "inconsistent"
            else:
                status = "partially_verified"
        elif extracted_domains and not extracted_domains[0].dns.resolves:
            status = "inconsistent"
        elif claimed_company:
            status = "unverified"
        else:
            status = "unavailable"

        return CompanyConsistencyResult(
            claimed_name=claimed_company,
            website_domain=primary_domain_str,
            recruiter_email=first_email.email if first_email else None,
            email_domain_match=email_match,
            status=status,
            consistency_notes=notes,
        )

    def _generate_signals(
        self,
        domain_results: List[DomainVerificationResult],
        emails: List[RecruiterEmailAnalysis],
        company_result: CompanyConsistencyResult,
    ) -> Tuple[List[VerificationSignal], int]:
        signals: List[VerificationSignal] = []
        raw_penalty = 0

        for d in domain_results:
            # Check Enterprise ATS
            is_ats = any(ats in d.hostname or ats in d.registrable_domain for ats in KNOWN_ENTERPRISE_ATS_DOMAINS)
            if is_ats:
                signals.append(VerificationSignal(
                    signal_code="ATS_PORTAL_VERIFIED",
                    name="Verified Enterprise ATS Portal",
                    severity="advisory",
                    weight=self.SIGNAL_WEIGHTS["ATS_PORTAL_VERIFIED"],
                    description=f"Job application is routed through verified Enterprise ATS infrastructure ({d.registrable_domain}).",
                    evidence=f"ATS Host: {d.hostname}",
                ))
                raw_penalty += self.SIGNAL_WEIGHTS["ATS_PORTAL_VERIFIED"]
                continue

            # Check Brand Lookalike / Typosquatting
            if company_result.claimed_name:
                c_clean = re.sub(r'[^a-zA-Z0-9]', '', company_result.claimed_name.lower())
                d_clean = d.registrable_domain.lower()
                if len(c_clean) >= 4 and c_clean in d_clean:
                    # e.g., 'google' in 'google-careers-portal.com' vs 'google.com'
                    official_domain = f"{c_clean}.com"
                    if d.registrable_domain != official_domain and ("-" in d_clean or any(tld in d_clean for tld in [".xyz", ".top", ".info", ".online", ".site"])):
                        w = self.SIGNAL_WEIGHTS["LOOKALIKE_BRAND_DOMAIN"]
                        signals.append(VerificationSignal(
                            signal_code="LOOKALIKE_BRAND_DOMAIN",
                            name="Potential Brand Lookalike / Phishing Domain",
                            severity="high",
                            weight=w,
                            description=f"Domain '{d.registrable_domain}' contains brand name '{company_result.claimed_name}' with suspicious structure/TLD.",
                            evidence=f"Claimed Brand: {company_result.claimed_name}, Domain: {d.registrable_domain}",
                        ))
                        raw_penalty += w

            # 1. Check DNS resolution
            if not d.dns.resolves:
                w = self.SIGNAL_WEIGHTS["DOMAIN_NOT_RESOLVING"]
                signals.append(VerificationSignal(
                    signal_code="DOMAIN_NOT_RESOLVING",
                    name="Domain Does Not Resolve via DNS",
                    severity="high",
                    weight=w,
                    description=f"Domain '{d.registrable_domain}' has no valid A or AAAA records in global DNS.",
                    evidence=f"DNS Status: {d.dns.status}",
                ))
                raw_penalty += w
            elif not d.dns.has_mx:
                # 2. Check MX records
                w = self.SIGNAL_WEIGHTS["DOMAIN_NO_MX"]
                signals.append(VerificationSignal(
                    signal_code="DOMAIN_NO_MX",
                    name="Missing Mail Exchange (MX) Infrastructure",
                    severity="low",
                    weight=w,
                    description=f"Domain '{d.registrable_domain}' does not publish MX records for inbound mail.",
                    evidence="No MX records found",
                ))
                raw_penalty += w

            # 3. Check Domain Age
            if d.is_recently_registered:
                w = self.SIGNAL_WEIGHTS["DOMAIN_RECENT_REGISTRATION"]
                age = d.rdap.domain_age_days
                signals.append(VerificationSignal(
                    signal_code="DOMAIN_RECENT_REGISTRATION",
                    name="Recently Registered Domain",
                    severity="medium",
                    weight=w,
                    description=f"Domain '{d.registrable_domain}' was registered recently ({age} days ago).",
                    evidence=f"Age: {age} days (Registered: {d.rdap.registration_date})",
                ))
                raw_penalty += w
            elif d.rdap.status == "unavailable" and d.dns.resolves:
                # Registration data unavailable
                signals.append(VerificationSignal(
                    signal_code="DOMAIN_REGISTRATION_UNAVAILABLE",
                    name="Registration Data Redacted / Unavailable",
                    severity="advisory",
                    weight=0,
                    description="RDAP registration dates are private or redacted by the registrar.",
                    evidence="RDAP query returned no creation timestamp",
                ))

        # 4. Check Email Domain Consistency
        for email in emails:
            if email.is_disposable_email:
                w = self.SIGNAL_WEIGHTS["EMAIL_DISPOSABLE_PROVIDER"]
                signals.append(VerificationSignal(
                    signal_code="EMAIL_DISPOSABLE_PROVIDER",
                    name="Disposable / Burner Recruiter Email Provider",
                    severity="high",
                    weight=w,
                    description=f"Recruiter uses temporary burner/disposable email provider (@{email.email_domain}).",
                    evidence=f"Disposable Email: {email.email}",
                ))
                raw_penalty += w
            elif email.matches_job_domain is False and not email.is_free_webmail:
                w = self.SIGNAL_WEIGHTS["EMAIL_DOMAIN_MISMATCH"]
                signals.append(VerificationSignal(
                    signal_code="EMAIL_DOMAIN_MISMATCH",
                    name="Recruiter Email Domain Mismatch",
                    severity="medium",
                    weight=w,
                    description=f"Recruiter email '{email.email}' belongs to a different domain than the claimed portal.",
                    evidence=f"Email Domain: {email.email_domain}",
                ))
                raw_penalty += w
            elif email.is_free_webmail:
                w = self.SIGNAL_WEIGHTS["EMAIL_FREE_WEBMAIL"]
                signals.append(VerificationSignal(
                    signal_code="EMAIL_FREE_WEBMAIL",
                    name="Personal Webmail Used by Recruiter",
                    severity="low",
                    weight=w,
                    description=f"Recruiter uses free webmail ({email.email_domain}) rather than an enterprise domain.",
                    evidence=f"Email: {email.email}",
                ))
                raw_penalty += w

        # 5. Check Company Consistency
        if company_result.status == "inconsistent" or (company_result.claimed_name and any(e.is_free_webmail for e in emails)):
            w = self.SIGNAL_WEIGHTS["COMPANY_DOMAIN_INCONSISTENCY"]
            signals.append(VerificationSignal(
                signal_code="COMPANY_DOMAIN_INCONSISTENCY",
                name="Claimed Company & Recruiter Identity Inconsistency",
                severity="medium",
                weight=w,
                description=f"Recruiter contact channels are inconsistent with the claimed corporate identity '{company_result.claimed_name}'.",
                evidence="; ".join(company_result.consistency_notes) if company_result.consistency_notes else f"Free webmail used for enterprise {company_result.claimed_name}",
            ))
            raw_penalty += w

        # Capped domain penalty score (can be 0 or capped at max)
        capped_penalty = max(0, min(raw_penalty, self.MAX_DOMAIN_PENALTY))
        return signals, capped_penalty

    def _compute_confidence(
        self,
        domains: List[DomainVerificationResult],
        emails: List[RecruiterEmailAnalysis],
        company: CompanyConsistencyResult,
    ) -> float:
        score = 0.50
        if domains:
            score += 0.20
            if domains[0].dns.resolves:
                score += 0.10
            if domains[0].rdap.domain_age_days:
                score += 0.10
        if emails:
            score += 0.10
        return round(min(1.0, score), 2)


verification_service = VerificationService()
