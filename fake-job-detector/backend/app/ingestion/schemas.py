"""Data schemas for normalized multi-modal job ingestion (Phase 8).
Unifies raw text, PDF files, OCR screenshots, and public URLs into a standard interface.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    TEXT = "TEXT"
    PDF = "PDF"
    IMAGE = "IMAGE"
    URL = "URL"


class ExtractionEvidenceLocation(BaseModel):
    source_type: SourceType
    page_number: Optional[int] = None
    bounding_box: Optional[Dict[str, float]] = None  # {x, y, width, height}
    text_offset_start: Optional[int] = None
    text_offset_end: Optional[int] = None
    snippet: str
    confidence: Optional[float] = None


class NormalizedJobContent(BaseModel):
    """Unified representation of ingested job posting content regardless of original input medium."""
    source_type: SourceType
    raw_text: str = Field(..., description="Extracted raw text content")
    normalized_text: str = Field(..., description="Cleaned text ready for ML vectorizer and Rule Engine")
    
    # Metadata
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    source_identifier: str = Field(..., description="Filename, source URL, or raw text hash")
    content_hash: str = Field(..., description="SHA-256 hash of extracted content")
    
    # File / Media Specific Properties
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    page_count: Optional[int] = None
    
    # Extraction Quality
    extraction_method: str = "direct"
    extraction_confidence: float = 1.0
    extraction_warnings: List[str] = Field(default_factory=list)
    
    # Extracted Structured Entities
    extracted_urls: List[str] = Field(default_factory=list)
    extracted_emails: List[str] = Field(default_factory=list)
    extracted_phone_numbers: List[str] = Field(default_factory=list)
    extracted_messaging_handles: List[str] = Field(default_factory=list)
    
    # Location Mapping
    evidence_locations: List[ExtractionEvidenceLocation] = Field(default_factory=list)
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestionProgressStatus(str, Enum):
    UPLOADING = "UPLOADING"
    EXTRACTING = "EXTRACTING"
    OCR_PROCESSING = "OCR_PROCESSING"
    FETCHING_URL = "FETCHING_URL"
    VERIFYING_DOMAIN = "VERIFYING_DOMAIN"
    RUNNING_ANALYSIS = "RUNNING_ANALYSIS"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
