from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Tuple
import dateutil.parser
import httpx

from app.core.logging import logger
from app.verification.schemas import RDAPAnalysis
from app.verification.ssrf import is_safe_hostname


class SafeRDAPClient:
    """Registration Data Access Protocol (RDAP) client for generic and ccTLDs.
    Uses HTTPS, parses standard ICANN RDAP JSON schemas, and calculates domain age in UTC.
    """

    # Public RDAP aggregator & registry fallback endpoints
    DEFAULT_RDAP_BASE = "https://rdap.org/domain"

    def __init__(self, timeout_sec: float = 2.5, cache_ttl_sec: int = 3600):
        self.timeout_sec = timeout_sec
        self.cache_ttl_sec = cache_ttl_sec
        self._cache: Dict[str, Tuple[float, RDAPAnalysis]] = {}

    def lookup_domain(self, domain: str) -> RDAPAnalysis:
        if not domain:
            return RDAPAnalysis(status="unavailable")

        clean_domain = domain.strip().lower().rstrip(".")

        # Check memory cache
        now = time.time()
        if clean_domain in self._cache:
            cached_time, cached_val = self._cache[clean_domain]
            if now - cached_time < self.cache_ttl_sec:
                return cached_val

        # SSRF validation
        is_safe, _ = is_safe_hostname(clean_domain)
        if not is_safe:
            result = RDAPAnalysis(status="unavailable")
            self._cache[clean_domain] = (now, result)
            return result

        rdap_url = f"{self.DEFAULT_RDAP_BASE}/{clean_domain}"

        try:
            with httpx.Client(timeout=self.timeout_sec, follow_redirects=True) as client:
                response = client.get(
                    rdap_url,
                    headers={"Accept": "application/rdap+json, application/json", "User-Agent": "SentinelJob-AI-RDAP/1.0"},
                )

            if response.status_code == 429:
                logger.warning(f"RDAP rate limit encountered for '{clean_domain}'")
                result = RDAPAnalysis(status="rate_limited", raw_rdap_url=rdap_url)
                self._cache[clean_domain] = (now, result)
                return result

            if response.status_code != 200:
                result = RDAPAnalysis(status="unavailable", raw_rdap_url=rdap_url)
                self._cache[clean_domain] = (now, result)
                return result

            data = response.json()
            analysis = self._parse_rdap_payload(data, rdap_url)
            self._cache[clean_domain] = (now, analysis)
            return analysis

        except httpx.TimeoutException:
            result = RDAPAnalysis(status="error", raw_rdap_url=rdap_url)
            return result
        except Exception as e:
            logger.debug(f"RDAP error on {clean_domain}: {e}")
            result = RDAPAnalysis(status="unavailable", raw_rdap_url=rdap_url)
            self._cache[clean_domain] = (now, result)
            return result

    def _parse_rdap_payload(self, data: Dict[str, Any], rdap_url: str) -> RDAPAnalysis:
        reg_date: Optional[datetime] = None
        exp_date: Optional[datetime] = None
        domain_age_days: Optional[int] = None
        registrar: Optional[str] = None
        nameservers: List[str] = []
        statuses: List[str] = data.get("status", [])

        # 1. Parse Event Dates (Registration & Expiration in UTC)
        events = data.get("events", [])
        for event in events:
            action = event.get("eventAction", "").lower()
            date_str = event.get("eventDate")
            if not date_str:
                continue

            try:
                parsed_dt = dateutil.parser.parse(date_str)
                if parsed_dt.tzinfo is None:
                    parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                else:
                    parsed_dt = parsed_dt.astimezone(timezone.utc)

                if action in ["registration", "created", "initial registration"]:
                    reg_date = parsed_dt
                elif action in ["expiration", "expires"]:
                    exp_date = parsed_dt
            except Exception:
                pass

        # Calculate domain age in UTC
        if reg_date:
            now_utc = datetime.now(timezone.utc)
            delta = now_utc - reg_date
            domain_age_days = max(0, delta.days)

        # 2. Parse Registrar Entity
        entities = data.get("entities", [])
        for entity in entities:
            roles = [r.lower() for r in entity.get("roles", [])]
            if "registrar" in roles:
                vcard = entity.get("vcardArray", [])
                if len(vcard) > 1 and isinstance(vcard[1], list):
                    for prop in vcard[1]:
                        if len(prop) > 3 and prop[0] == "fn":
                            registrar = prop[3]
                            break
                if not registrar:
                    registrar = entity.get("handle")

        # 3. Parse Nameservers
        ns_list = data.get("nameservers", [])
        for ns in ns_list:
            ldh = ns.get("ldhName")
            if ldh:
                nameservers.append(ldh.lower())

        return RDAPAnalysis(
            status="available" if reg_date else "available_without_dates",
            registration_date=reg_date,
            expiration_date=exp_date,
            domain_age_days=domain_age_days,
            registrar_name=registrar,
            nameservers=nameservers,
            domain_status=statuses,
            raw_rdap_url=rdap_url,
        )


rdap_client = SafeRDAPClient()
