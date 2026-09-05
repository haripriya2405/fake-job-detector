"""Shared entity extraction, text sanitization and normalization utilities (Phase 8).
Extracts URLs, emails, phone numbers, and messaging indicators without leaking sensitive data.
"""

import hashlib
import re
from typing import Dict, List, Set, Tuple
from bs4 import BeautifulSoup
from app.ml.preprocessing import preprocessor


# Regex Patterns for Entity Extraction
_URL_PATTERN = re.compile(r'(?:https?://|www\.)[^\s<>"\'{}|\\^`]+', re.IGNORECASE)
_EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
_PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b|\b(?:\+?91|0)?[6-9]\d{9}\b')
_TELEGRAM_HANDLE_PATTERN = re.compile(r'(?:t\.me/|@)([a-zA-Z0-9_]{5,32})\b', re.IGNORECASE)
_WHATSAPP_PATTERN = re.compile(r'(?:wa\.me/|api\.whatsapp\.com/send\?phone=|\bwhatsapp\b[^\d]*(\+?\d{10,15}))', re.IGNORECASE)
_SIGNAL_PATTERN = re.compile(r'(?:signal\.me/|signal:\s*(\+?\d{10,15}))', re.IGNORECASE)


class ContentSanitizer:
    """Safe extraction of structured entities and cleaning of raw text input."""

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract valid HTTP/HTTPS URLs from raw text."""
        matches = _URL_PATTERN.findall(text)
        urls: List[str] = []
        for m in matches:
            clean = m.rstrip('.,;:)!?"\'')
            if clean.startswith("www."):
                clean = "http://" + clean
            if clean not in urls:
                urls.append(clean)
        return urls

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """Extract email addresses from text."""
        matches = _EMAIL_PATTERN.findall(text)
        emails = list(dict.fromkeys([e.lower().rstrip('.') for e in matches]))
        return emails

    @staticmethod
    def extract_phones(text: str) -> List[str]:
        """Extract candidate phone numbers from text."""
        matches = _PHONE_PATTERN.findall(text)
        phones = list(dict.fromkeys([p.strip() for p in matches if len(p.strip()) >= 10]))
        return phones

    @staticmethod
    def extract_messaging_handles(text: str) -> List[str]:
        """Extract Telegram, WhatsApp, and Signal handles/identifiers."""
        handles: List[str] = []
        
        # Telegram
        for match in _TELEGRAM_HANDLE_PATTERN.finditer(text):
            h = match.group(1) if match.group(1) else match.group(0)
            handles.append(f"telegram:@{h}")
            
        # WhatsApp
        for match in _WHATSAPP_PATTERN.finditer(text):
            h = match.group(1) if match.group(1) else match.group(0)
            handles.append(f"whatsapp:{h}")
            
        # Signal
        for match in _SIGNAL_PATTERN.finditer(text):
            h = match.group(1) if match.group(1) else match.group(0)
            handles.append(f"signal:{h}")

        return list(dict.fromkeys(handles))

    @staticmethod
    def clean_html_to_text(html_content: str) -> str:
        """Strip scripts, styles, navigation and boilerplate tags from HTML, returning visible text."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip unneeded elements
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Normalize excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def normalize_for_ml(raw_text: str) -> str:
        """Normalize raw text using the central TextPreprocessor (preserves fraud entropy cues)."""
        return preprocessor.clean_text(raw_text)

    @staticmethod
    def compute_sha256(content: str | bytes) -> str:
        """Compute SHA-256 hash of text or bytes."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()


sanitizer = ContentSanitizer()
