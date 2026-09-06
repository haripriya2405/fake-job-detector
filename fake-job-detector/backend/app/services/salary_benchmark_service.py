"""Market Salary Benchmarking & Compensation Anomaly Detection Engine (Phase 21 - India & Global Dual Currency).
Compares job salaries against empirical Indian Market benchmarks (NASSCOM / AmbitionBox in INR/LPA)
and US BLS (Bureau of Labor Statistics in USD) to detect unrealistic compensation traps (e.g. ₹5,000/day data entry or $80/hr typing).
"""

from typing import Any, Dict, List, Optional, Tuple
import re
from pydantic import BaseModel, Field


class SalaryBenchmarkInfo(BaseModel):
    detected_salary_text: Optional[str] = None
    currency: str = "USD"  # "INR" | "USD"
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    frequency: Optional[str] = None  # "HOURLY" | "DAILY" | "MONTHLY" | "YEARLY" | "LPA"
    annualized_min: Optional[float] = None
    annualized_max: Optional[float] = None
    matched_job_family: str
    market_median_annual: float
    market_p25_annual: float
    market_p90_annual: float
    market_p90_hourly: Optional[float] = None
    discrepancy_ratio: float = 1.0  # offered_annual / market_median
    is_unrealistic_high: bool = False
    is_unrealistic_low: bool = False
    risk_points: int = 0
    verdict: str = "REALISTIC_MARKET_RATE"  # "REALISTIC_MARKET_RATE" | "UNREALISTIC_HIGH_TRAP" | "SUSPICIOUS_LOW_RATE" | "NO_SALARY_DETECTED"
    explanation: str


# 🇮🇳 Indian Market Benchmarks (Annualized INR in ₹)
INDIAN_MARKET_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "data_entry_typing": {
        "keywords": ["data entry", "typist", "typing", "form filling", "copy paste", "transcription", "captioner", "sms sending", "captcha"],
        "median_annual": 240000,  # ₹2.4 LPA (~₹20,000/mo)
        "p25_annual": 180000,     # ₹1.8 LPA (~₹15,000/mo)
        "p90_annual": 360000,     # ₹3.6 LPA (~₹30,000/mo)
        "max_credible_monthly": 45000,  # > ₹45,000/mo for data entry is almost certainly a scam
        "max_credible_daily": 1500,     # > ₹1,500/day for data entry is a classic scam lure
        "max_credible_annual": 500000,  # 5 LPA max
    },
    "customer_support": {
        "keywords": ["customer service", "customer support", "call center", "bpo", "telecaller", "telecalling", "support rep", "chat support", "help desk", "inbound support"],
        "median_annual": 300000,  # ₹3.0 LPA (~₹25,000/mo)
        "p25_annual": 220000,     # ₹2.2 LPA
        "p90_annual": 480000,     # ₹4.8 LPA (~₹40,000/mo)
        "max_credible_monthly": 60000,
        "max_credible_daily": 2000,
        "max_credible_annual": 700000,
    },
    "administrative_assistant": {
        "keywords": ["administrative assistant", "executive assistant", "office clerk", "receptionist", "virtual assistant", "personal assistant", "back office"],
        "median_annual": 360000,  # ₹3.6 LPA (~₹30,000/mo)
        "p25_annual": 250000,     # ₹2.5 LPA
        "p90_annual": 550000,     # ₹5.5 LPA
        "max_credible_monthly": 65000,
        "max_credible_daily": 2200,
        "max_credible_annual": 750000,
    },
    "software_engineering": {
        "keywords": ["software engineer", "developer", "backend", "frontend", "full stack", "devops", "cloud architect", "sre", "python", "golang", "react", "java", "node", "mern"],
        "median_annual": 950000,  # 9.5 LPA
        "p25_annual": 500000,     # 5.0 LPA
        "p90_annual": 2500000,    # 25.0 LPA
        "max_credible_monthly": 400000,
        "max_credible_daily": 15000,
        "max_credible_annual": 5000000,
    },
    "data_science_ai": {
        "keywords": ["data scientist", "machine learning", "ai engineer", "data analyst", "deep learning", "nlp engineer", "computer vision", "business analyst"],
        "median_annual": 1100000,  # 11.0 LPA
        "p25_annual": 600000,      # 6.0 LPA
        "p90_annual": 2800000,     # 28.0 LPA
        "max_credible_monthly": 450000,
        "max_credible_daily": 18000,
        "max_credible_annual": 6000000,
    },
    "sales_marketing": {
        "keywords": ["sales", "marketing", "business development", "bde", "bdr", "sdr", "social media manager", "content writer", "seo specialist", "digital marketing"],
        "median_annual": 450000,  # 4.5 LPA
        "p25_annual": 280000,     # 2.8 LPA
        "p90_annual": 1200000,    # 12.0 LPA
        "max_credible_monthly": 150000,
        "max_credible_daily": 5000,
        "max_credible_annual": 2000000,
    },
    "general_corporate": {
        "keywords": [],
        "median_annual": 480000,  # 4.8 LPA
        "p25_annual": 300000,     # 3.0 LPA
        "p90_annual": 1200000,    # 12.0 LPA
        "max_credible_monthly": 120000,
        "max_credible_daily": 4000,
        "max_credible_annual": 1800000,
    },
}

# 🇺🇸 US BLS Empirical Market Distributions (Annualized USD in $)
STANDARD_MARKET_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "data_entry_typing": {
        "keywords": ["data entry", "typist", "typing", "form filling", "copy paste", "transcription", "captioner"],
        "median_annual": 38000,
        "p25_annual": 31000,
        "p90_annual": 48000,
        "median_hourly": 18.25,
        "p90_hourly": 23.00,
        "max_credible_hourly": 35.00,
        "max_credible_monthly": 4500,
        "max_credible_daily": 200,
        "max_credible_annual": 60000,
    },
    "customer_support": {
        "keywords": ["customer service", "customer support", "call center", "support rep", "chat support", "help desk", "inbound support"],
        "median_annual": 42000,
        "p25_annual": 34000,
        "p90_annual": 56000,
        "median_hourly": 20.20,
        "p90_hourly": 27.00,
        "max_credible_hourly": 40.00,
        "max_credible_monthly": 5500,
        "max_credible_daily": 250,
        "max_credible_annual": 75000,
    },
    "administrative_assistant": {
        "keywords": ["administrative assistant", "executive assistant", "office clerk", "receptionist", "virtual assistant", "personal assistant"],
        "median_annual": 46000,
        "p25_annual": 36000,
        "p90_annual": 65000,
        "median_hourly": 22.00,
        "p90_hourly": 31.25,
        "max_credible_hourly": 45.00,
        "max_credible_monthly": 6000,
        "max_credible_daily": 300,
        "max_credible_annual": 85000,
    },
    "software_engineering": {
        "keywords": ["software engineer", "developer", "backend", "frontend", "full stack", "devops", "cloud architect", "sre", "python", "golang", "react"],
        "median_annual": 130000,
        "p25_annual": 95000,
        "p90_annual": 195000,
        "median_hourly": 62.50,
        "p90_hourly": 93.75,
        "max_credible_hourly": 150.00,
        "max_credible_monthly": 20000,
        "max_credible_daily": 1000,
        "max_credible_annual": 280000,
    },
    "data_science_ai": {
        "keywords": ["data scientist", "machine learning", "ai engineer", "data analyst", "deep learning", "nlp engineer", "computer vision"],
        "median_annual": 125000,
        "p25_annual": 90000,
        "p90_annual": 185000,
        "median_hourly": 60.00,
        "p90_hourly": 89.00,
        "max_credible_hourly": 140.00,
        "max_credible_monthly": 19000,
        "max_credible_daily": 950,
        "max_credible_annual": 260000,
    },
    "sales_marketing": {
        "keywords": ["sales", "marketing", "account executive", "bdr", "sdr", "social media manager", "content writer", "seo specialist"],
        "median_annual": 68000,
        "p25_annual": 48000,
        "p90_annual": 120000,
        "median_hourly": 32.70,
        "p90_hourly": 57.70,
        "max_credible_hourly": 90.00,
        "max_credible_monthly": 12000,
        "max_credible_daily": 600,
        "max_credible_annual": 160000,
    },
    "general_corporate": {
        "keywords": [],
        "median_annual": 60000,
        "p25_annual": 42000,
        "p90_annual": 110000,
        "median_hourly": 28.85,
        "p90_hourly": 52.88,
        "max_credible_hourly": 85.00,
        "max_credible_monthly": 10000,
        "max_credible_daily": 500,
        "max_credible_annual": 150000,
    },
}


class SalaryBenchmarkService:
    """Extracts stated compensation and benchmarks against real-world Indian (INR/LPA) and Global (USD) market norms."""

    def __init__(self):
        # 🇮🇳 Indian INR & LPA Formulations Regex
        self.inr_patterns = [
            # 3.5 - 6 LPA / 8 LPA - 12 LPA / 3.5 to 6 Lakhs
            (re.compile(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lacs?)?\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lacs?)(?:\s*(?:per\s*annum|pa|p\.a\.|\/year))?", re.I), "LPA"),
            (re.compile(r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lacs?)(?:\s*(?:per\s*annum|pa|p\.a\.|\/year))?", re.I), "LPA"),
            # ₹25,000 - ₹35,000 / month or Rs. 25,000 pm or INR 25000
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(mo|month|monthly|pm|p\.m\.)\b", re.I), "MONTHLY"),
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(mo|month|monthly|pm|p\.m\.)\b", re.I), "MONTHLY"),
            # ₹2,000 - ₹5,000 / day (Classic Indian Data Entry Scam Trap)
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(day|daily|per\s+day)\b", re.I), "DAILY"),
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(day|daily|per\s+day)\b", re.I), "DAILY"),
            # ₹3,00,000 - ₹6,00,000 / year or per annum
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(yr|year|annum|annually|annual|pa|p\.a\.)\b", re.I), "YEARLY"),
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(yr|year|annum|annually|annual|pa|p\.a\.)\b", re.I), "YEARLY"),
            # Plain ₹ range: ₹25,000 - ₹50,000
            (re.compile(r"(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)\s*(?:-|to)\s*(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)", re.I), "AUTO"),
            # Context match: salary: ₹40,000
            (re.compile(r"(?:salary|pay|ctc|stipend|compensation)\s*(?:range)?\s*(?:is|of|:)?\s*(?:₹|rs\.?|inr)\s*(\d{1,3}(?:,\d{2,3})*(?:\.\d{2})?)", re.I), "AUTO"),
        ]

        # 🇺🇸 USD Formulations Regex
        self.usd_patterns = [
            # $45 - $60 / hour or $45/hr
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(hr|hour|hr\.|hourly)\b", re.I), "HOURLY"),
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(hr|hour|hr\.|hourly)\b", re.I), "HOURLY"),
            # $120,000 - $150,000 / year or per annum
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(yr|year|annum|annually|annual)\b", re.I), "YEARLY"),
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(yr|year|annum|annually|annual)\b", re.I), "YEARLY"),
            # $4,000 - $6,000 / month
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(mo|month|monthly)\b", re.I), "MONTHLY"),
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(mo|month|monthly)\b", re.I), "MONTHLY"),
            # $800 - $1,200 / week
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+|\s+)?(wk|week|weekly)\b", re.I), "WEEKLY"),
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)(?:\s*/\s*|\s+per\s+)(wk|week|weekly)\b", re.I), "WEEKLY"),
            # Plain range: $140,000 - $160,000
            (re.compile(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:-|to)\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.I), "AUTO"),
            # Plain numbers with salary context: salary: $75,000
            (re.compile(r"(?:salary|pay|compensation|rate)\s*(?:range)?\s*(?:is|of|:)?\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.I), "AUTO"),
        ]

    def match_job_family(self, title: str, text: str, is_inr: bool = False) -> str:
        """Classify job posting into an empirical benchmark job family."""
        combined = f"{title} {text}".lower()
        benchmarks = INDIAN_MARKET_BENCHMARKS if is_inr else STANDARD_MARKET_BENCHMARKS
        for family, data in benchmarks.items():
            if family == "general_corporate":
                continue
            for kw in data["keywords"]:
                if re.search(r"\b" + re.escape(kw) + r"\b", combined):
                    return family
        return "general_corporate"

    def _parse_num(self, val: Optional[str]) -> Optional[float]:
        if not val:
            return None
        try:
            return float(str(val).replace(",", "").strip())
        except (ValueError, TypeError):
            return None

    def extract_salary(self, text: str) -> Optional[Tuple[float, float, str, str, str]]:
        """Extract min amount, max amount, frequency, currency, and matching snippet."""
        # 1. Check Indian INR formulations first
        for pat, default_freq in self.inr_patterns:
            m = pat.search(text)
            if m:
                groups = m.groups()
                snippet = m.group(0).strip()
                if default_freq == "LPA":
                    min_val = self._parse_num(groups[0])
                    max_val = self._parse_num(groups[1]) if (len(groups) > 1 and groups[1]) else min_val
                    if min_val is not None:
                        return min_val, max_val or min_val, "LPA", "INR", snippet

                parsed_numbers = []
                freq_raw = default_freq
                for g in groups:
                    if g is None:
                        continue
                    n = self._parse_num(g)
                    if n is not None:
                        parsed_numbers.append(n)
                    else:
                        freq_raw = g.lower()

                if not parsed_numbers:
                    continue

                min_val = parsed_numbers[0]
                max_val = parsed_numbers[1] if len(parsed_numbers) > 1 else min_val

                if default_freq in ["MONTHLY", "DAILY", "YEARLY"]:
                    frequency = default_freq
                elif any(x in str(freq_raw) for x in ["day", "daily"]):
                    frequency = "DAILY"
                elif any(x in str(freq_raw) for x in ["mo", "month", "pm"]):
                    frequency = "MONTHLY"
                elif any(x in str(freq_raw) for x in ["yr", "year", "annum", "pa"]):
                    frequency = "YEARLY"
                else:
                    frequency = "MONTHLY" if min_val <= 100000 else "YEARLY"

                return min_val, max_val, frequency, "INR", snippet

        # 2. Check USD formulations
        for pat, default_freq in self.usd_patterns:
            m = pat.search(text)
            if m:
                groups = m.groups()
                snippet = m.group(0).strip()
                parsed_numbers = []
                freq_raw = default_freq
                for g in groups:
                    if g is None:
                        continue
                    n = self._parse_num(g)
                    if n is not None:
                        parsed_numbers.append(n)
                    else:
                        freq_raw = g.lower()

                if not parsed_numbers:
                    continue

                min_val = parsed_numbers[0]
                max_val = parsed_numbers[1] if len(parsed_numbers) > 1 else min_val

                if default_freq in ["HOURLY", "MONTHLY", "WEEKLY", "YEARLY"]:
                    frequency = default_freq
                elif any(x in str(freq_raw) for x in ["hr", "hour"]):
                    frequency = "HOURLY"
                elif any(x in str(freq_raw) for x in ["mo", "month"]):
                    frequency = "MONTHLY"
                elif any(x in str(freq_raw) for x in ["wk", "week"]):
                    frequency = "WEEKLY"
                else:
                    frequency = "YEARLY" if min_val > 10000 else "HOURLY"

                return min_val, max_val, frequency, "USD", snippet

        return None

    def evaluate_compensation(self, text: str, job_title: str = "") -> SalaryBenchmarkInfo:
        """Benchmark stated salary against Indian (INR) or Global (USD) market rates."""
        extracted = self.extract_salary(text)

        if not extracted:
            # Default to INR baseline for general queries
            is_inr = bool(re.search(r"\b(india|noida|bangalore|bengaluru|mumbai|delhi|hyderabad|pune|chennai|gurgaon|kolkata|lpa|inr|rs|₹)\b", f"{job_title} {text}", re.I))
            family = self.match_job_family(job_title, text, is_inr=is_inr)
            benchmark = INDIAN_MARKET_BENCHMARKS[family] if is_inr else STANDARD_MARKET_BENCHMARKS[family]
            curr_sym = "₹" if is_inr else "$"

            return SalaryBenchmarkInfo(
                detected_salary_text=None,
                currency="INR" if is_inr else "USD",
                matched_job_family=family,
                market_median_annual=benchmark["median_annual"],
                market_p25_annual=benchmark["p25_annual"],
                market_p90_annual=benchmark["p90_annual"],
                market_p90_hourly=benchmark.get("p90_hourly"),
                discrepancy_ratio=1.0,
                is_unrealistic_high=False,
                is_unrealistic_low=False,
                risk_points=0,
                verdict="NO_SALARY_DETECTED",
                explanation=f"No explicit salary or compensation rate detected in posting. (Standard median: {curr_sym}{benchmark['median_annual']:,}/yr).",
            )

        min_amt, max_amt, freq, currency, snippet = extracted
        is_inr = (currency == "INR")
        family = self.match_job_family(job_title, text, is_inr=is_inr)
        benchmark = INDIAN_MARKET_BENCHMARKS[family] if is_inr else STANDARD_MARKET_BENCHMARKS[family]
        curr_sym = "₹" if is_inr else "$"

        # Annualize based on frequency and currency
        if freq == "LPA":
            ann_min = min_amt * 100000
            ann_max = max_amt * 100000
        elif freq == "DAILY":
            ann_min = min_amt * 260  # ~260 working days/yr
            ann_max = max_amt * 260
        elif freq == "MONTHLY":
            ann_min = min_amt * 12
            ann_max = max_amt * 12
        elif freq == "WEEKLY":
            ann_min = min_amt * 52
            ann_max = max_amt * 52
        elif freq == "HOURLY":
            ann_min = min_amt * 2080
            ann_max = max_amt * 2080
        else:  # YEARLY
            ann_min = min_amt
            ann_max = max_amt

        effective_annual = (ann_min + ann_max) / 2.0
        effective_monthly = effective_annual / 12.0
        discrepancy = effective_annual / float(benchmark["median_annual"])

        # Check for Unrealistic High Salary Trap (e.g. ₹5,000/day data entry or $80/hr typing)
        is_unrealistic_high = False
        is_unrealistic_low = False
        risk_pts = 0
        verdict = "REALISTIC_MARKET_RATE"

        if is_inr:
            # Indian Market Anomaly Rules
            if family in ["data_entry_typing", "customer_support", "administrative_assistant"]:
                if effective_monthly > benchmark.get("max_credible_monthly", 45000) or effective_annual > benchmark.get("max_credible_annual", 500000):
                    is_unrealistic_high = True
                    risk_pts = 40
                    verdict = "UNREALISTIC_HIGH_TRAP"
                    explanation = (
                        f"Offered compensation of '{snippet}' (~₹{effective_monthly:,.0f}/month or {effective_annual/100000:.1f} LPA) is {discrepancy:.1f}x higher than the "
                        f"Indian market median (₹{benchmark['median_annual']/100000:.1f} LPA, ~₹{benchmark['median_annual']/12:,.0f}/mo). "
                        f"Offering inflated wages for entry-level typing/form filling is a classic Indian job scam (demanding registration or security fees)."
                    )
                else:
                    explanation = f"Offered compensation of '{snippet}' aligns with standard Indian market compensation (Median: ₹{benchmark['median_annual']/100000:.1f} LPA)."
            else:
                if discrepancy > 2.3:
                    is_unrealistic_high = True
                    risk_pts = 25
                    verdict = "UNREALISTIC_HIGH_TRAP"
                    explanation = (
                        f"Offered salary '{snippet}' (~{effective_annual/100000:.1f} LPA) is {discrepancy:.1f}x above Indian industry median "
                        f"({benchmark['median_annual']/100000:.1f} LPA). High risk of deceptive recruitment lure."
                    )
                else:
                    explanation = f"Offered salary '{snippet}' is within standard Indian industry variance for {family.replace('_', ' ').title()}."
        else:
            # US / Global USD Anomaly Rules
            effective_hourly = (min_amt + max_amt) / 2.0 if freq == "HOURLY" else effective_annual / 2080.0
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
            currency=currency,
            min_amount=min_amt,
            max_amount=max_amt,
            frequency=freq,
            annualized_min=ann_min,
            annualized_max=ann_max,
            matched_job_family=family,
            market_median_annual=benchmark["median_annual"],
            market_p25_annual=benchmark["p25_annual"],
            market_p90_annual=benchmark["p90_annual"],
            market_p90_hourly=benchmark.get("p90_hourly"),
            discrepancy_ratio=round(discrepancy, 2),
            is_unrealistic_high=is_unrealistic_high,
            is_unrealistic_low=is_unrealistic_low,
            risk_points=risk_pts,
            verdict=verdict,
            explanation=explanation,
        )


# Singleton instance
salary_benchmark_service = SalaryBenchmarkService()
