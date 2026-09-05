from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.rules.definitions import RULE_REGISTRY, RuleDefinition
from app.rules.schemas import RuleEngineResult, TriggeredRule


class RuleEngine:
    """Deterministic Security Rule Engine.
    Evaluates text against versioned security heuristics, extracts exact evidence quotes,
    and applies category caps and duplicate suppression.
    """

    VERSION = "rules-v1.0.0"

    # Category Maximum Score Caps (Configurable)
    CATEGORY_CAPS: Dict[str, int] = {
        "financial": 30,
        "crypto_task": 25,
        "compensation": 20,
        "manipulation": 15,
        "data_privacy": 15,
        "communication": 10,
        "content_quality": 10,
    }

    def __init__(self, rules: Optional[List[RuleDefinition]] = None):
        self.rules = rules or RULE_REGISTRY

    def _extract_evidence_context(self, text: str, match_span: tuple, pad: int = 40) -> str:
        """Extract matched snippet with surrounding sentence context."""
        start, end = match_span
        start_idx = max(0, start - pad)
        end_idx = min(len(text), end + pad)
        snippet = text[start_idx:end_idx].strip()
        if start_idx > 0:
            snippet = "..." + snippet
        if end_idx < len(text):
            snippet = snippet + "..."
        return snippet

    def evaluate(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> RuleEngineResult:
        """Evaluate input text against enabled security rules."""
        if not text:
            return RuleEngineResult(rule_version=self.VERSION)

        metadata = metadata or {}
        triggered: List[TriggeredRule] = []
        category_raw_scores: Dict[str, int] = {cat: 0 for cat in self.CATEGORY_CAPS}
        seen_evidence_spans: List[tuple] = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            evidence_quote = None
            span = None

            if rule.pattern:
                match = rule.pattern.search(text)
                if match:
                    span = match.span()
                    evidence_quote = self._extract_evidence_context(text, span)
            elif rule.custom_matcher:
                custom_match_str = rule.custom_matcher(text, metadata)
                if custom_match_str:
                    idx = text.lower().find(custom_match_str.lower())
                    span = (idx, idx + len(custom_match_str)) if idx != -1 else (0, len(custom_match_str))
                    evidence_quote = self._extract_evidence_context(text, span)

            if evidence_quote and span:
                # Correlated signal handling: check for exact span overlap with same category
                is_duplicate_span = any(
                    abs(s[0] - span[0]) < 10 and abs(s[1] - span[1]) < 10 for s in seen_evidence_spans
                )

                # Damped weight if exact overlapping snippet already triggered
                effective_weight = rule.default_weight if not is_duplicate_span else max(5, rule.default_weight // 2)
                seen_evidence_spans.append(span)

                triggered_rule = TriggeredRule(
                    rule_code=rule.code,
                    name=rule.name,
                    category=rule.category,
                    severity=rule.severity,
                    matched=True,
                    score_contribution=effective_weight,
                    confidence=rule.confidence,
                    evidence_text=evidence_quote,
                    explanation=rule.description,
                    recommendation=rule.recommendation,
                    rule_version=self.VERSION,
                )
                triggered.append(triggered_rule)
                category_raw_scores[rule.category] = category_raw_scores.get(rule.category, 0) + effective_weight

        # Apply Category Caps
        category_capped_scores: Dict[str, int] = {}
        total_capped_score = 0
        total_raw_score = sum(category_raw_scores.values())

        for cat, raw_score in category_raw_scores.items():
            cap = self.CATEGORY_CAPS.get(cat, 100)
            capped = min(raw_score, cap)
            category_capped_scores[cat] = capped
            total_capped_score += capped

        return RuleEngineResult(
            rule_version=self.VERSION,
            triggered_rules=triggered,
            category_scores=category_capped_scores,
            raw_score=total_raw_score,
            capped_score=total_capped_score,
        )


rule_engine = RuleEngine()
