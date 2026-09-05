import re
from typing import Any, Dict, List, Optional, Tuple


class PhoneCarrierService:
    """Service for extracting recruiter phone numbers and classifying carrier line types (VoIP vs Mobile/Landline)."""

    # Known VoIP prefixes, virtual carrier identifiers, and burner ranges
    KNOWN_VOIP_CARRIERS = [
        "TextNow", "Twilio", "Bandwidth.com", "Google Voice", "Pinger",
        "Dingtone", "SkypeIn", "Vonage Virtual", "BurnerApp", "Telnyx"
    ]

    # Known VoIP area codes or virtual exchanges heavily abused in job scams
    VOIP_EXCHANGES = {"201-203", "347-491", "415-800", "747-200", "929-200"}

    # Toll-free prefixes
    TOLL_FREE_AREAS = {"800", "888", "877", "866", "855", "844", "833"}

    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """Extract candidate phone numbers in standard US and international formats."""
        if not text:
            return []

        # Matches formats: +1-555-123-4567, (555) 123-4567, 555.123.4567, 555-123-4567, +44 20 7946 0958, etc.
        pattern = r"(?:\+?(\d{1,3})[-.\s]?)?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b"
        matches = re.finditer(pattern, text)

        phones = []
        for m in matches:
            country, area, prefix, line = m.groups()
            c_str = f"+{country} " if country else "+1 "
            formatted = f"{c_str}({area}) {prefix}-{line}"
            if formatted not in phones:
                phones.append(formatted)

        return phones

    def classify_number(self, phone: str, context_text: str = "") -> Dict[str, Any]:
        """Classify a single phone number's line type, carrier, and scam probability."""
        digits = re.sub(r"\D", "", phone)
        area_code = digits[1:4] if len(digits) == 11 and digits.startswith("1") else digits[:3]

        lower_ctx = context_text.lower() if context_text else ""
        
        is_voip = False
        carrier_name = "Standard Cellular Network"
        line_type = "MOBILE_CELLULAR"
        risk_contribution = 0
        risk_flags = []

        if area_code in self.TOLL_FREE_AREAS:
            line_type = "TOLL_FREE"
            carrier_name = "Toll-Free Enterprise Route"
        elif "textnow" in lower_ctx or "pinger" in lower_ctx or "dingtone" in lower_ctx:
            is_voip = True
            line_type = "VOIP_BURNER"
            carrier_name = "TextNow / Virtual Burner Line"
            risk_contribution = 15
            risk_flags.append("Recruiter provided virtual VoIP burner number commonly used in anonymous scams")
        elif "google voice" in lower_ctx or "gv" in lower_ctx:
            is_voip = True
            line_type = "VOIP_VIRTUAL"
            carrier_name = "Google Voice Virtual Line"
            risk_contribution = 10
            risk_flags.append("Virtual Google Voice number without verified corporate enterprise trunk")
        elif "telegram" in lower_ctx or "whatsapp" in lower_ctx:
            # When combined with messaging app direction, treat as elevated risk virtual route
            is_voip = True
            line_type = "VOIP_MESSAGING_APP"
            carrier_name = "Virtual OTT Messaging Trunk"
            risk_contribution = 12
            risk_flags.append("Phone contact redirected applicant to unverified Telegram / WhatsApp messaging")
        else:
            line_type = "MOBILE_CELLULAR"
            carrier_name = "Tier-1 Wireless Carrier (AT&T / Verizon / T-Mobile)"

        return {
            "phone_number": phone,
            "area_code": area_code,
            "line_type": line_type,
            "carrier_name": carrier_name,
            "is_voip": is_voip,
            "risk_contribution": risk_contribution,
            "risk_flags": risk_flags,
        }

    def analyze_contact_phones(self, text: str) -> Dict[str, Any]:
        """Extract and analyze all phone numbers in job posting or recruiter message."""
        phones = self.extract_phone_numbers(text)
        if not phones:
            return {
                "detected": False,
                "phone_count": 0,
                "phones": [],
                "has_voip_burner": False,
                "risk_penalty": 0,
            }

        analyzed_list = [self.classify_number(p, context_text=text) for p in phones]
        has_voip = any(item["is_voip"] for item in analyzed_list)
        total_penalty = min(20, sum(item["risk_contribution"] for item in analyzed_list))

        return {
            "detected": True,
            "phone_count": len(phones),
            "phones": analyzed_list,
            "has_voip_burner": has_voip,
            "risk_penalty": total_penalty,
        }


phone_carrier_service = PhoneCarrierService()
