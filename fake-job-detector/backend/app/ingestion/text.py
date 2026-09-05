"""Direct text ingestor for raw job postings (Phase 8)."""

from typing import Any, Dict, Optional
from app.ingestion.base import BaseIngestor
from app.ingestion.limits import limits
from app.ingestion.sanitizer import sanitizer
from app.ingestion.schemas import ExtractionEvidenceLocation, NormalizedJobContent, SourceType


class TextIngestor(BaseIngestor):
    """Handles raw pasted job text ingestion."""

    def ingest(self, source_input: str, metadata: Optional[Dict[str, Any]] = None) -> NormalizedJobContent:
        if not source_input or not isinstance(source_input, str):
            raise ValueError("Text input must be a non-empty string.")

        text = source_input.strip()
        if len(text) < limits.MIN_RAW_TEXT_LENGTH:
            raise ValueError(f"Job posting text is too short ({len(text)} chars). Minimum required is {limits.MIN_RAW_TEXT_LENGTH} characters.")

        if len(text) > limits.MAX_RAW_TEXT_LENGTH:
            text = text[:limits.MAX_RAW_TEXT_LENGTH]

        metadata = metadata or {}
        job_title = metadata.get("job_title")
        company_name = metadata.get("company_name")

        normalized = sanitizer.normalize_for_ml(text)
        content_hash = sanitizer.compute_sha256(text)
        urls = sanitizer.extract_urls(text)
        emails = sanitizer.extract_emails(text)
        phones = sanitizer.extract_phones(text)
        handles = sanitizer.extract_messaging_handles(text)

        evidence = [
            ExtractionEvidenceLocation(
                source_type=SourceType.TEXT,
                text_offset_start=0,
                text_offset_end=len(text),
                snippet=text[:250] + ("..." if len(text) > 250 else ""),
                confidence=1.0,
            )
        ]

        return NormalizedJobContent(
            source_type=SourceType.TEXT,
            raw_text=text,
            normalized_text=normalized,
            job_title=job_title,
            company_name=company_name,
            source_identifier=f"text_{content_hash[:12]}",
            content_hash=content_hash,
            file_size_bytes=len(text.encode("utf-8")),
            extraction_method="direct_text",
            extraction_confidence=1.0,
            extracted_urls=urls,
            extracted_emails=emails,
            extracted_phone_numbers=phones,
            extracted_messaging_handles=handles,
            evidence_locations=evidence,
            source_metadata=metadata,
        )


text_ingestor = TextIngestor()
