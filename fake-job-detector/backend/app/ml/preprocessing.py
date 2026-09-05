import re
from typing import List, Optional
import unicodedata


class TextPreprocessor:
    """Production-grade text preprocessor for job fraud NLP classification.
    Cleans raw posting text while deliberately preserving high-signal fraud cues
    (URLs, emails, phone numbers, currency denominations, messaging apps).
    """

    def __init__(
        self,
        lowercase: bool = True,
        normalize_currency: bool = True,
        normalize_contacts: bool = True,
        normalize_urls: bool = True,
        remove_repeated_chars: bool = True,
    ):
        self.lowercase = lowercase
        self.normalize_currency = normalize_currency
        self.normalize_contacts = normalize_contacts
        self.normalize_urls = normalize_urls
        self.remove_repeated_chars = remove_repeated_chars

        # Compiled Regex Patterns
        self.url_pattern = re.compile(
            r'https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)',
            re.IGNORECASE,
        )
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        )
        self.phone_pattern = re.compile(
            r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b'
        )
        # Currency expressions: $, ₹, Rs, INR, USD, €, £, crypto amounts
        self.currency_pattern = re.compile(
            r'([$€£₹]|(?:USD|INR|EUR|GBP|Rs\.?))\s*(\d+(?:,\d{3})*(?:\.\d{1,2})?|\d+)\s*(?:/(?:hr|hour|day|week|month|yr|year|daily|weekly|annum))?',
            re.IGNORECASE,
        )
        # Telegram / social handles: @handle
        self.handle_pattern = re.compile(r'(?<!\w)@([a-zA-Z0-9_]{3,32})\b')
        # Repeated characters (e.g. "freeeeee" -> "free")
        self.repeated_char_pattern = re.compile(r'(.)\1{2,}')
        # Multiple whitespace
        self.whitespace_pattern = re.compile(r'\s+')

    def clean_text(self, text: Optional[str]) -> str:
        """Process a single text document through the normalization pipeline."""
        if not text or not isinstance(text, str):
            return ""

        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Extract / normalize URLs
        if self.normalize_urls:
            normalized = self.url_pattern.sub(" token_url ", normalized)

        # 3. Extract / normalize Emails
        if self.normalize_contacts:
            normalized = self.email_pattern.sub(" token_email ", normalized)

        # 4. Extract / normalize Telegram/Social handles (keep @ indicator signal)
        normalized = self.handle_pattern.sub(r" token_handle \1 ", normalized)

        # 5. Extract / normalize Currency expressions
        if self.normalize_currency:
            normalized = self.currency_pattern.sub(" token_currency ", normalized)

        # 6. Extract / normalize Phone numbers (ensure we don't accidentally match plain single numbers)
        if self.normalize_contacts:
            normalized = self.phone_pattern.sub(" token_phone ", normalized)

        # 7. Repeated characters compression
        if self.remove_repeated_chars:
            normalized = self.repeated_char_pattern.sub(r'\1\1', normalized)

        # 8. Lowercase normalization
        if self.lowercase:
            normalized = normalized.lower()

        # 9. Clean special non-alphanumeric noise while preserving key tokens
        # Keep letters, digits, spaces, and underscore for special tokens
        normalized = re.sub(r'[^a-z0-9_\s]', ' ', normalized)

        # 10. Whitespace collapsing
        cleaned = self.whitespace_pattern.sub(" ", normalized).strip()

        return cleaned

    def transform(self, texts: List[str]) -> List[str]:
        """Batch process a collection of text documents."""
        return [self.clean_text(t) for t in texts]


# Global singleton instance
preprocessor = TextPreprocessor()
