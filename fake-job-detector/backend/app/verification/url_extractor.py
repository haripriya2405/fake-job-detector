import re
from typing import List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from app.verification.schemas import ExtractedURL
from app.verification.ssrf import is_safe_hostname

# Regular expressions for URL matching
URL_REGEX = re.compile(
    r'(?:https?:\/\/|www\.)[a-zA-Z0-9][-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{2,12}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)',
    re.IGNORECASE,
)

# Common Two-Level Public Suffixes (lightweight fallback without heavy external deps)
TWO_LEVEL_TLDS = {
    "co.uk", "org.uk", "gov.uk", "ac.uk",
    "co.in", "net.in", "org.in", "gov.in", "edu.in",
    "com.au", "net.au", "org.au", "edu.au",
    "co.nz", "net.nz", "org.nz",
    "co.za", "org.za",
    "co.jp", "ne.jp", "ac.jp",
    "com.br", "org.br",
    "com.sg", "edu.sg",
}

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "dclid", "msclkid", "mc_eid", "yclid", "_hsenc", "_hsmi",
}


def get_registrable_domain(hostname: str) -> str:
    """Extract registrable domain from hostname (e.g. 'sub.google.com' -> 'google.com', 'jobs.bbc.co.uk' -> 'bbc.co.uk')."""
    if not hostname:
        return ""
    host = hostname.strip().lower().rstrip(".")
    parts = host.split(".")
    if len(parts) <= 2:
        return host

    last_two = ".".join(parts[-2:])
    if last_two in TWO_LEVEL_TLDS and len(parts) >= 3:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


class URLExtractor:
    """Safe URL extractor and normalizer."""

    def extract_urls(self, text: str) -> List[ExtractedURL]:
        if not text:
            return []

        raw_matches = URL_REGEX.findall(text)
        results: List[ExtractedURL] = []
        seen_urls = set()

        for raw_url in raw_matches:
            normalized = self.normalize_url(raw_url)
            if normalized and normalized.url not in seen_urls:
                seen_urls.add(normalized.url)
                results.append(normalized)

        # Also search for standalone bare domains (e.g. "apply at stripe.com/careers" or "visit google.com")
        bare_domain_pattern = re.compile(
            r'\b(?:at|on|visit|apply at|portal:?)\s+([a-zA-Z0-9][-a-zA-Z0-9]{1,62}\.(?:com|org|net|io|co|in|edu|gov|ai|tech|app)(?:\/[^\s,;\)]*)?)',
            re.IGNORECASE,
        )
        bare_matches = bare_domain_pattern.findall(text)
        for bare in bare_matches:
            normalized = self.normalize_url(bare)
            if normalized and normalized.url not in seen_urls:
                seen_urls.add(normalized.url)
                results.append(normalized)

        return results

    def normalize_url(self, raw_url: str) -> Optional[ExtractedURL]:
        if not raw_url:
            return None

        clean_url = raw_url.strip().rstrip(".,;)>]\"'")

        # Ensure scheme
        if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
            clean_url = "https://" + clean_url

        try:
            parsed = urlparse(clean_url)
            hostname = (parsed.hostname or "").lower().rstrip(".")
            if not hostname or "." not in hostname:
                return None

            is_safe, _ = is_safe_hostname(hostname)
            registrable = get_registrable_domain(hostname)

            # Strip tracking query parameters
            query_params = parse_qsl(parsed.query, keep_blank_values=True)
            clean_query = [
                (k, v) for k, v in query_params if k.lower() not in TRACKING_PARAMS
            ]
            new_query = urlencode(clean_query)

            clean_parsed = parsed._replace(
                netloc=hostname,
                query=new_query,
                fragment="",
            )
            canonical_url = urlunparse(clean_parsed)

            return ExtractedURL(
                url=canonical_url,
                hostname=hostname,
                registrable_domain=registrable,
                scheme=parsed.scheme or "https",
                path=parsed.path or "/",
                is_safe=is_safe,
                extraction_source="text",
            )
        except Exception:
            return None


url_extractor = URLExtractor()
