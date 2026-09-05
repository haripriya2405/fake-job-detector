import ipaddress
import re
import socket
from typing import NamedTuple, Tuple
from urllib.parse import urlparse


BLOCKED_HOSTNAMES = {
    "localhost",
    "loopback",
    "metadata.google.internal",
    "instance-data",
    "169.254.169.254",
}

BLOCKED_SUFFIXES = (
    ".local",
    ".localhost",
    ".internal",
    ".corp",
    ".lan",
    ".home",
    ".arpa",
)

# Private & Link-Local IP Networks
PRIVATE_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 ULA
    ipaddress.ip_network("fe80::/10"),  # IPv6 Link-Local
]


class SSRFValidationResult(NamedTuple):
    is_safe: bool
    blocked_reason: str
    hostname: str


def is_safe_hostname(hostname: str) -> Tuple[bool, str]:
    """Check if a hostname or domain name is safe to resolve and query externally without SSRF risk."""
    if not hostname:
        return False, "Empty hostname"

    host_clean = hostname.strip().lower().rstrip(".")

    # Check blocked keywords & suffixes
    if host_clean in BLOCKED_HOSTNAMES:
        return False, f"Blocked internal/metadata hostname: '{host_clean}'"

    for suffix in BLOCKED_SUFFIXES:
        if host_clean.endswith(suffix):
            return False, f"Blocked internal suffix '{suffix}'"

    # If it is a direct IP address, validate IP range immediately
    try:
        ip_obj = ipaddress.ip_address(host_clean)
        for net in PRIVATE_NETWORKS:
            if ip_obj in net:
                return False, f"Target IP '{host_clean}' belongs to private/restricted network {net}"
        return True, "Safe IP"
    except ValueError:
        # Check for integer/hexadecimal IP representations (e.g. 2130706433 or 0x7f000001)
        if host_clean.isdigit() or host_clean.startswith("0x"):
            try:
                val = int(host_clean, 0)
                if 0 <= val <= 0xFFFFFFFF:
                    ip_obj = ipaddress.IPv4Address(val)
                    for net in PRIVATE_NETWORKS:
                        if ip_obj in net:
                            return False, f"Target integer IP '{host_clean}' ({ip_obj}) belongs to private/restricted network {net}"
                    return True, "Safe IP"
            except (ValueError, OverflowError):
                pass

    # Hostname pattern validation (RFC 1123)
    if not re.match(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*$", host_clean):
        return False, f"Invalid hostname format: '{host_clean}'"

    return True, "Safe Hostname"


def is_safe_ip(ip_str: str) -> Tuple[bool, str]:
    """Check if an IP string is safe (not loopback, private, link-local, or multicast)."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        for net in PRIVATE_NETWORKS:
            if ip_obj in net:
                return False, f"IP '{ip_str}' is inside forbidden range {net}"
        return True, "Safe IP"
    except ValueError:
        return False, f"Invalid IP address representation: '{ip_str}'"


class SSRFProtection:
    """Centralized SSRF protection service validating URLs and preventing DNS rebinding attacks."""

    @staticmethod
    def validate_url(url: str) -> SSRFValidationResult:
        try:
            parsed = urlparse(url)
            scheme = (parsed.scheme or "").lower()
            if scheme not in ("http", "https"):
                return SSRFValidationResult(
                    is_safe=False,
                    blocked_reason=f"Unsupported protocol scheme '{scheme}'. Only HTTP/HTTPS allowed.",
                    hostname="",
                )

            hostname = parsed.hostname
            if not hostname:
                return SSRFValidationResult(
                    is_safe=False,
                    blocked_reason="Missing or empty hostname in URL.",
                    hostname="",
                )

            safe_host, reason = is_safe_hostname(hostname)
            if not safe_host:
                return SSRFValidationResult(
                    is_safe=False,
                    blocked_reason=reason,
                    hostname=hostname,
                )

            # DNS Rebinding check: resolve hostname and check resulting IPs
            try:
                # If hostname is not an IP literal, perform resolution safety check
                ipaddress.ip_address(hostname)
            except ValueError:
                # Hostname is a domain name, check resolved addresses if reachable
                try:
                    addr_info = socket.getaddrinfo(hostname, None)
                    for family, _, _, _, sockaddr in addr_info:
                        resolved_ip = sockaddr[0]
                        safe_ip, ip_reason = is_safe_ip(resolved_ip)
                        if not safe_ip:
                            return SSRFValidationResult(
                                is_safe=False,
                                blocked_reason=f"Hostname '{hostname}' resolves to forbidden private IP '{resolved_ip}': {ip_reason}",
                                hostname=hostname,
                            )
                except socket.gaierror:
                    # DNS failure will be handled gracefully during fetch
                    pass

            return SSRFValidationResult(is_safe=True, blocked_reason="", hostname=hostname)

        except Exception as e:
            return SSRFValidationResult(is_safe=False, blocked_reason=f"URL parsing failure: {str(e)}", hostname="")


ssrf_protection = SSRFProtection()
