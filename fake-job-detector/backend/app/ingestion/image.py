"""Image and Screenshot Ingestor using OCR extraction (Phase 8)."""

from typing import Any, Dict, Optional
from app.core.logging import logger
from app.ingestion.base import BaseIngestor
from app.ingestion.limits import limits
from app.ingestion.sanitizer import sanitizer
from app.ingestion.schemas import (
    ExtractionEvidenceLocation,
    NormalizedJobContent,
    SourceType,
)
from app.ocr.preprocessing import image_preprocessor
from app.ocr.service import ocr_service


class ImageIngestor(BaseIngestor):
    """Safely decodes job screenshot images, runs OCR, and extracts structured entities."""

    def ingest(self, source_input: bytes, metadata: Optional[Dict[str, Any]] = None) -> NormalizedJobContent:
        if not source_input or not isinstance(source_input, bytes):
            raise ValueError("Image input must be non-empty bytes.")

        if len(source_input) > limits.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"Image exceeds maximum size limit of {limits.MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB.")

        # Validate format integrity immediately
        image_preprocessor.validate_and_load(source_input)

        metadata = metadata or {}
        filename = metadata.get("filename", "screenshot.png")
        mime_type = metadata.get("mime_type", "image/png")
        content_hash = sanitizer.compute_sha256(source_input)

        ocr_res = ocr_service.extract_text(source_input)
        raw_text = ocr_res.extracted_text.strip()
        warnings = list(ocr_res.warnings)

        if not raw_text:
            if not warnings:
                warnings.append("No readable text could be extracted from the uploaded image.")
            raw_text = "[No readable text extracted from image]"

        normalized = sanitizer.normalize_for_ml(raw_text)
        urls = sanitizer.extract_urls(raw_text)
        emails = sanitizer.extract_emails(raw_text)
        phones = sanitizer.extract_phones(raw_text)
        handles = sanitizer.extract_messaging_handles(raw_text)

        evidence_locations = []
        for word in ocr_res.words[:20]:  # Capture key word locations
            bbox_dict = None
            if word.bounding_box:
                bbox_dict = {
                    "x": word.bounding_box.x,
                    "y": word.bounding_box.y,
                    "width": word.bounding_box.width,
                    "height": word.bounding_box.height,
                }
            evidence_locations.append(
                ExtractionEvidenceLocation(
                    source_type=SourceType.IMAGE,
                    snippet=word.text,
                    bounding_box=bbox_dict,
                    confidence=word.confidence,
                )
            )

        return NormalizedJobContent(
            source_type=SourceType.IMAGE,
            raw_text=raw_text,
            normalized_text=normalized,
            job_title=metadata.get("job_title"),
            company_name=metadata.get("company_name"),
            source_identifier=filename,
            content_hash=content_hash,
            original_filename=filename,
            mime_type=mime_type,
            file_size_bytes=len(source_input),
            extraction_method="tesseract_ocr",
            extraction_confidence=ocr_res.confidence,
            extraction_warnings=warnings,
            extracted_urls=urls,
            extracted_emails=emails,
            extracted_phone_numbers=phones,
            extracted_messaging_handles=handles,
            evidence_locations=evidence_locations,
            source_metadata={
                **metadata,
                "ocr_word_count": ocr_res.word_count,
                "ocr_processing_time_ms": ocr_res.processing_time_ms,
            },
        )


image_ingestor = ImageIngestor()
