import time
from typing import Dict, List, Optional, Tuple
import dns.exception
import dns.resolver

from app.core.logging import logger
from app.verification.schemas import DNSAnalysis
from app.verification.ssrf import is_safe_hostname, is_safe_ip


class SafeDNSResolver:
    """Safe DNS client with SSRF protection, strict timeouts, and memory TTL caching."""

    def __init__(self, timeout_sec: float = 2.0, cache_ttl_sec: int = 600):
        self.timeout_sec = timeout_sec
        self.cache_ttl_sec = cache_ttl_sec
        self._cache: Dict[str, Tuple[float, DNSAnalysis]] = {}

        # Configure custom resolver
        self.resolver = dns.resolver.Resolver()
        self.resolver.lifetime = timeout_sec
        self.resolver.timeout = timeout_sec

    def resolve_domain(self, domain: str) -> DNSAnalysis:
        if not domain:
            return DNSAnalysis(status="unresolved")

        clean_domain = domain.strip().lower().rstrip(".")

        # Check in-memory cache
        now = time.time()
        if clean_domain in self._cache:
            cached_time, cached_val = self._cache[clean_domain]
            if now - cached_time < self.cache_ttl_sec:
                return cached_val

        # SSRF Hostname validation
        is_safe, reason = is_safe_hostname(clean_domain)
        if not is_safe:
            result = DNSAnalysis(
                resolves=False,
                status="ssrf_blocked",
            )
            self._cache[clean_domain] = (now, result)
            return result

        start_t = time.perf_counter()
        a_records: List[str] = []
        aaaa_records: List[str] = []
        mx_records: List[str] = []
        ns_records: List[str] = []

        try:
            # 1. Query A records (IPv4)
            try:
                answers = self.resolver.resolve(clean_domain, "A")
                for rdata in answers:
                    ip_str = str(rdata.address)
                    # Check resolved IP against DNS rebinding SSRF
                    is_ip_safe, _ = is_safe_ip(ip_str)
                    if is_ip_safe:
                        a_records.append(ip_str)
                    else:
                        logger.warning(f"DNS Rebinding blocked: '{clean_domain}' resolved to restricted IP '{ip_str}'")
                        return DNSAnalysis(resolves=False, status="ssrf_blocked")
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                pass
            except dns.exception.Timeout:
                pass

            # 2. Query AAAA records (IPv6)
            try:
                answers_aaaa = self.resolver.resolve(clean_domain, "AAAA")
                for rdata in answers_aaaa:
                    ip_str = str(rdata.address)
                    is_ip_safe, _ = is_safe_ip(ip_str)
                    if is_ip_safe:
                        aaaa_records.append(ip_str)
            except Exception:
                pass

            # 3. Query MX records (Mail eXchangers)
            try:
                answers_mx = self.resolver.resolve(clean_domain, "MX")
                for rdata in answers_mx:
                    mx_host = str(rdata.exchange).rstrip(".")
                    mx_records.append(f"{rdata.preference} {mx_host}")
            except Exception:
                pass

            # 4. Query NS records
            try:
                answers_ns = self.resolver.resolve(clean_domain, "NS")
                for rdata in answers_ns:
                    ns_records.append(str(rdata.target).rstrip("."))
            except Exception:
                pass

            elapsed_ms = (time.perf_counter() - start_t) * 1000.0
            resolves = len(a_records) > 0 or len(aaaa_records) > 0 or len(mx_records) > 0

            result = DNSAnalysis(
                resolves=resolves,
                a_records=a_records,
                aaaa_records=aaaa_records,
                mx_records=mx_records,
                has_mx=len(mx_records) > 0,
                ns_records=ns_records,
                query_time_ms=round(elapsed_ms, 2),
                status="resolves" if resolves else "nxdomain",
            )
            self._cache[clean_domain] = (now, result)
            return result

        except dns.resolver.NXDOMAIN:
            result = DNSAnalysis(resolves=False, status="nxdomain")
            self._cache[clean_domain] = (now, result)
            return result
        except dns.exception.Timeout:
            result = DNSAnalysis(resolves=False, status="timeout")
            return result
        except Exception as e:
            logger.debug(f"DNS resolution error on {clean_domain}: {e}")
            result = DNSAnalysis(resolves=False, status="unresolved")
            return result


dns_resolver = SafeDNSResolver()
