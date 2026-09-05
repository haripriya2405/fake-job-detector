"""Base abstract class for all ingestion medium providers (Phase 8)."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from app.ingestion.schemas import NormalizedJobContent


class BaseIngestor(ABC):
    """Abstract interface for ingesting raw input and converting to NormalizedJobContent."""

    @abstractmethod
    def ingest(self, source_input: Any, metadata: Optional[Dict[str, Any]] = None) -> NormalizedJobContent:
        """Process source input and return standardized normalized job representation.
        Raises ValueError or appropriate exception on malformed/unsupported input.
        """
        pass
