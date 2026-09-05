"""Separate Adversarial & Obfuscation Robustness Benchmark (Phase 7D).
Contains synthetic and heavily mutated adversarial threat patterns:
- Spaced keywords ('r e g i s t r a t i o n', 'T e l e g r a m')
- Punctuation insertion ('c.a.s.h.i.e.r - c.h.e.c.k')
- Evasive paraphrasing ('refundable equipment onboarding security bond')
- Disguised crypto task recharge ('workstation rating optimization wallet')
- Homoglyph / character substitutions
Kept strictly separate from the real-world holdout dataset to prevent distribution contamination.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pydantic import BaseModel, Field


class AdversarialTestCase(BaseModel):
    case_id: str
    attack_type: str
    description: str
    raw_text: str
    expected_label: int = 1  # All are deceptive threats
    notes: str


ADVERSARIAL_ROBUSTNESS_CORPUS: List[Dict[str, Any]] = [
    {
        "case_id": "ADV-SPACE-01",
        "attack_type": "spaced_keyword_evasion",
        "description": "Spaced letters in registration fee and Telegram handle",
        "text": "Immediate home typist vacancy! Earn Rs. 40,000 per week. Pay mandatory r e g i s t r a t i o n fee of Rs. 2,000 before onboarding. Contact manager on T e l e g r a m @Scam_HR.",
        "notes": "Tests model sensitivity to spaced whitespace splitting of core threat words.",
    },
    {
        "case_id": "ADV-SPACE-02",
        "attack_type": "spaced_keyword_evasion",
        "description": "Spaced crypto payment terminology",
        "text": "Earn $300 daily rating travel hotels. Transfer 100 U S D T to company w a l l e t address to activate daily withdrawal VIP privilege.",
        "notes": "Tests spaced cryptocurrency token detection.",
    },
    {
        "case_id": "ADV-PUNCT-01",
        "attack_type": "punctuation_injection",
        "description": "Period-injected cashier check and wire transfer terminology",
        "text": "Virtual Assistant: We mail a c.a.s.h.i.e.r - c.h.e.c.k of $4,500. Deposit at your bank, keep 10%, and w.i.r.e remainder to supplier via W.e.s.t.e.r.n U.n.i.o.n.",
        "notes": "Tests resilience against punctuation insertion inside money mule keywords.",
    },
    {
        "case_id": "ADV-PARAPH-01",
        "attack_type": "paraphrased_fee_disguise",
        "description": "Advance fee disguised as refundable courier insurance contribution",
        "text": "Remote Publishing Clerk ($55/hour). A fully refundable onboarding security contribution of $185 is required for specialized equipment transit courier insurance before interview.",
        "notes": "Tests semantic comprehension of advance-fee schemes using corporate insurance jargon.",
    },
    {
        "case_id": "ADV-PARAPH-02",
        "attack_type": "paraphrased_task_disguise",
        "description": "Crypto task scheme disguised as merchant workstation optimization",
        "text": "E-Commerce Optimization Associate: Work 20 minutes daily. Fund your personal workstation balance with $50 to unlock tier-2 product optimization tasks and receive daily commission settlements.",
        "notes": "Tests recognition of deposit-to-work brush task fraud framed as workstation funding.",
    },
    {
        "case_id": "ADV-PII-01",
        "attack_type": "credential_harvesting_disguise",
        "description": "Direct deposit setup demanding bank netbanking password and OTP",
        "text": "Congratulations on your selection! To initiate direct payroll deposit, reply to this message with your online banking username, password, and the 6-digit authentication PIN sent to your phone.",
        "notes": "Tests critical detection of OTP and credential theft in onboarding lures.",
    },
    {
        "case_id": "ADV-IMPER-01",
        "attack_type": "typosquatted_brand_lure",
        "description": "Typosquatted corporate subdomain demanding application fee",
        "text": "Google Cloud Infrastructure is hiring Remote DevOps Engineers. Salary $190,000. Submit your credentials at https://google-careers-portal-apply.xyz and pay $45 test bench verification fee.",
        "notes": "Tests brand lookalike combined with advance screening fee.",
    },
    {
        "case_id": "ADV-HOMO-01",
        "attack_type": "unicode_homoglyph",
        "description": "Cyrillic homoglyph substitution in key payment tokens",
        "text": "URGENT HIRING: Wоrk frоm hоmе Dаtа Еntrу. Pау rеgіstrаtіоn dероsіt vіа GРау tо HR dеsk bеfоrе stаrt.",
        "notes": "Tests NFKC unicode normalization defense against Cyrillic visual lookalike characters.",
    },
]


class AdversarialBenchmarkEvaluator:
    """Evaluates text classification models strictly on the separate adversarial benchmark."""

    def __init__(self, corpus: Optional[List[Dict[str, Any]]] = None):
        self.corpus = corpus or ADVERSARIAL_ROBUSTNESS_CORPUS

    def get_benchmark_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.corpus)

    def evaluate_model_robustness(self, pipeline: Any, preprocessor_func: Any) -> Dict[str, Any]:
        """Evaluate how many adversarial evasion attempts are successfully flagged as fraud."""
        df = self.get_benchmark_df()
        raw_texts = df["text"].tolist()
        cleaned_texts = [preprocessor_func(t) for t in raw_texts]
        expected = [1] * len(raw_texts)

        preds = pipeline.predict(cleaned_texts)
        if hasattr(pipeline, "predict_proba"):
            probs = pipeline.predict_proba(cleaned_texts)[:, 1]
        else:
            probs = preds.astype(float)

        caught = sum(1 for p in preds if p == 1)
        total = len(expected)
        adversarial_recall = caught / total if total > 0 else 0.0

        details = []
        for i, row in df.iterrows():
            is_caught = bool(preds[i] == 1)
            details.append({
                "case_id": row["case_id"],
                "attack_type": row["attack_type"],
                "predicted_probability": round(float(probs[i]), 4),
                "is_detected": is_caught,
            })

        return {
            "total_adversarial_cases": total,
            "detected_threats": caught,
            "evaded_threats": total - caught,
            "adversarial_recall": round(float(adversarial_recall), 4),
            "robustness_score": round(float(adversarial_recall * 100.0), 2),
            "case_breakdown": details,
        }
