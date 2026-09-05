"""Test Suite for Salary Benchmarking & Anomaly Detection (Phase 21)."""

import pytest
from app.services.salary_benchmark_service import SalaryBenchmarkService, salary_benchmark_service


def test_realistic_data_entry_salary():
    """Verify normal hourly rate ($18/hr) is recognized as realistic for data entry."""
    text = "Hiring Remote Data Entry Clerk. Compensation is $18.50 - $22.00 / hour. Benefits include 401(k) and health."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Data Entry Clerk")

    assert res.matched_job_family == "data_entry_typing"
    assert res.is_unrealistic_high is False
    assert res.verdict == "REALISTIC_MARKET_RATE"
    assert res.min_amount == 18.50
    assert res.max_amount == 22.00
    assert res.frequency == "HOURLY"


def test_unrealistic_high_data_entry_salary_trap():
    """Verify inflated rate ($75/hr for data entry) is flagged as an unrealistic scam lure."""
    text = "Immediate Start Data Entry Typist Needed! Earn $75 per hour working from home. No experience needed."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Typist")

    assert res.matched_job_family == "data_entry_typing"
    assert res.is_unrealistic_high is True
    assert res.verdict == "UNREALISTIC_HIGH_TRAP"
    assert res.risk_points == 40
    assert "market median" in res.explanation


def test_annual_software_engineer_salary():
    """Verify competitive enterprise software engineer salary ($140k - $160k/yr)."""
    text = "Senior Python Backend Engineer at Stripe. Salary range: $140,000 - $160,000 / year plus equity."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Senior Python Backend Engineer")

    assert res.matched_job_family == "software_engineering"
    assert res.is_unrealistic_high is False
    assert res.verdict == "REALISTIC_MARKET_RATE"
    assert res.annualized_min == 140000.0


def test_no_salary_mentioned():
    """Verify graceful handling when no salary is mentioned."""
    text = "We are seeking a marketing intern to join our team in New York. Apply online with your resume."
    res = salary_benchmark_service.evaluate_compensation(text, job_title="Marketing Intern")

    assert res.verdict == "NO_SALARY_DETECTED"
    assert res.detected_salary_text is None
    assert res.is_unrealistic_high is False
