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


def test_ai_explainer_indian_safety_advisory():
    """Verify AI Explainer synthesizes Indian-specific safety advisories (1930, cybercrime.gov.in, UPI caution) for high-risk Indian postings."""
    from app.services.ai_explainer import ai_explainer

    indian_fraud_text = "TCS direct selection for System Engineer. CTC 6.5 LPA. Pay Rs. 4,500 refundable laptop gatepass fee via PhonePe UPI."
    explanation = ai_explainer.generate_explanation(
        raw_text=indian_fraud_text,
        job_title="System Engineer",
        company_name="TCS",
        risk_score=92,
        risk_level="critical",
        ml_prob=0.88,
    )

    assert "UPI" in explanation or "GPay" in explanation
    assert "1930" in explanation
    assert "cybercrime.gov.in" in explanation


def test_ai_explainer_global_safety_fallback():
    """Verify AI Explainer uses standard international advisories (FTC / IC3) when text is global/USD."""
    from app.services.ai_explainer import ai_explainer

    global_fraud_text = "We will send a $4,500 cashier check to purchase home office equipment. Wire remaining $3,500 back via Western Union."
    explanation = ai_explainer.generate_explanation(
        raw_text=global_fraud_text,
        job_title="Administrative Assistant",
        company_name="Global Tech Corp",
        risk_score=95,
        risk_level="critical",
        ml_prob=0.92,
    )

    assert "cashier check" in explanation or "wire" in explanation
    assert "FTC" in explanation or "IC3" in explanation or "off-platform" in explanation

