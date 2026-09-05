from abc import ABC, abstractmethod
from typing import Any, Dict, List


class NLPService(ABC):
    """Abstract interface for text preprocessing, tokenization, and TF-IDF extraction."""

    @abstractmethod
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize raw text."""
        pass

    @abstractmethod
    def extract_features(self, text: str) -> Any:
        """Extract vectorized features for downstream ML classification."""
        pass
