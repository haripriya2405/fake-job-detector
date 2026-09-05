"""OCR base schemas and abstract interface (Phase 8)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OCRBoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float


class OCREvidenceWord(BaseModel):
    text: str
    confidence: float
    bounding_box: Optional[OCRBoundingBox] = None


class OCRResult(BaseModel):
    extracted_text: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    word_count: int
    words: List[OCREvidenceWord] = Field(default_factory=list)
    processing_time_ms: float
    warnings: List[str] = Field(default_factory=list)
    engine_name: str = "Tesseract-OCR"


class BaseOCRService(ABC):
    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> OCRResult:
        """Extract text from raw image bytes safely."""
        pass
