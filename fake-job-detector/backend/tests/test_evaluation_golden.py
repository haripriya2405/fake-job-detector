"""Automated Golden Benchmark Test Suite for SentinelJob AI (Phase 6).
Evaluates system behavior against:
- Cohort A: Clean Legitimate
- Cohort B: Obvious Scams
- Cohort C: Impersonation & Typosquatting
- Cohort D: Borderline & Ambiguous
- Cohort E: Adversarial & Obfuscated
- Safety & Security Invariants
"""

from unittest.mock import MagicMock, patch
import pytest

from app.ml.engine import analysis_engine
from app.rules.engine import rule_engine
from app.rules.risk import risk_engine
from app.verification.dns_client import dns_resolver
from app.verification.rdap_client import rdap_client
from app.verification.schemas import DNSAnalysis, RDAPAnalysis
from app.verification.service import verification_service
from app.verification.ssrf import is_safe_hostname, is_safe_ip
from evaluation.golden_dataset import GOLDEN_TEST_CASES, GoldenTestCase
from evaluation.harness import SystemEvaluationHarness


@pytest.fixture(autouse=True)
def mock_external_network_for_testing():
    """Ensure 100% deterministic, offline test execution for golden benchmark."""
    def mock_dns_resolve(domain: str) -> DNSAnalysis:
        suspicious_keywords = ["unresolving", "scam", "info", "fake", "xyz", "top", "online", "tk", "click", "site"]
        if any(kw in domain.lower() for kw in suspicious_keywords):
            return DNSAnalysis(domain=domain, resolves=False, a_records=[], aaaa_records=[], mx_records=[], has_mx=False)
        return DNSAnalysis(domain=domain, resolves=True, a_records=["93.184.216.34"], aaaa_records=[], mx_records=["mail." + domain], has_mx=True)

    def mock_rdap_query(domain: str) -> RDAPAnalysis:
        suspicious_keywords = ["unresolving", "scam", "info", "fake", "xyz", "top", "online", "tk", "click", "site"]
        if any(kw in domain.lower() for kw in suspicious_keywords):
            return RDAPAnalysis(status="unavailable", error_message="Registry 404", domain_age_days=0)
        return RDAPAnalysis(status="available", registrar_name="Verisign Inc.", domain_age_days=3650)

    with patch.object(dns_resolver, "resolve_domain", side_effect=mock_dns_resolve), \
         patch.object(rdap_client, "lookup_domain", side_effect=mock_rdap_query):
        yield


# -----------------------------------------------------------------------------
# 1. Clean Legitimate Postings (Cohort A)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", [c for c in GOLDEN_TEST_CASES if c.cohort == "clean_legitimate"], ids=lambda c: c.id)
def test_clean_legitimate_postings_remain_low_risk(case: GoldenTestCase):
    """Clean legitimate job postings must remain in the configured expected risk tier (<= 35)."""
    ml_res = analysis_engine.analyze_text(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    rule_res = rule_engine.evaluate(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    ver_res = verification_service.verify_job_posting(case.text, claimed_company=case.company_name, job_title=case.title)
    risk_res = risk_engine.synthesize(ml_res, rule_res, ver_res)

    assert risk_res.risk_level in case.expected_risk_tiers, f"Case {case.id} escalated unexpectedly to {risk_res.risk_level} (Score: {risk_res.final_score})"
    assert risk_res.final_score <= case.expected_max_score, f"Case {case.id} score {risk_res.final_score} exceeded max {case.expected_max_score}"


# -----------------------------------------------------------------------------
# 2. Obvious Scams (Cohort B)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", [c for c in GOLDEN_TEST_CASES if c.cohort == "obvious_scam"], ids=lambda c: c.id)
def test_obvious_scams_trigger_suspicious_or_critical_risk(case: GoldenTestCase):
    """Obvious scams with fees, check overpayment, or crypto deposits must be flagged."""
    ml_res = analysis_engine.analyze_text(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    rule_res = rule_engine.evaluate(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    ver_res = verification_service.verify_job_posting(case.text, claimed_company=case.company_name, job_title=case.title)
    risk_res = risk_engine.synthesize(ml_res, rule_res, ver_res)

    assert risk_res.final_score >= 30, f"Case {case.id} under-scored at {risk_res.final_score}"
    assert len(risk_res.triggered_indicators) > 0, f"Case {case.id} had no triggered indicators"
    assert risk_res.explanation is not None and len(risk_res.explanation) > 10


# -----------------------------------------------------------------------------
# 3. Impersonation & Typosquatting (Cohort C)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", [c for c in GOLDEN_TEST_CASES if c.cohort == "impersonation"], ids=lambda c: c.id)
def test_impersonation_detection(case: GoldenTestCase):
    """Impersonated brands with mismatched domains or free webmail must trigger medium+ risk."""
    ml_res = analysis_engine.analyze_text(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    rule_res = rule_engine.evaluate(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    ver_res = verification_service.verify_job_posting(case.text, claimed_company=case.company_name, job_title=case.title)
    risk_res = risk_engine.synthesize(ml_res, rule_res, ver_res)

    assert risk_res.risk_level in ["medium", "high", "critical"], f"Case {case.id} failed to trigger elevated risk ({risk_res.risk_level})"
    assert risk_res.final_score >= 30


# -----------------------------------------------------------------------------
# 4. Borderline Postings (Cohort D)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", [c for c in GOLDEN_TEST_CASES if c.cohort == "borderline"], ids=lambda c: c.id)
def test_borderline_cases_do_not_falsely_escalate_to_critical(case: GoldenTestCase):
    """Borderline attributes (Gmail recruiter, WhatsApp screening, senior high salary) must not escalate to High or Critical."""
    ml_res = analysis_engine.analyze_text(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    rule_res = rule_engine.evaluate(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    ver_res = verification_service.verify_job_posting(case.text, claimed_company=case.company_name, job_title=case.title)
    risk_res = risk_engine.synthesize(ml_res, rule_res, ver_res)

    assert risk_res.risk_level in ["low", "medium"], f"Borderline case {case.id} falsely escalated to {risk_res.risk_level} (Score: {risk_res.final_score})"
    assert risk_res.final_score <= 59


# -----------------------------------------------------------------------------
# 5. Adversarial & Obfuscated Evasions (Cohort E)
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("case", [c for c in GOLDEN_TEST_CASES if c.cohort == "adversarial"], ids=lambda c: c.id)
def test_adversarial_obfuscation_resilience(case: GoldenTestCase):
    """Spaced words, paraphrased deposits, and vague tasks must trigger elevated risk."""
    ml_res = analysis_engine.analyze_text(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    rule_res = rule_engine.evaluate(case.text, metadata={"job_title": case.title, "company_name": case.company_name})
    ver_res = verification_service.verify_job_posting(case.text, claimed_company=case.company_name, job_title=case.title)
    risk_res = risk_engine.synthesize(ml_res, rule_res, ver_res)

    assert risk_res.final_score >= 35, f"Adversarial evasion succeeded on {case.id} (Score: {risk_res.final_score})"


# -----------------------------------------------------------------------------
# 6. Safety & Security Invariant Checks
# -----------------------------------------------------------------------------
def test_ssrf_defense_invariants():
    """Verify SSRF filters block localhost, internal subnets, and metadata endpoints."""
    safe_host, _ = is_safe_hostname("localhost")
    assert not safe_host
    safe_ip_host, _ = is_safe_hostname("127.0.0.1")
    assert not safe_ip_host
    safe_meta, _ = is_safe_hostname("169.254.169.254")
    assert not safe_meta
    safe_gcp, _ = is_safe_hostname("metadata.google.internal")
    assert not safe_gcp
    safe_corp, _ = is_safe_hostname("corp.intranet.local")
    assert not safe_corp

    safe_ip1, _ = is_safe_ip("10.0.0.5")
    assert not safe_ip1
    safe_ip2, _ = is_safe_ip("192.168.1.1")
    assert not safe_ip2
    safe_ip3, _ = is_safe_ip("172.16.0.1")
    assert not safe_ip3
    safe_ip4, _ = is_safe_ip("::1")
    assert not safe_ip4


def test_explainability_invariants_across_all_cases():
    """Verify that every evaluated case produces structured evidence without fabrication."""
    harness = SystemEvaluationHarness()
    report = harness.run_full_evaluation()

    assert len(report["explainability_violations"]) == 0, f"Found explainability violations: {report['explainability_violations']}"
    assert report["metrics"]["false_positive_rate"] == 0.0, "False positive rate on clean legitimate postings must be 0.0"
