"""Ingestion limits and resource constraints for SentinelJob AI (Phase 8).
Prevents Denial-of-Service, memory exhaustion, decompression bombs, and infinite redirect loops.
"""

from pydantic import BaseModel


class IngestionLimits(BaseModel):
    # File Size Limits
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    MAX_RAW_TEXT_LENGTH: int = 100_000  # 100,000 characters
    MIN_RAW_TEXT_LENGTH: int = 20  # Minimum 20 characters

    # PDF Constraints
    MAX_PDF_PAGES: int = 20
    PDF_EXTRACTION_TIMEOUT_SECONDS: float = 8.0

    # Image / OCR Constraints
    MAX_IMAGE_WIDTH: int = 4096
    MAX_IMAGE_HEIGHT: int = 4096
    MAX_IMAGE_PIXELS: int = 16_000_000  # 16 Megapixels
    OCR_PROCESSING_TIMEOUT_SECONDS: float = 10.0
    LOW_OCR_CONFIDENCE_THRESHOLD: float = 0.50

    # Web URL / Network Constraints
    MAX_URL_RESPONSE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    MAX_EXTRACTED_HTML_TEXT_BYTES: int = 1 * 1024 * 1024  # 1 MB
    MAX_REDIRECT_HOPS: int = 5
    HTTP_CONNECT_TIMEOUT_SECONDS: float = 5.0
    HTTP_READ_TIMEOUT_SECONDS: float = 8.0

    # Allowed MIME Types
    ALLOWED_IMAGE_MIMES: tuple = (
        "image/png",
        "image/jpeg",
        "image/pjpeg",
        "image/webp",
    )
    ALLOWED_PDF_MIMES: tuple = (
        "application/pdf",
        "application/x-pdf",
    )


limits = IngestionLimits()
