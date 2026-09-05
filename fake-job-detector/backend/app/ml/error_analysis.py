"""Model Disagreement & Error Analysis Engine (Phase 20).
Analyzes prediction divergences between Baseline and Candidate models without exposing PII.
"""

from typing import Any, Dict, List, Optional
import re
import numpy as np
import pandas as pd


class ErrorAnalyzer:
    """Dissects classification discrepancies, false positives, and false negatives."""

    ERROR_CATEGORIES = [
        "fake_check_reimbursement",
        "upfront_fee_demand",
        "crypto_payment_task",
        "channel_diversion",
        "credential_harvesting",
        "recruiter_impersonation",
        "typosquatted_domain",
        "urgent_onboarding",
        "unusual_legitimate_job",
        "borderline_compensation",
        "linguistic_obfuscation",
    ]

    @staticmethod
    def sanitize_pii(text: str) -> str:
        """Strip and redact any personally identifiable info from logs & reports."""
        # Redact emails
        text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[REDACTED_EMAIL]", text)
        # Redact phone numbers
        text = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]", text)
        # Redact crypto wallet addresses
        text = re.sub(r"\b(?:0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[A-Za-z1-9]{33})\b", "[REDACTED_WALLET]", text)
        # Redact passwords/pins/tokens
        text = re.sub(r"(?i)(password|pin|otp|token)\s*[:=]\s*\S+", r"\1: [REDACTED]", text)
        return text

    def categorize_sample(self, text: str, label: int) -> str:
        """Determine specific fraud vector or legitimate subcategory."""
        lower = text.lower()
        if label == 1:
            if "check" in lower or "cheque" in lower or "cashier" in lower:
                return "fake_check_reimbursement"
            elif "fee" in lower or "deposit" in lower or "registration" in lower or "bond" in lower:
                return "upfront_fee_demand"
            elif "usdt" in lower or "crypto" in lower or "wallet" in lower or "vip" in lower:
                return "crypto_payment_task"
            elif "telegram" in lower or "whatsapp" in lower or "signal" in lower or "t.me" in lower:
                return "channel_diversion"
            elif "password" in lower or "pin" in lower or "otp" in lower or "netbanking" in lower:
                return "credential_harvesting"
            elif "xyz" in lower or "top" in lower or "portal-apply" in lower:
                return "typosquatted_domain"
            elif "urgent" in lower or "hours" in lower or "immediate selection" in lower:
                return "urgent_onboarding"
            return "linguistic_obfuscation"
        else:
            if "remote" in lower and ("hourly" in lower or "contract" in lower):
                return "borderline_compensation"
            return "unusual_legitimate_job"

    def analyze_disagreements(
        self,
        holdout_df: pd.DataFrame,
        base_probs: List[float],
        cand_probs: List[float],
        threshold: float = 0.50,
    ) -> Dict[str, Any]:
        """Classify case agreements and disagreements across holdout."""
        y_true = holdout_df["label"].values.astype(int)
        raw_texts = holdout_df["text"].tolist()
        record_ids = holdout_df.get("record_id", [f"REC-{i:04d}" for i in range(len(y_true))]).tolist()

        base_preds = (np.array(base_probs) >= threshold).astype(int)
        cand_preds = (np.array(cand_probs) >= threshold).astype(int)

        cases: List[Dict[str, Any]] = []
        category_counts: Dict[str, int] = {cat: 0 for cat in self.ERROR_CATEGORIES}

        classifications = {
            "BOTH_CORRECT": 0,
            "BASELINE_CORRECT": 0,
            "TRANSFORMER_CORRECT": 0,
            "BOTH_WRONG": 0,
            "AMBIGUOUS": 0,
        }

        for i in range(len(y_true)):
            yt = y_true[i]
            bp = base_preds[i]
            cp = cand_preds[i]
            b_prob = float(base_probs[i])
            c_prob = float(cand_probs[i])
            text = raw_texts[i]
            rec_id = record_ids[i]

            b_correct = (bp == yt)
            c_correct = (cp == yt)

            if b_correct and c_correct:
                case_type = "BOTH_CORRECT"
            elif b_correct and not c_correct:
                case_type = "BASELINE_CORRECT"
            elif not b_correct and c_correct:
                case_type = "TRANSFORMER_CORRECT"
            else:
                case_type = "BOTH_WRONG"

            # Ambiguity flag when probabilities hover near decision threshold
            if abs(b_prob - 0.50) < 0.08 and abs(c_prob - 0.50) < 0.08:
                case_type = "AMBIGUOUS"

            classifications[case_type] += 1
            cat = self.categorize_sample(text, yt)
            category_counts[cat] = category_counts.get(cat, 0) + 1

            cases.append({
                "record_id": rec_id,
                "true_label": int(yt),
                "baseline_prob": round(b_prob, 4),
                "candidate_prob": round(c_prob, 4),
                "baseline_pred": int(bp),
                "candidate_pred": int(cp),
                "case_classification": case_type,
                "category": cat,
                "sanitized_snippet": self.sanitize_pii(text[:140]) + ("..." if len(text) > 140 else ""),
            })

        disagreements = [c for c in cases if c["case_classification"] in ["BASELINE_CORRECT", "TRANSFORMER_CORRECT", "BOTH_WRONG", "AMBIGUOUS"]]

        return {
            "total_analyzed": len(y_true),
            "summary_counts": classifications,
            "category_error_distribution": category_counts,
            "disagreement_count": len(disagreements),
            "disagreement_cases": disagreements,
        }
