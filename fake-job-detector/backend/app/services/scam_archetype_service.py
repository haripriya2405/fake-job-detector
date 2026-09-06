"""SentinelJob AI — Scam Archetype Classification Engine (Phase 22).

Identifies primary and concurrent secondary deceptive recruitment archetypes
across linguistic patterns, payment channels, PII demands, and task vectors.
"""

from typing import Any, Dict, List, Set, Tuple
from app.llm.schemas import ScamArchetypeEnum


class ScamArchetypeService:
    """Classifies recruitment fraud into standardized threat archetypes."""

    ARCHETYPE_DEFINITIONS: Dict[ScamArchetypeEnum, Dict[str, Any]] = {
        ScamArchetypeEnum.TASK_SCAM: {
            "title": "Task & Optimization Scheme",
            "description": "Requires candidate to perform repetitive tasks (video liking, hotel ratings, merchant order boosting) with deposit demands.",
            "keywords": ["task", "like", "subscribe", "youtube", "rating", "hotel review", "merchant boost", "vip task", "commission level"],
            "severity": "CRITICAL",
        },
        ScamArchetypeEnum.FAKE_CHECK: {
            "title": "Fake Cashier Check & Overpayment",
            "description": "Sends a counterfeit check for home office supplies, instructing the candidate to deposit and wire back funds.",
            "keywords": ["cashier check", "check deposit", "overpayment", "office equipment vendor", "wire remainder", "bitcoin atm", "coinstar"],
            "severity": "CRITICAL",
        },
        ScamArchetypeEnum.ADVANCE_FEE: {
            "title": "Advance-Fee & Security Deposit",
            "description": "Requires upfront payment for training kits, laptop gatepass, uniform clearance, or software license keys.",
            "keywords": ["registration fee", "gatepass", "security deposit", "refundable fee", "software license fee", "training fee", "uniform fee", "processing charge"],
            "severity": "HIGH",
        },
        ScamArchetypeEnum.IDENTITY_HARVEST: {
            "title": "Identity & Credential Harvesting",
            "description": "Demands sensitive identity documents (Aadhaar OTP, SSN, netbanking credentials, passport copies) prior to formal employment.",
            "keywords": ["aadhaar otp", "netbanking password", "debit card pin", "ssn", "social security", "bank credentials", "login password"],
            "severity": "CRITICAL",
        },
        ScamArchetypeEnum.CRYPTO_SCAM: {
            "title": "Cryptocurrency Investment & Wallet Scheme",
            "description": "Requires funds to be deposited into crypto wallets (USDT, BTC) or decentralized task accounts.",
            "keywords": ["usdt", "crypto wallet", "bitcoin", "erc20", "trc20", "recharge wallet", "crypto task"],
            "severity": "CRITICAL",
        },
        ScamArchetypeEnum.PAYMENT_SCAM: {
            "title": "Unauthorized Payment Channel Demands",
            "description": "Solicits funds through consumer peer-to-peer payment apps (UPI, GPay, PhonePe, Paytm, Zelle, CashApp, Venmo).",
            "keywords": ["upi id", "gpay", "phonepe", "paytm", "zelle", "cashapp", "venmo", "western union", "moneygram"],
            "severity": "HIGH",
        },
        ScamArchetypeEnum.IMPERSONATION: {
            "title": "Corporate Brand & Executive Impersonation",
            "description": "Spoofs prominent enterprises (TCS, Infosys, Wipro, Google, Microsoft, Amazon) using lookalike domains or free webmail.",
            "keywords": ["tcs", "infosys", "wipro", "tata", "microsoft", "google", "amazon", "apple", "deloitte"],
            "severity": "HIGH",
        },
        ScamArchetypeEnum.FAKE_RECRUITER: {
            "title": "Unverified / Ghost Recruiter",
            "description": "Presents as a hiring manager using personal webmail (@gmail.com, @yahoo.com) and redirects candidates to unmoderated messaging apps.",
            "keywords": ["telegram", "whatsapp", "@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com"],
            "severity": "MEDIUM",
        },
        ScamArchetypeEnum.RESHIPPING: {
            "title": "Package Mule & Reshipping Scheme",
            "description": "Employs candidate to receive goods purchased with stolen credit cards and reship them internationally.",
            "keywords": ["package inspector", "reshipping", "forward parcels", "receive luxury goods", "repackage merchandise"],
            "severity": "CRITICAL",
        },
        ScamArchetypeEnum.GHOST_JOB: {
            "title": "Deceptive Ghost Listing",
            "description": "Non-existent role advertised solely to harvest applicant contact lists and resumes for spam marketing.",
            "keywords": ["instant hiring", "no interview needed", "guaranteed placement", "unlimited vacancies"],
            "severity": "LOW",
        },
        ScamArchetypeEnum.INVESTMENT_SCAM: {
            "title": "High-Yield Employment Investment Fraud",
            "description": "Promises high daily returns or profit sharing under the guise of part-time remote employment.",
            "keywords": ["daily return", "high yield", "guaranteed profit", "investment commission", "earn 10% profit daily"],
            "severity": "CRITICAL",
        },
    }

    def classify_archetypes(
        self,
        raw_text: str,
        risk_score: int = 0,
        rule_codes: List[str] = None,
    ) -> Tuple[ScamArchetypeEnum, List[ScamArchetypeEnum]]:
        """Determines primary and secondary threat archetypes based on multi-signal matching."""
        text_lower = raw_text.lower()
        rules_set = set(rule_codes or [])
        matched_scores: Dict[ScamArchetypeEnum, int] = {}

        # 1. Evaluate Rule Codes
        for code in rules_set:
            if "UPI" in code or "QR" in code:
                matched_scores[ScamArchetypeEnum.PAYMENT_SCAM] = matched_scores.get(ScamArchetypeEnum.PAYMENT_SCAM, 0) + 40
            if "FEE" in code or "REGISTRATION" in code:
                matched_scores[ScamArchetypeEnum.ADVANCE_FEE] = matched_scores.get(ScamArchetypeEnum.ADVANCE_FEE, 0) + 40
            if "TASK" in code or "VIP" in code:
                matched_scores[ScamArchetypeEnum.TASK_SCAM] = matched_scores.get(ScamArchetypeEnum.TASK_SCAM, 0) + 40
            if "CHECK" in code or "CASHIER" in code:
                matched_scores[ScamArchetypeEnum.FAKE_CHECK] = matched_scores.get(ScamArchetypeEnum.FAKE_CHECK, 0) + 50
            if "AADHAAR" in code or "PAN" in code or "SSN" in code:
                matched_scores[ScamArchetypeEnum.IDENTITY_HARVEST] = matched_scores.get(ScamArchetypeEnum.IDENTITY_HARVEST, 0) + 50
            if "IMPERSONATION" in code:
                matched_scores[ScamArchetypeEnum.IMPERSONATION] = matched_scores.get(ScamArchetypeEnum.IMPERSONATION, 0) + 35
            if "CRYPTO" in code:
                matched_scores[ScamArchetypeEnum.CRYPTO_SCAM] = matched_scores.get(ScamArchetypeEnum.CRYPTO_SCAM, 0) + 40

        # 2. Evaluate Keywords
        for archetype, defs in self.ARCHETYPE_DEFINITIONS.items():
            for kw in defs["keywords"]:
                if kw in text_lower:
                    matched_scores[archetype] = matched_scores.get(archetype, 0) + 15

        if not matched_scores or risk_score < 25:
            return ScamArchetypeEnum.OTHER, []

        # Sort by score descending
        sorted_archetypes = sorted(matched_scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_archetypes[0][0]
        secondary = [arch for arch, score in sorted_archetypes[1:4] if score >= 20 and arch != primary]

        return primary, secondary


scam_archetype_service = ScamArchetypeService()
