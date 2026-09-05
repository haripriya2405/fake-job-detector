"""Safe Public Job URL Fetcher & HTML Ingestor (Phase 8).
Enforces strict SSRF firewall validation before initial request and after EVERY redirect hop.
Strips scripts, tracking, styles, and navigation boilerplate to produce clean job text.
"""

from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

from app.core.logging import logger
from app.ingestion.base import BaseIngestor
from app.ingestion.limits import limits
from app.ingestion.sanitizer import sanitizer
from app.ingestion.schemas import (
    ExtractionEvidenceLocation,
    NormalizedJobContent,
    SourceType,
)
from app.verification.ssrf import ssrf_protection


class UrlIngestor(BaseIngestor):
    """Safely retrieves public web job postings with end-to-end SSRF protection."""

    def ingest(self, source_input: str, metadata: Optional[Dict[str, Any]] = None) -> NormalizedJobContent:
        if not source_input or not isinstance(source_input, str):
            raise ValueError("URL input must be a non-empty string.")

        target_url = source_input.strip()
        parsed_scheme = urlparse(target_url).scheme.lower()
        if parsed_scheme and parsed_scheme not in ["http", "https"]:
            raise ValueError(f"URL security violation: Forbidden protocol '{parsed_scheme}'. Only HTTP and HTTPS URLs are permitted.")

        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        metadata = metadata or {}
        warnings: List[str] = []

        # 1. Initial SSRF Firewall Validation
        ssrf_res = ssrf_protection.validate_url(target_url)
        if not ssrf_res.is_safe:
            raise ValueError(f"URL security violation: {ssrf_res.blocked_reason}")

        # 2. Fetch URL with Manual Redirect Validation to ensure SSRF safety at every hop
        fetched_content, final_url, status_code, content_type = self._fetch_safely(target_url)

        # 3. Clean and Extract Text from HTML
        title, company_guess, clean_text = self._extract_html_content(fetched_content)

        if not clean_text:
            warnings.append("Webpage contains very little or no readable text.")
            clean_text = f"[No readable job text extracted from {final_url}]"

        normalized = sanitizer.normalize_for_ml(clean_text)
        content_hash = sanitizer.compute_sha256(clean_text)
        urls = sanitizer.extract_urls(clean_text)
        if final_url not in urls:
            urls.insert(0, final_url)

        emails = sanitizer.extract_emails(clean_text)
        phones = sanitizer.extract_phones(clean_text)
        handles = sanitizer.extract_messaging_handles(clean_text)

        evidence_locations = [
            ExtractionEvidenceLocation(
                source_type=SourceType.URL,
                snippet=f"Source URL: {final_url} (HTTP {status_code}) — {clean_text[:250]}...",
                confidence=1.0,
            )
        ]

        return NormalizedJobContent(
            source_type=SourceType.URL,
            raw_text=clean_text,
            normalized_text=normalized,
            job_title=metadata.get("job_title") or title,
            company_name=metadata.get("company_name") or company_guess,
            source_identifier=final_url,
            content_hash=content_hash,
            mime_type=content_type,
            file_size_bytes=len(fetched_content.encode("utf-8")),
            extraction_method="safe_html_parser",
            extraction_confidence=0.90 if len(clean_text) > 100 else 0.40,
            extraction_warnings=warnings,
            extracted_urls=urls,
            extracted_emails=emails,
            extracted_phone_numbers=phones,
            extracted_messaging_handles=handles,
            evidence_locations=evidence_locations,
            source_metadata={
                **metadata,
                "initial_url": target_url,
                "final_url": final_url,
                "http_status": status_code,
                "page_title": title,
            },
        )

    def _fetch_safely(self, initial_url: str) -> tuple[str, str, int, str]:
        """Performs HTTP GET with strict hop-by-hop SSRF validation."""
        current_url = initial_url
        redirect_hops = 0

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 SentinelJob-Security-Scanner/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        with httpx.Client(
            timeout=httpx.Timeout(
                connect=limits.HTTP_CONNECT_TIMEOUT_SECONDS,
                read=limits.HTTP_READ_TIMEOUT_SECONDS,
                write=5.0,
                pool=5.0,
            ),
            follow_redirects=False,  # Manual redirect loop to validate SSRF after each hop
            headers=headers,
        ) as client:
            while redirect_hops <= limits.MAX_REDIRECT_HOPS:
                # SSRF check on current URL
                check = ssrf_protection.validate_url(current_url)
                if not check.is_safe:
                    raise ValueError(f"SSRF security violation during redirect to '{current_url}': {check.blocked_reason}")

                try:
                    response = client.get(current_url)
                except httpx.TimeoutException:
                    raise ValueError(f"Connection timeout fetching public job URL '{current_url}'.")
                except Exception as e:
                    raise ValueError(f"Network error fetching URL '{current_url}': {str(e)}")

                # Check for redirects
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("Location")
                    if not location:
                        raise ValueError("HTTP redirect status received without Location header.")
                    
                    next_url = urljoin(current_url, location)
                    current_url = next_url
                    redirect_hops += 1
                    continue

                if response.status_code >= 400:
                    raise ValueError(f"Remote server returned HTTP error {response.status_code} for URL '{current_url}'.")

                content_type = response.headers.get("Content-Type", "").lower()
                if not any(t in content_type for t in ["text/html", "application/xhtml+xml", "text/plain"]):
                    raise ValueError(f"Unsupported content type '{content_type}'. Public URL must return an HTML or text job posting.")

                body_bytes = response.content
                if len(body_bytes) > limits.MAX_URL_RESPONSE_SIZE_BYTES:
                    raise ValueError(f"URL response size ({len(body_bytes)} bytes) exceeds maximum limit of {limits.MAX_URL_RESPONSE_SIZE_BYTES // (1024 * 1024)} MB.")

                try:
                    html_text = response.text
                except Exception:
                    html_text = body_bytes.decode("utf-8", errors="replace")

                return html_text, current_url, response.status_code, content_type

        raise ValueError(f"Too many HTTP redirects (exceeded maximum limit of {limits.MAX_REDIRECT_HOPS} hops).")

    def _extract_html_content(self, html_text: str) -> tuple[Optional[str], Optional[str], str]:
        """Parse title, headings, and clean visible text from HTML."""
        soup = BeautifulSoup(html_text, "html.parser")

        title = None
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        # Clean noise tags
        for element in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "svg", "button", "form"]):
            element.decompose()

        # Extract main text
        clean_text = soup.get_text(separator=" ", strip=True)
        import re
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if len(clean_text) > limits.MAX_EXTRACTED_HTML_TEXT_BYTES:
            clean_text = clean_text[:limits.MAX_EXTRACTED_HTML_TEXT_BYTES]

        return title, None, clean_text


url_ingestor = UrlIngestor()
