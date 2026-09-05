from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
import pytest

from app.rules.engine import rule_engine
from app.rules.risk import risk_engine
from app.verification.dns_client import SafeDNSResolver, dns_resolver
from app.verification.rdap_client import SafeRDAPClient, rdap_client
from app.verification.schemas import DNSAnalysis, DomainVerificationResult, RDAPAnalysis
from app.verification.service import VerificationService, verification_service
from app.verification.ssrf import is_safe_hostname, is_safe_ip
from app.verification.url_extractor import URLExtractor, get_registrable_domain, url_extractor


# 1-5: URL Extraction & Normalization
def test_valid_url_extraction():
    """Test extracting fully qualified HTTPS URL."""
    text = "Please submit your application directly on https://careers.google.com/jobs/results/."
    urls = url_extractor.extract_urls(text)
    assert len(urls) >= 1
    assert urls[0].hostname == "careers.google.com"
    assert urls[0].registrable_domain == "google.com"
    assert urls[0].scheme == "https"


def test_url_without_scheme():
    """Test normalizing URL without http/https scheme."""
    norm = url_extractor.normalize_url("stripe.com/jobs")
    assert norm is not None
    assert norm.url.startswith("https://stripe.com")
    assert norm.registrable_domain == "stripe.com"


def test_invalid_url_handling():
    """Test that non-URLs or broken strings return None / empty."""
    assert url_extractor.normalize_url("not a url") is None
    assert url_extractor.normalize_url("http://") is None
    assert url_extractor.normalize_url("...") is None


def test_multiple_urls_and_query_stripping():
    """Test extracting multiple URLs and stripping tracking parameters."""
    text = (
        "Check our site https://company.org/apply?utm_source=linkedin&utm_medium=jobboard&id=42 "
        "and also review http://docs.company.org/handbook"
    )
    urls = url_extractor.extract_urls(text)
    assert len(urls) == 2
    assert "utm_source" not in urls[0].url
    assert "id=42" in urls[0].url


def test_domain_normalization_two_level_tld():
    """Test extracting registrable domains with two-level TLDs (e.g. .co.uk, .co.in)."""
    assert get_registrable_domain("jobs.amazon.co.uk") == "amazon.co.uk"
    assert get_registrable_domain("careers.tech.co.in") == "tech.co.in"
    assert get_registrable_domain("sub.domain.example.com") == "example.com"


# 6-8: DNS Resolution & MX Records
def test_dns_resolution_mx_present():
    """Test DNS analysis when domain resolves and has MX records."""
    resolver = SafeDNSResolver()
    with patch.object(resolver.resolver, "resolve") as mock_resolve:
        mock_a = MagicMock()
        mock_a.address = "93.184.216.34"
        mock_mx = MagicMock()
        mock_mx.exchange = "mail.example.com."
        mock_mx.preference = 10

        def side_effect(domain, rdtype):
            if rdtype == "A":
                return [mock_a]
            elif rdtype == "MX":
                return [mock_mx]
            raise Exception("No record")

        mock_resolve.side_effect = side_effect
        dns_res = resolver.resolve_domain("example.com")

        assert dns_res.resolves is True
        assert dns_res.has_mx is True
        assert "93.184.216.34" in dns_res.a_records
        assert dns_res.status == "resolves"


def test_dns_resolution_mx_absent():
    """Test DNS analysis when domain resolves but has no MX records."""
    resolver = SafeDNSResolver()
    with patch.object(resolver.resolver, "resolve") as mock_resolve:
        mock_a = MagicMock()
        mock_a.address = "198.51.100.1"

        def side_effect(domain, rdtype):
            if rdtype == "A":
                return [mock_a]
            raise Exception("No MX")

        mock_resolve.side_effect = side_effect
        dns_res = resolver.resolve_domain("no-mail-domain.com")

        assert dns_res.resolves is True
        assert dns_res.has_mx is False


# 9-12: RDAP Registration Data & Domain Age
def test_rdap_success_and_domain_age():
    """Test parsing RDAP response with creation date and calculating domain age."""
    client = SafeRDAPClient()
    mock_rdap_payload = {
        "events": [
            {"eventAction": "registration", "eventDate": "2015-01-01T00:00:00Z"},
            {"eventAction": "expiration", "eventDate": "2030-01-01T00:00:00Z"},
        ],
        "entities": [
            {
                "roles": ["registrar"],
                "vcardArray": ["vcard", [["version", {}, "text", "4.0"], ["fn", {}, "text", "MarkMonitor Inc."]]],
            }
        ],
        "nameservers": [{"ldhName": "ns1.google.com"}],
        "status": ["clientTransferProhibited"],
    }

    with patch("httpx.Client.get") as mock_get:
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = mock_rdap_payload
        mock_get.return_value = mock_res

        rdap_res = client.lookup_domain("google.com")
        assert rdap_res.status == "available"
        assert rdap_res.domain_age_days is not None
        assert rdap_res.domain_age_days > 3000
        assert rdap_res.registrar_name == "MarkMonitor Inc."


def test_rdap_recently_registered_domain():
    """Test that a domain registered 10 days ago produces the recently registered signal."""
    recent_date = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    mock_payload = {
        "events": [{"eventAction": "registration", "eventDate": recent_date}],
        "entities": [],
        "nameservers": [],
    }

    client = SafeRDAPClient()
    with patch("httpx.Client.get") as mock_get:
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = mock_payload
        mock_get.return_value = mock_res

        rdap_res = client.lookup_domain("brand-new-scam-portal.xyz")
        assert rdap_res.domain_age_days == 10


def test_rdap_unavailable():
    """Test handling unavailable RDAP data gracefully without raising exceptions."""
    client = SafeRDAPClient()
    with patch("httpx.Client.get") as mock_get:
        mock_res = MagicMock()
        mock_res.status_code = 404
        mock_get.return_value = mock_res

        rdap_res = client.lookup_domain("nonexistent-portal.com")
        assert rdap_res.status == "unavailable"
        assert rdap_res.domain_age_days is None


# 13-15: Email Domain Consistency
def test_matching_email_domain():
    """Test matching recruiter email domain against company domain."""
    svc = VerificationService()
    mock_domain_res = DomainVerificationResult(
        url="https://stripe.com",
        hostname="stripe.com",
        registrable_domain="stripe.com",
        dns=DNSAnalysis(resolves=True, has_mx=True),
        rdap=RDAPAnalysis(status="available", domain_age_days=3000),
        is_recently_registered=False,
    )
    with patch.object(svc, "_verify_single_domain", return_value=mock_domain_res):
        text = "Apply on stripe.com or email talent@stripe.com directly."
        out = svc.verify_job_posting(text, claimed_company="Stripe")

        assert out.company.email_domain_match is True
        assert out.company.status in ["verified", "partially_verified"]
        assert out.domain_penalty_score == 0


def test_mismatched_email_domain():
    """Test mismatched recruiter email domain generating signal."""
    svc = VerificationService()
    mock_domain_res = DomainVerificationResult(
        url="https://google.com",
        hostname="google.com",
        registrable_domain="google.com",
        dns=DNSAnalysis(resolves=True, has_mx=True),
        rdap=RDAPAnalysis(status="available", domain_age_days=5000),
        is_recently_registered=False,
    )
    with patch.object(svc, "_verify_single_domain", return_value=mock_domain_res):
        text = "Google Cloud careers page at google.com. Send resume to hr@apex-hiring-agency.top."
        out = svc.verify_job_posting(text, claimed_company="Google")

        signal_codes = [s.signal_code for s in out.signals]
        assert "EMAIL_DOMAIN_MISMATCH" in signal_codes
        assert out.domain_penalty_score > 0


# 16-19: SSRF & Safety Protection
def test_ssrf_localhost_attempt():
    """Test rejecting localhost and 127.0.0.1 attempts."""
    is_safe, reason = is_safe_hostname("localhost")
    assert is_safe is False

    is_safe, reason = is_safe_hostname("127.0.0.1")
    assert is_safe is False

    is_safe, reason = is_safe_hostname("sub.localhost")
    assert is_safe is False


def test_ssrf_private_and_metadata_ip_attempt():
    """Test rejecting private RFC1918 and AWS/GCP metadata 169.254.169.254."""
    assert is_safe_ip("10.0.0.1")[0] is False
    assert is_safe_ip("172.16.5.20")[0] is False
    assert is_safe_ip("192.168.1.1")[0] is False
    assert is_safe_ip("169.254.169.254")[0] is False
    assert is_safe_hostname("metadata.google.internal")[0] is False


def test_rdap_rate_limit_and_timeout():
    """Test handling RDAP rate-limiting (429) and network timeouts gracefully."""
    client = SafeRDAPClient()
    with patch("httpx.Client.get") as mock_get:
        mock_res = MagicMock()
        mock_res.status_code = 429
        mock_get.return_value = mock_res

        res = client.lookup_domain("rate-limited-test.com")
        assert res.status == "rate_limited"


# 20: Full Verification + RiskEngine Integration
def test_full_verification_risk_engine_integration():
    """Test multi-layer synthesis: ML + Rules + Domain Verification."""
    scam_text = (
        "URGENT HIRING: Work from Home. Send $100 registration fee. "
        "Apply at https://unresolving-fake-domain-2026.xyz and email recruiter@gmail.com on Telegram."
    )
    # ML output
    ml_res = {"ml_probability": 0.85, "ml_label": "suspicious"}
    # Rule engine
    rule_res = rule_engine.evaluate(scam_text)
    # Verification service
    ver_res = verification_service.verify_job_posting(scam_text, claimed_company="Apex Global")

    # Synthesize
    risk_res = risk_engine.synthesize(
        ml_result=ml_res,
        rule_result=rule_res,
        verification_result=ver_res,
    )

    assert risk_res.final_score >= 60
    assert risk_res.risk_level in ["high", "critical"]
    assert risk_res.score_breakdown.domain_penalty >= 0
    assert "Overall Risk Score:" in risk_res.explanation
