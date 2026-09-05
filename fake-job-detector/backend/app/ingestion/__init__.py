"""Unified Multi-Modal Ingestion Dispatcher (Phase 8).
Accepts Text, PDF, Image, or Public URL, returning NormalizedJobContent.
"""

from typing import Any, Dict, Optional
from app.ingestion.image import image_ingestor
from app.ingestion.pdf import pdf_ingestor
from app.ingestion.schemas import NormalizedJobContent, SourceType
from app.ingestion.text import text_ingestor
from app.ingestion.url import url_ingestor


def ingest_job_input(
    source_type: SourceType | str,
    source_data: Any,
    metadata: Optional[Dict[str, Any]] = None,
) -> NormalizedJobContent:
    """Dispatches raw job input to the appropriate safe ingestion provider."""
    if isinstance(source_type, str):
        source_type = SourceType(source_type.upper())

    if source_type == SourceType.TEXT:
        return text_ingestor.ingest(source_data, metadata=metadata)
    elif source_type == SourceType.PDF:
        return pdf_ingestor.ingest(source_data, metadata=metadata)
    elif source_type == SourceType.IMAGE:
        return image_ingestor.ingest(source_data, metadata=metadata)
    elif source_type == SourceType.URL:
        return url_ingestor.ingest(source_data, metadata=metadata)
    else:
        raise ValueError(f"Unsupported source type '{source_type}'. Must be one of: TEXT, PDF, IMAGE, URL.")
