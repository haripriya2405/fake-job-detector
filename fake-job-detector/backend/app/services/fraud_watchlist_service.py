from typing import Any, Dict, List, Optional


class FraudWatchlistService:
    """Cross-references job postings against official FTC, BBB Scam Tracker, and FBI IC3 fraud advisories."""

    # Curated official fraud database advisories
    WATCHLIST_RECORDS = [
        {
            "id": "FTC-ALERT-2024-01",
            "agency": "Federal Trade Commission (FTC)",
            "agency_code": "FTC",
            "title": "Fake Job Offers and Cashier Check Overpayment Scams",
            "threat_type": "CHECK_OVERPAYMENT",
            "keywords": ["cashier check", "certified check", "home office equipment", "equipment vendor", "deposit check"],
            "summary": "Scammers send counterfeit cashier checks to buy home equipment, asking victims to forward extra balance to a vendor before the check bounces.",
            "reference_url": "https://consumer.ftc.gov/articles/job-scams",
            "severity": "CRITICAL",
            "risk_penalty": 25,
        },
        {
            "id": "FTC-ALERT-2024-02",
            "agency": "Federal Trade Commission (FTC)",
            "agency_code": "FTC",
            "title": "Task-Based and Crypto Optimization Rating Scams",
            "threat_type": "CRYPTO_TASK",
            "keywords": ["usdt", "crypto recharge", "task rating", "negative balance", "recharge deposit", "commission withdrawal"],
            "summary": "Fake recruitment lures promising daily wages rating products, requiring escalating cryptocurrency deposits to unlock withdrawal commissions.",
            "reference_url": "https://consumer.ftc.gov/consumer-alerts/2024/03/scammers-are-rating-products-fake-jobs",
            "severity": "CRITICAL",
            "risk_penalty": 25,
        },
        {
            "id": "BBB-TRACKER-2024-03",
            "agency": "Better Business Bureau (BBB)",
            "agency_code": "BBB",
            "title": "Telegram & WhatsApp Remote Interview Impersonation Trap",
            "threat_type": "MESSAGING_INTERVIEW",
            "keywords": ["telegram", "whatsapp interview", "text-only interview", "no video interview", "hiring manager telegram"],
            "summary": "Impostors posing as well-known corporate recruiters conduct text-only screening on Telegram to siphon banking details and upfront fees.",
            "reference_url": "https://www.bbb.org/article/news-releases/23769-bbb-scam-alert-employment-scams",
            "severity": "HIGH",
            "risk_penalty": 20,
        },
        {
            "id": "BBB-TRACKER-2024-04",
            "agency": "Better Business Bureau (BBB)",
            "agency_code": "BBB",
            "title": "Pay-to-Work Upfront Screening & Background Fee Scheme",
            "threat_type": "UPFRONT_FEE",
            "keywords": ["registration fee", "onboarding fee", "software license fee", "screening deposit", "refundable fee"],
            "summary": "Fraudulent job offers requiring applicants to pay upfront registration, background check, or certification fees via peer-to-peer payment apps.",
            "reference_url": "https://www.bbb.org/scamtracker",
            "severity": "HIGH",
            "risk_penalty": 20,
        },
        {
            "id": "IC3-ADVISORY-2024-05",
            "agency": "FBI Internet Crime Complaint Center (IC3)",
            "agency_code": "FBI_IC3",
            "title": "Cyber Criminals Use Spoofed Domains to Steal Personally Identifiable Information",
            "threat_type": "DATA_HARVESTING",
            "keywords": ["driver license", "social security number", "ssn", "voided check", "direct deposit form before interview"],
            "summary": "Threat actors create lookalike domains to harvest applicant SSNs, government IDs, and banking information for synthetic identity theft.",
            "reference_url": "https://www.ic3.gov/Media/Y2023/PSA230321",
            "severity": "HIGH",
            "risk_penalty": 20,
        },
    ]

    def cross_reference_posting(
        self,
        text: str,
        company_name: Optional[str] = None,
        job_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cross-reference text and metadata against FTC, BBB, and FBI IC3 advisories."""
        content = f"{text} {company_name or ''} {job_url or ''}".lower()

        matches = []
        agencies_flagged = set()
        total_penalty = 0

        for record in self.WATCHLIST_RECORDS:
            matched_keywords = [kw for kw in record["keywords"] if kw in content]
            if len(matched_keywords) >= 1:
                matches.append({
                    "id": record["id"],
                    "agency": record["agency"],
                    "agency_code": record["agency_code"],
                    "title": record["title"],
                    "threat_type": record["threat_type"],
                    "summary": record["summary"],
                    "severity": record["severity"],
                    "matched_keywords": matched_keywords,
                    "reference_url": record["reference_url"],
                })
                agencies_flagged.add(record["agency_code"])
                total_penalty += record["risk_penalty"]

        # Cap penalty at 30
        final_penalty = min(30, total_penalty)

        has_match = len(matches) > 0
        status_verdict = "MATCHED_WARNING" if has_match else "CLEAN_PASS"

        return {
            "has_watchlist_matches": has_match,
            "status_verdict": status_verdict,
            "match_count": len(matches),
            "agencies_checked": ["FTC", "BBB", "FBI_IC3"],
            "agencies_flagged": list(agencies_flagged),
            "matches": matches,
            "risk_penalty": final_penalty,
        }

    @classmethod
    def get_all_advisories(cls) -> List[Dict[str, Any]]:
        """Retrieve all active external fraud advisories."""
        return cls.WATCHLIST_RECORDS


fraud_watchlist_service = FraudWatchlistService()

