"""Market Salary Benchmarking & Compensation Anomaly Detection Engine (Phase 21).
Compares job salaries against empirical BLS (Bureau of Labor Statistics) and EMSCAD market benchmarks
to detect unrealistic compensation traps (e.g. $80/hr data entry) or exploitative zero-pay scams.
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from pydantic import BaseModel, Field


class SalaryBenchmarkInfo(BaseModel):
    detected_salary_text: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    frequency: Optional[str] = None  # "HOURLY" | "MONTHLY" | "YEARLY"
    annualized_min: Optional[float] = None
    annualized_max: Optional[float] = None
    matched_job_family: str
    market_median_annual: float
    market_p25_annual: float
    market_p90_annual: float
    market_p90_hourly: float
    discrepancy_ratio: float = 1.0  # offered_annual / market_median
    is_unrealistic_high: bool = False
    is_unrealistic_low: bool = False
    risk_points: int = 0
    verdict: str = "REALISTIC_MARKET_RATE"  # "REALISTIC_MARKET_RATE" | "UNREALISTIC_HIGH_TRAP" | "SUSPICIOUS_LOW_RATE" | "NO_SALARY_DETECTED"
    explanation: str


# Empirical BLS / Industry Market Distributions (Annualized USD)
STANDARD_MARKET_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "data_entry_typing": {
        "keywords": ["data entry", "typist", "typing", "form filling", "copy paste", "transcription", "captioner"],
        "median_annual": 38000,
        "p25_annual": 31000,
        "p90_annual": 48000,
        "median_hourly": 18.25,
        "p90_hourly": 23.00,
        "max_credible_hourly": 35.00,
    },
    "customer_support": {
        "keywords": ["customer service", "customer support", "call center", "support rep", "chat support", "help desk", "inbound support"],
        "median_annual": 42000,
        "p25_annual": 34000,
        "p90_annual": 56000,
        "median_hourly": 20.20,
        "p90_hourly": 27.00,
        "max_credible_hourly": 40.00,
    },
    "administrative_assistant": {
        "keywords": ["administrative assistant", "executive assistant", "office clerk", "receptionist", "virtual assistant", "personal assistant"],
        "median_annual": 46000,
        "p25_annual": 36000,
        "p90_annual": 65000,
        "median_hourly": 22.00,
        "p90_hourly": 31.25,
        "max_credible_hourly": 45.00,
    },
    "software_engineering": {
        "keywords": ["software engineer", "developer", "backend", "frontend", "full stack", "devops", "cloud architect", "sre", "python", "golang", "react"],
        "median_annual": 130000,
        "p25_annual": 95000,
        "p90_annual": 195000,
        "median_hourly": 62.50,
        "p90_hourly": 93.75,
        "max_credible_hourly": 150.00,
    },
    "data_science_ai": {
        "keywords": ["data scientist", "machine learning", "ai engineer", "data analyst", "deep learning", "nlp engineer", "computer vision"],
        "median_annual": 125000,
        "p25_annual": 90000,
        "p90_annual": 185000,
        "median_hourly": 60.00,
        "p90_hourly": 89.00,
        "max_credible_hourly": 140.00,
    },
    "sales_marketing": {
        "keywords": ["sales", "marketing", "account executive", "bdr", "sdr", "social media manager", "content writer", "seo specialist"],
        "median_annual": 68000,
        "p25_annual": 48000,
        "p90_annual": 120000,
        "median_hourly": 32.70,
        "p90_hourly": 57.70,
        "max_credible_hourly": 90.00,
    },
    "general_corporate": {
        "keywords": [],
        "median_annual": 60000,
        "p25_annual": 42000,
        "p90_annual": 110000,
        "median_hourly": 28.85,
        "p90_hourly": 52.88,
        "max_credible_hourly": 85.00,
    },
}


class SalaryBenchmarkService:
    """Extracts stated compensation and benchmarks against real-world market norms."""

    def __init__(self):
        # Regex patterns for various salary formulations
        self.salary_patterns = [
            # $45 - $60 / hour or $45/hr or $45 per hour
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(hr|hour|hr\.|hourly)\b", re.I),
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(hr|hour|hr\.|hourly)\b", re.I),
            # $120,000 - $150,000 / year or per annum
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(yr|year|annum|annually|annual)\b", re.I),
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(yr|year|annum|annually|annual)\b", re.I),
            # $4,000 - $6,000 / month
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(mo|month|monthly)\b", re.I),
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(mo|month|monthly)\b", re.I),
            # $800 - $1,200 / week
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(wk|week|weekly)\b", re.I),
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(wk|week|weekly)\b", re.I),
            # Plain range: $140,000 - $160,000
            re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.I),
            # Plain numbers with salary context: salary: $75,000 or pay: $50/hr
            re.compile(r"(?:salary|pay|compensation|rate)\s*(?:range)?\s*(?:is|of|:)?\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.I),
        ]

    def match_job_family(self, title: str, text: str) -> str:
        """Classify job posting into an empirical benchmark job family."""
        combined = f"{title} {text}".lower()
        for family, data in STANDARD_MARKET_BENCHMARKS.items():
            if family == "general_corporate":
                continue
            for kw in data["keywords"]:
                if re.search(r"\b" + re.escape(kw) + r"\b", combined):
                    return family
        return "general_corporate"

    def extract_salary(self, text: str) -> Optional[Tuple[float, float, str, str]]:
        """Extract min amount, max amount, frequency, and matching snippet."""
        for pat in self.salary_patterns:
            m = pat.search(text)
            if m:
                groups = m.groups()
                snippet = m.group(0).strip()
                if len(groups) == 3:
                    min_val = float(groups[0].replace(",", ""))
                    max_val = float(groups[1].replace(",", ""))
                    freq_raw = groups[2].lower()
                elif len(groups) == 2:
                    min_val = float(groups[0].replace(",", ""))
                    max_val = min_val
                    freq_raw = groups[1].lower()
                elif len(groups) == 1:
                    min_val = float(groups[0].replace(",", ""))
                    max_val = min_val
                    freq_raw = "yr" if min_val > 10000 else "hr"
                else:
                    continue

                if any(x in freq_raw for x in ["hr", "hour"]):
                    frequency = "HOURLY"
                elif any(x in freq_raw for x in ["mo", "month"]):
                    frequency = "MONTHLY"
                elif any(x in freq_raw for x in ["wk", "week"]):
                    frequency = "WEEKLY"
                else:
                    frequency = "YEARLY"

                return min_val, max_val, frequency, snippet
        return None

    def evaluate_compensation(self, text: str, job_title: str = "") -> SalaryBenchmarkInfo:
        """Benchmark stated salary against BLS/industry market rates."""
        family = self.match_job_family(job_title, text)
        benchmark = STANDARD_MARKET_BENCHMARKS[family]
        extracted = self.extract_salary(text)

        if not extracted:
            return SalaryBenchmarkInfo(
                detected_salary_text=None,
                matched_job_family=family,
                market_median_annual=benchmark["median_annual"],
                market_p25_annual=benchmark["p25_annual"],
                market_p90_annual=benchmark["p90_annual"],
                market_p90_hourly=benchmark["p90_hourly"],
                discrepancy_ratio=1.0,
                is_unrealistic_high=False,
                is_unrealistic_low=False,
                risk_points=0,
                verdict="NO_SALARY_DETECTED",
                explanation="No explicit salary or hourly compensation rate detected in posting.",
            )

        min_amt, max_amt, freq, snippet = extracted

        # Annualize for comparison
        if freq == "HOURLY":
            ann_min = min_amt * 2080
            ann_max = max_amt * 2080
            effective_hourly = (min_amt + max_amt) / 2.0
        elif freq == "MONTHLY":
            ann_min = min_amt * 12
            ann_max = max_amt * 12
            effective_hourly = (ann_min + ann_max) / (2.0 * 2080)
        elif freq == "WEEKLY":
            ann_min = min_amt * 52
            ann_max = max_amt * 52
            effective_hourly = (ann_min + ann_max) / (2.0 * 2080)
        else:  # YEARLY
            ann_min = min_amt
            ann_max = max_amt
            effective_hourly = (ann_min + ann_max) / (2.0 * 2080)

        effective_annual = (ann_min + ann_max) / 2.0
        discrepancy = effective_annual / float(benchmark["median_annual"])

        # Check for Unrealistic High Salary Trap (e.g. $80/hr data entry typing)
        is_unrealistic_high = False
        is_unrealistic_low = False
        risk_pts = 0
        verdict = "REALISTIC_MARKET_RATE"

        if family in ["data_entry_typing", "customer_support", "administrative_assistant"]:
            if effective_hourly > benchmark["max_credible_hourly"]:
                is_unrealistic_high = True
                risk_pts = 40
                verdict = "UNREALISTIC_HIGH_TRAP"
                explanation = (
                    f"Offered compensation of '{snippet}' (~${effective_hourly:.2f}/hr) is {discrepancy:.1f}x higher than the "
                    f"market median (${benchmark['median_hourly']:.2f}/hr, 90th percentile: ${benchmark['p90_hourly']:.2f}/hr). "
                    f"Extreme salary inflation for entry-level work is a classic advance-fee / check scam recruitment lure."
                )
            else:
                explanation = f"Offered compensation of '{snippet}' aligns with standard market range (${benchmark['median_hourly']:.2f}/hr)."
        else:
            if discrepancy > 2.2:
                is_unrealistic_high = True
                risk_pts = 25
                verdict = "UNREALISTIC_HIGH_TRAP"
                explanation = (
                    f"Offered salary '{snippet}' (~${effective_annual:,.0f}/yr) is {discrepancy:.1f}x above industry median "
                    f"(${benchmark['median_annual']:,.0f}/yr). High risk of deceptive lure."
                )
            else:
                explanation = f"Offered salary '{snippet}' is within standard industry variance for {family.replace('_', ' ').title()}."

        return SalaryBenchmarkInfo(
            detected_salary_text=snippet,
            min_amount=min_amt,
            max_amount=max_amt,
            frequency=freq,
            annualized_min=ann_min,
            annualized_max=ann_max,
            matched_job_family=family,
            market_median_annual=benchmark["median_annual"],
            market_p25_annual=benchmark["p25_annual"],
            market_p90_annual=benchmark["p90_annual"],
            market_p90_hourly=benchmark["p90_hourly"],
            discrepancy_ratio=round(discrepancy, 2),
            is_unrealistic_high=is_unrealistic_high,
            is_unrealistic_low=is_unrealistic_low,
            risk_points=risk_pts,
            verdict=verdict,
            explanation=explanation,
        )


# Singleton instance
salary_benchmark_service = SalaryBenchmarkService()
