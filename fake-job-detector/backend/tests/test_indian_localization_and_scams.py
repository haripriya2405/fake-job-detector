"""Test Suite for Indian Market Localization, Dual Currency (₹ INR / LPA), and Indian Job Scam Vectors."""

import pytest
from app.services.salary_benchmark_service import salary_benchmark_service
from app.services.fraud_watchlist_service import fraud_watchlist_service
from app.rules.engine import rule_engine


def test_indian_lpa_salary_extraction_and_benchmarking():
    """Verify Indian LPA compensation (e.g., 6.5 LPA) is correctly recognized and benchmarked."""
    text = "We are hiring a Full Stack Developer (React/Node). Compensation package: 8 LPA - 12 LPA."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Full Stack Developer")

    assert res.currency == "INR"
    assert res.frequency == "LPA"
    assert res.min_amount == 8.0
    assert res.max_amount == 12.0
    assert res.annualized_min == 800000.0
    assert res.is_unrealistic_high is False
    assert res.verdict == "REALISTIC_MARKET_RATE"


def test_indian_data_entry_daily_scam_trap_detected():
    """Verify classic Indian daily pay scam trap ('Earn ₹3,000/day by typing') is flagged."""
    text = "Urgent requirement: Data entry & form filling typing work from home. Earn ₹3,500/day. No skills required."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Data Entry Typist")

    assert res.currency == "INR"
    assert res.is_unrealistic_high is True
    assert res.verdict == "UNREALISTIC_HIGH_TRAP"
    assert res.risk_points >= 40
    assert "₹" in res.explanation


def test_indian_monthly_inr_benchmarking():
    """Verify monthly INR formulation (₹25,000/month) is benchmarked against Indian salary standards."""
    text = "Opening for Customer Support Associate. Monthly salary: ₹22,000 - ₹28,000 / month."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Customer Support")

    assert res.currency == "INR"
    assert res.frequency == "MONTHLY"
    assert res.min_amount == 22000.0
    assert res.max_amount == 28000.0
    assert res.is_unrealistic_high is False


def test_indian_upi_payment_rule_detection():
    """Verify security rule catches requests for UPI / GPay / PhonePe / Paytm registration fee."""
    text = "To confirm your interview slot, please pay refundable gate pass fee of ₹1,500 via GPay / PhonePe UPI ID hr@upi."
    res = rule_engine.evaluate(text)
    rule_codes = [t.rule_code for t in res.triggered_rules]

    assert "FIN_UPI_QR_PAYMENT" in rule_codes


def test_indian_it_impersonation_detection():
    """Verify security rule catches unauthorized Indian IT enterprise impersonation."""
    text = "TCS Hiring: Selected for Assistant System Engineer. Pay registration charge before issuing appointment letter."
    res = rule_engine.evaluate(text)
    rule_codes = [t.rule_code for t in res.triggered_rules]

    assert "FIN_REGISTRATION_FEE" in rule_codes or "RECRUIT_INDIAN_IT_IMPERSONATION" in rule_codes


def test_indian_cybercrime_1930_watchlist_match():
    """Verify text with Indian video liking task matches I4C / 1930 Cybercrime advisory."""
    text = "Part time work: Earn ₹3,000 daily. Just like YouTube videos and rate hotel task to earn daily commission."
    match_res = fraud_watchlist_service.cross_reference_posting(text)

    assert match_res["has_watchlist_matches"] is True
    assert "I4C_MHA" in match_res["agencies_flagged"]
    assert "1930" in match_res["national_helpline"]
