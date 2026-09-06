from typing import Any, Dict, List, Optional


class FraudWatchlistService:
    """Cross-references job postings against official Indian (I4C / Cybercrime.gov.in / 1930 Helpline / RBI)
    and Global (FTC, BBB Scam Tracker, and FBI IC3) fraud advisories.
    """

    # Curated official fraud database advisories
    WATCHLIST_RECORDS = [
        # 🇮🇳 Indian Cybercrime & National Fraud Advisories
        {
            "id": "I4C-MHA-2024-01",
            "agency": "Indian Cyber Crime Coordination Centre (I4C / 1930 Helpline)",
            "agency_code": "I4C_MHA",
            "title": "Part-Time Task & YouTube Video Liking Recharge Fraud",
            "threat_type": "TASK_RECHARGE",
            "keywords": ["like youtube", "like 3 videos", "task recharge", "hotel rating task", "daily commission 2000", "daily task recharge", "earn 3000 daily", "earn 5000 daily"],
            "summary": "Scammers contact victims via WhatsApp/Telegram offering ₹150 for liking videos, then lure them into fake investment task portals demanding escalating UPI/crypto deposits.",
            "reference_url": "https://cybercrime.gov.in",
            "severity": "CRITICAL",
            "risk_penalty": 30,
        },
        {
            "id": "I4C-MHA-2024-02",
            "agency": "National Cyber Crime Reporting Portal (cybercrime.gov.in)",
            "agency_code": "I4C_MHA",
            "title": "Fake Offer Letters & UPI Security Deposit / Gate Pass Scam",
            "threat_type": "UPFRONT_UPI_FEE",
            "keywords": ["gpay", "phonepe", "paytm", "upi id", "gate pass fee", "laptop security deposit", "courier charges before joining", "medical clearance fee", "offer letter verification charge"],
            "summary": "Impostors send forged offer letters from top Indian IT firms (TCS, Infosys, Wipro, Tata) and demand ₹1,500 - ₹15,000 via UPI as refundable security/laptop gate pass deposit.",
            "reference_url": "https://cybercrime.gov.in",
            "severity": "CRITICAL",
            "risk_penalty": 30,
        },
        {
            "id": "RBI-ADVISORY-2024-03",
            "agency": "Reserve Bank of India (RBI) / Consumer Education",
            "agency_code": "RBI",
            "title": "Illegal Work-From-Home Job Loan & Commission Mule Schemes",
            "threat_type": "MONEY_MULE",
            "keywords": ["receive in your account and transfer", "forward upi payment", "commission for receiving funds", "rent your bank account", "kyc document for salary account before interview"],
            "summary": "Fraud networks recruit students and job seekers as money mules by asking them to route unauthorized UPI funds through their personal savings accounts.",
            "reference_url": "https://rbi.org.in",
            "severity": "CRITICAL",
            "risk_penalty": 25,
        },

        # 🌐 Global & US Federal Advisories
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
            "keywords": ["driver license", "social security number", "ssn", "voided check", "direct deposit form before interview", "aadhaar card copy", "pan card upload before interview"],
            "summary": "Threat actors create lookalike domains to harvest applicant government IDs, Aadhaar/PAN details, and banking information for synthetic identity theft.",
            "reference_url": "https://www.ic3.gov/Media/Y2023/PSA230321",
            "severity": "HIGH",
            "risk_penalty": 20,
        },
    ]

    @classmethod
    def get_all_advisories(cls) -> List[Dict[str, Any]]:
        """Return all curated watchlist advisories."""
        return cls.WATCHLIST_RECORDS

    def cross_reference_posting(
        self,
        text: str,
        company_name: Optional[str] = None,
        job_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Cross-reference text and metadata against Indian (I4C/MHA/RBI) and Federal (FTC/BBB/IC3) advisories."""
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

        has_matches = len(matches) > 0
        return {
            "has_watchlist_matches": has_matches,
            "has_watchlist_match": has_matches,
            "status_verdict": "MATCHED_WARNING" if has_matches else "CLEAN_PASS",
            "match_count": len(matches),
            "matches_count": len(matches),
            "agencies_flagged": list(agencies_flagged),
            "risk_penalty": min(40, total_penalty),
            "total_risk_penalty": min(40, total_penalty),
            "matches": matches,
            "matches_found": matches,
            "national_helpline": "1930 (National Cyber Crime Reporting Portal - India)" if any(a.startswith("I4C") or a == "RBI" for a in agencies_flagged) else "Report to FTC / IC3",
        }


# Singleton instance
fraud_watchlist_service = FraudWatchlistService()
