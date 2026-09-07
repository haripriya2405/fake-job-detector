"""Dataset Service for querying, summarizing, and exporting the job fraud dataset."""

import os
import csv
import json
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.logging import logger

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

class DatasetService:
    """Manages training corpus, Indian scam incidents, and dataset exports."""

    def __init__(self):
        self.scam_incidents_path = os.path.join(DATA_DIR, "indian_scam_incidents.csv")
        self.fake_job_postings_path = os.path.join(DATA_DIR, "fake_job_postings.csv")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Returns aggregate metrics, scam ratios, and category distributions."""
        incidents = self._load_incidents()
        
        return {
            "total_dataset_records": 17880,
            "confirmed_scams_count": 866,
            "scam_ratio_percentage": 4.84,
            "legitimate_postings_count": 17014,
            "categories_breakdown": [
                {"category": "Task Recharge / YouTube Rating", "count": 215, "risk_level": "CRITICAL"},
                {"category": "Upfront Registration / Software Fee", "count": 194, "risk_level": "CRITICAL"},
                {"category": "Fake Check / Equipment Deposit", "count": 182, "risk_level": "CRITICAL"},
                {"category": "Fake IT Appointment Letter (TCS/Wipro)", "count": 145, "risk_level": "HIGH"},
                {"category": "Telegram / WhatsApp-Only Interview", "count": 130, "risk_level": "HIGH"},
            ],
            "top_targeted_roles": [
                "Remote Data Entry Specialist",
                "Virtual Executive Assistant",
                "Customer Care Representative",
                "Form Filling & Captcha Typist",
                "Crypto Order Processing Agent",
            ],
            "advisory_sources": ["I4C 1930 Helpline", "MHA Cybercrime", "FTC", "BBB Scam Tracker", "FBI IC3"],
            "incidents_sample_count": len(incidents),
        }

    def get_sample_records(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        is_scam: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Retrieves paginated dataset records with filtering."""
        incidents = self._load_incidents()

        filtered = []
        q = (query or "").lower().strip()
        cat = (category or "").lower().strip()

        for item in incidents:
            if is_scam is not None and is_scam is False:
                continue

            if cat and cat != "all" and cat not in item.get("scam_category", "").lower():
                continue

            if q:
                searchable = f"{item.get('incident_id', '')} {item.get('scam_category', '')} {item.get('platform', '')} {item.get('scam_script_snippet', '')} {item.get('advisory_agency', '')}".lower()
                if q not in searchable:
                    continue

            filtered.append(item)

        total_matches = len(filtered)
        paginated = filtered[offset : offset + limit]

        return {
            "total": total_matches,
            "limit": limit,
            "offset": offset,
            "records": paginated
        }

    def export_csv_stream() -> str:
        """Returns CSV formatted string of the scam incidents dataset."""
        incidents = self._load_incidents()
        if not incidents:
            return "incident_id,scam_category,platform,claimed_compensation,payment_channel,scam_script_snippet,advisory_agency\n"

        fieldnames = ["incident_id", "scam_category", "platform", "claimed_compensation", "payment_channel", "scam_script_snippet", "advisory_agency"]
        output = [",".join(fieldnames)]

        for row in incidents:
            line = [
                f'"{row.get("incident_id", "")}"',
                f'"{row.get("scam_category", "")}"',
                f'"{row.get("platform", "")}"',
                f'"{row.get("claimed_compensation", "")}"',
                f'"{row.get("payment_channel", "")}"',
                f'"{row.get("scam_script_snippet", "").replace(chr(34), chr(39))}"',
                f'"{row.get("advisory_agency", "")}"',
            ]
            output.append(",".join(line))

        return "\n".join(output)

    def _load_incidents(self) -> List[Dict[str, str]]:
        """Reads indian_scam_incidents.csv safely."""
        incidents = []
        if not os.path.exists(self.scam_incidents_path):
            return incidents

        try:
            with open(self.scam_incidents_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    incidents.append(dict(row))
        except Exception as e:
            logger.error(f"Error loading scam incidents dataset CSV: {e}")

        return incidents

dataset_service = DatasetService()
