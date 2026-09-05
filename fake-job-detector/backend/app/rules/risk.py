from typing import Any, Dict, List, Optional
from app.rules.schemas import (
    RiskEngineResult,
    RiskScoreBreakdown,
    RuleEngineResult,
    TriggeredRule,
)
from app.verification.schemas import VerificationOutput


class RiskEngine:
    """Multi-factor Risk Synthesis Engine.
    Combines:
    1. Statistical ML Probability (Max 35 pts)
    2. Deterministic Security Rules (Max 65 pts)
    3. External Domain & Company Consistency Signals (Max 25 pts)
    Total aggregate score is strictly capped at 0-100.
    """

    VERSION = "risk-engine-v1.0.0"

    # Configurable Scoring Caps
    MAX_ML_POINTS: int = 35
    MAX_RULE_POINTS: int = 65
    MAX_DOMAIN_POINTS: int = 35
    MAX_TOTAL_POINTS: int = 100

    def synthesize(
        self,
        ml_result: Dict[str, Any],
        rule_result: RuleEngineResult,
        verification_result: Optional[VerificationOutput] = None,
    ) -> RiskEngineResult:
        """Synthesize ML probability, deterministic rules, and verification signals into a final score."""
        ml_prob = float(ml_result.get("ml_probability", 0.0))
        ml_label = ml_result.get("ml_label", "pending")

        # 1. Compute ML Contribution (Max 35 points)
        ml_contribution = int(round(ml_prob * self.MAX_ML_POINTS))

        # 2. Compute Rule Contribution (Max 65 points)
        rule_raw_sum = rule_result.capped_score
        rule_contribution = min(rule_raw_sum, self.MAX_RULE_POINTS)

        # 3. Compute Domain & Verification Penalty (Max 25 points)
        domain_penalty = 0
        if verification_result:
            domain_penalty = min(verification_result.domain_penalty_score, self.MAX_DOMAIN_POINTS)

        # 4. Total Aggregate Score (Strictly Capped at 0-100)
        raw_total = ml_contribution + rule_contribution + domain_penalty
        final_score = min(max(0, raw_total), self.MAX_TOTAL_POINTS)

        # 5. Risk Tier Classification
        if final_score >= 80:
            risk_level = "critical"
        elif final_score >= 60:
            risk_level = "high"
        elif final_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"

        # 6. Synthesize Narrative Explanation
        explanation_lines = []
        explanation_lines.append(
            f"Overall Risk Score: {final_score}/100 ({risk_level.upper()})."
        )

        if rule_result.triggered_rules:
            explanation_lines.append("Key Threat Indicators Detected:")
            for r in rule_result.triggered_rules:
                explanation_lines.append(f"• [{r.severity.upper()}] {r.name}: '{r.evidence_text}'")
        else:
            explanation_lines.append("No explicit deterministic scam signatures triggered.")

        if verification_result and verification_result.signals:
            explanation_lines.append("Domain & Identity Verification Signals:")
            for s in verification_result.signals:
                explanation_lines.append(f"• [{s.severity.upper()}] {s.name}: {s.description}")

        explanation_lines.append(
            f"ML Classifier evaluated text with {ml_prob * 100:.1f}% statistical likelihood towards '{ml_label}' profile (+{ml_contribution} pts)."
        )

        full_explanation = "\n".join(explanation_lines)

        # 7. Aggregate and Prioritize Recommendations
        recommendations: List[Dict[str, str]] = []
        seen_recs = set()

        for r in rule_result.triggered_rules:
            if r.recommendation and r.recommendation not in seen_recs:
                seen_recs.add(r.recommendation)
                priority = "urgent" if r.severity in ["critical", "high"] else "advisory"
                recommendations.append({
                    "priority": priority,
                    "action": r.name,
                    "detail": r.recommendation,
                })

        if verification_result and verification_result.signals:
            for s in verification_result.signals:
                rec_text = f"Verify {s.name.lower()} independently with corporate registry before sharing data."
                if rec_text not in seen_recs:
                    seen_recs.add(rec_text)
                    recommendations.append({
                        "priority": "advisory",
                        "action": s.name,
                        "detail": s.description,
                    })

        if not recommendations:
            recommendations.append({
                "priority": "advisory",
                "action": "Standard Verification",
                "detail": "Always verify job postings directly on the employer's official corporate careers website.",
            })

        breakdown = RiskScoreBreakdown(
            ml_contribution=ml_contribution,
            ml_probability=round(ml_prob, 4),
            rule_contribution=rule_contribution,
            category_breakdown=rule_result.category_scores,
            domain_penalty=domain_penalty,
            total_score=final_score,
        )

        return RiskEngineResult(
            final_score=final_score,
            risk_level=risk_level,
            score_breakdown=breakdown,
            triggered_indicators=rule_result.triggered_rules,
            explanation=full_explanation,
            recommendations=recommendations,
            engine_version=self.VERSION,
        )


risk_engine = RiskEngine()
