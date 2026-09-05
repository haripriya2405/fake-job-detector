import pytest
from app.rules.definitions import RULE_REGISTRY
from app.rules.engine import RuleEngine, rule_engine
from app.rules.risk import RiskEngine, risk_engine
from app.rules.schemas import RuleEngineResult


def test_rule_registry_completeness():
    """Verify all required rule categories exist in the versioned registry."""
    categories = {r.category for r in RULE_REGISTRY}
    expected_categories = {
        "financial",
        "communication",
        "manipulation",
        "compensation",
        "data_privacy",
        "crypto_task",
    }
    assert expected_categories.issubset(categories)
    assert len(RULE_REGISTRY) >= 15
    for r in RULE_REGISTRY:
        assert r.code
        assert r.name
        assert r.severity in ["critical", "high", "medium", "low"]
        assert r.default_weight > 0
        assert r.recommendation


def test_scenario_1_clean_legitimate_job():
    """Scenario 1: Clean corporate job posting produces 0 triggered rules and low risk."""
    clean_text = (
        "Stripe is hiring a Senior Software Engineer in San Francisco, CA. "
        "Requirements: 5+ years experience in distributed systems, Go or Java, "
        "and Kubernetes. Apply online via stripe.com/jobs."
    )
    rule_res = rule_engine.evaluate(clean_text)
    assert len(rule_res.triggered_rules) == 0
    assert rule_res.capped_score == 0

    risk_res = risk_engine.synthesize(
        ml_result={"ml_probability": 0.15, "ml_label": "legitimate"},
        rule_result=rule_res,
    )
    assert risk_res.final_score < 30
    assert risk_res.risk_level == "low"
    assert "No explicit deterministic scam signatures triggered" in risk_res.explanation


def test_scenario_2_registration_fee_scam():
    """Scenario 2: Upfront registration fee scam."""
    text = "Work from home Data Entry. Weekly stipend ₹30,000. Registration fee of ₹2,500 required before joining."
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "FIN_REGISTRATION_FEE" in codes

    risk_res = risk_engine.synthesize(
        ml_result={"ml_probability": 0.85, "ml_label": "suspicious"},
        rule_result=rule_res,
    )
    assert risk_res.final_score >= 50
    assert any("registration" in rec["detail"].lower() for rec in risk_res.recommendations)


def test_scenario_3_cashier_check_scam():
    """Scenario 3: Mailed cashier check / vendor check scam."""
    text = (
        "We are sending a cashier check of $3,000 for your home office. "
        "Deposit check at your ATM and wire remainder to our approved equipment vendor."
    )
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "FIN_CASHIER_CHECK_FRAUD" in codes

    matched_rule = next(r for r in rule_res.triggered_rules if r.rule_code == "FIN_CASHIER_CHECK_FRAUD")
    assert "cashier check" in matched_rule.evidence_text.lower()


def test_scenario_4_telegram_scam():
    """Scenario 4: Telegram-only recruitment."""
    text = "Online Customer Service Assistant. Please contact HR manager on Telegram @ApexCareers_Recruiter."
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "COMM_TELEGRAM_RECRUITMENT" in codes


def test_scenario_5_whatsapp_scam():
    """Scenario 5: WhatsApp onboarding scheme."""
    text = "Part time job opening. Message to +19988776655 on WhatsApp to begin onboarding."
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "COMM_WHATSAPP_RECRUITMENT" in codes


def test_scenario_6_crypto_task_scam():
    """Scenario 6: Crypto VIP rating & deposit-to-withdraw trap."""
    text = "Earn $400 daily rating movies. Deposit 100 USDT into crypto wallet to activate commission portal."
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "CRYPTO_WALLET_DEPOSIT" in codes or "TASK_DEPOSIT_TO_WITHDRAW" in codes

    risk_res = risk_engine.synthesize(
        ml_result={"ml_probability": 0.90, "ml_label": "suspicious"},
        rule_result=rule_res,
    )
    assert risk_res.risk_level in ["high", "critical"]


def test_scenario_7_sensitive_data_request():
    """Scenario 7: Demanding banking credentials and OTP."""
    text = "Immediate hiring. Send bank login credentials and netbanking password to setup payroll before interview."
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "DATA_BANK_CREDENTIALS" in codes


def test_scenario_8_urgency_plus_payment_combination():
    """Scenario 8: Urgent action paired with advance payment."""
    text = "URGENT HIRING: Needed immediately. Pay 1500 before joining. Act immediately!"
    rule_res = rule_engine.evaluate(text)
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "RECRUIT_URGENT_ACTION" in codes
    assert "FIN_ADVANCE_PAYMENT" in codes


def test_scenario_9_correlated_payment_rules_and_category_caps():
    """Scenario 9: Multiple correlated payment triggers do not exceed financial category cap (30 pts)."""
    text = (
        "Registration fee required. Also training fee needed. "
        "Must pay advance payment and security deposit before interview."
    )
    rule_res = rule_engine.evaluate(text)
    # Financial category cap is 30
    assert rule_res.category_scores["financial"] <= 30
    assert rule_res.raw_score > rule_res.capped_score


def test_scenario_10_high_salary_legitimate_job():
    """Scenario 10: High compensation for legitimate senior role does not trigger scam flag."""
    text = (
        "Google Cloud Platform is hiring a Principal Cloud Architect in New York. "
        "Compensation range: $220,000 - $310,000 per year plus equity and comprehensive benefits. "
        "Requires 10+ years experience in distributed systems. Apply at google.com/careers."
    )
    rule_res = rule_engine.evaluate(text)
    # Should NOT trigger COMP_UNREALISTIC_PAY since this is not basic data entry
    codes = [r.rule_code for r in rule_res.triggered_rules]
    assert "COMP_UNREALISTIC_PAY" not in codes
    assert rule_res.capped_score == 0


def test_scenario_11_overall_score_capping():
    """Test that extreme multi-signal scam scores are strictly bounded at 100."""
    extreme_scam = (
        "URGENT HIRING: No interview required. Guaranteed selection! "
        "Pay ₹5,000 registration fee. Deposit check at ATM and wire money back. "
        "Earn $500/hr liking YouTube videos. Deposit 500 USDT on Telegram @ScamKing. "
        "Send bank login credentials and copy of passport before interview."
    )
    rule_res = rule_engine.evaluate(extreme_scam)
    risk_res = risk_engine.synthesize(
        ml_result={"ml_probability": 0.99, "ml_label": "suspicious"},
        rule_result=rule_res,
    )
    assert risk_res.final_score <= 100
    assert risk_res.risk_level == "critical"
    assert len(risk_res.triggered_indicators) >= 4
