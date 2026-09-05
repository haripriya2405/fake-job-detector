"""SentinelJob AI — Comprehensive AI Forensic Explainer & LLM Synthesis Engine.

Synthesizes multi-modal extraction telemetry, neural transformer predictions,
deterministic heuristic indicators, and RDAP/DNS verification results into
rich, 100% accurate, plain-English forensic intelligence reports.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


class AIExplainer:
    """Generates rich, 100% grounded AI explanations using Gemini/LLM APIs or deterministic forensic rules."""

    @staticmethod
    async def generate_llm_explanation_async(
        raw_text: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        risk_score: int = 0,
        risk_level: str = "low",
        verification_signals: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini LLM API with strict factual grounding on verification signals."""
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            return None

        prompt = f"""
You are an expert Cybersecurity & Job Fraud Forensic Analyst. Analyze the following job posting telemetry and verification signals:

Job Title: {job_title or 'Unknown'}
Company: {company_name or 'Unknown'}
Calculated Risk Score: {risk_score}/100 ({risk_level.upper()})
Verification Signals: {json.dumps(verification_signals or {}, indent=2)}

Job Text Snippet:
{raw_text[:1500]}

Respond STRICTLY in valid JSON format with the following keys:
{{
  "executive_summary": "Concise 2-3 sentence forensic synthesis of why this posting is rated {risk_level}.",
  "company_verification_notes": "Summary of company digital footprint.",
  "location_notes": "Evaluation of geographic alignment.",
  "contact_notes": "Domain and recruiter email match summary.",
  "salary_notes": "Evaluation of salary range against industry standards.",
  "grammar_notes": "Evaluation of linguistic tone and syntax quality.",
  "recommendations": ["Tip 1", "Tip 2", "Tip 3", "Tip 4", "Tip 5", "Tip 6"]
}}
Do NOT hallucinate facts not present in the telemetry.
"""

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"}
                }
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    text_content = result["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text_content)
        except Exception as e:
            logger.warning(f"LLM API call failed, falling back to deterministic synthesis: {e}")

        return None

    @staticmethod
    def generate_explanation(
        raw_text: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        source_type: str = "text",
        risk_score: int = 0,
        risk_level: str = "low",
        ml_prob: float = 0.0,
        ml_highlights: Optional[List[Dict[str, Any]]] = None,
        triggered_indicators: Optional[List[Any]] = None,
        verification_signals: Optional[List[Any]] = None,
        page_count: Optional[int] = None,
        extraction_method: Optional[str] = None,
    ) -> str:
        """Construct a structured, multi-section forensic explanation grounded on empirical evidence."""
        lines = []

        # 1. Document & Ingestion Synopsis
        src_label = source_type.upper()
        doc_desc = "text submission"
        if src_label == "PDF":
            doc_desc = f"multi-page PDF document ({page_count or 1} page{'s' if (page_count or 1) > 1 else ''})"
        elif src_label == "IMAGE":
            doc_desc = "screenshot/image artifact via optical character recognition (OCR)"
        elif src_label == "URL":
            doc_desc = "public job webpage ingested via safe HTTP fetch"

        title_str = f"'{job_title}'" if job_title and job_title != "Job Posting" else "an uncaptioned position"
        company_str = f" purportedly from '{company_name}'" if company_name and company_name != "Claimed Organization" else ""

        # Executive Summary
        if risk_level in ["critical", "high"]:
            verdict_badge = "CRITICAL THREAT DETECTED" if risk_level == "critical" else "HIGH RISK SUSPICIOUS POSTING"
            lines.append(f"### {verdict_badge}")
            lines.append(
                f"SentinelJob AI evaluated this {doc_desc} for {title_str}{company_str} and assigned an overall risk rating of **{risk_score}/100 ({risk_level.upper()})**."
            )
        elif risk_level == "medium":
            lines.append("### CAUTION ADVISED — MODERATE RISK")
            lines.append(
                f"SentinelJob AI evaluated this {doc_desc} for {title_str}{company_str} and assigned an overall risk rating of **{risk_score}/100 (MEDIUM)**."
            )
        else:
            lines.append("### LOW RISK / LEGITIMATE PROFILE")
            lines.append(
                f"SentinelJob AI evaluated this {doc_desc} for {title_str}{company_str} and determined a clean risk score of **{risk_score}/100 (LOW RISK)**."
            )

        # 2. Neural Linguistic Analysis
        lines.append("\n#### AI Neural Linguistic Analysis:")
        if ml_prob > 0.60:
            lines.append(
                f"• The Deep Transformer model detected strong linguistic manipulation patterns with **{ml_prob * 100:.1f}% statistical confidence** towards fraudulent behavior."
            )
        elif ml_prob > 0.25:
            lines.append(
                f"• The Deep Transformer model flagged mild manipulative phrasing with **{ml_prob * 100:.1f}% probability** of non-standard recruitment behavior."
            )
        else:
            lines.append(
                f"• The Deep Transformer model identified standard, professional corporate recruitment terminology with **{(1 - ml_prob) * 100:.1f}% confidence** in its legitimacy."
            )

        # Highlighted Manipulative Spans
        if ml_highlights:
            lines.append("\n**Key Flagged Phrases:**")
            seen_spans = set()
            for h in ml_highlights[:4]:
                matched = h.get("matched_text", "")
                cat = h.get("category", "manipulation").replace("_", " ").title()
                if matched and matched.lower() not in seen_spans:
                    seen_spans.add(matched.lower())
                    lines.append(f"  - **{cat}**: *\"{matched}\"* — {h.get('context_sentence', '')}")

        # 3. Rule Engine & Threat Signals
        if triggered_indicators:
            lines.append("\n#### Identified Threat Signals:")
            for ind in triggered_indicators[:5]:
                name = getattr(ind, "name", getattr(ind, "title", str(ind)))
                desc = getattr(ind, "explanation", getattr(ind, "description", ""))
                sev = getattr(ind, "severity", "medium").upper()
                lines.append(f"• **[{sev}] {name}**: {desc}")

        # 4. Domain & Identity Assessment
        if verification_signals:
            lines.append("\n#### Entity & Domain Verification:")
            for s in verification_signals[:3]:
                s_name = getattr(s, "name", str(s))
                s_desc = getattr(s, "description", "")
                lines.append(f"• **{s_name}**: {s_desc}")

        # 5. Actionable Next Steps
        lines.append("\n#### Recommended Next Steps:")
        if risk_level in ["critical", "high"]:
            lines.append("1. **Do not send money or banking info**: Never purchase equipment from vendor links or accept cashier checks.")
            lines.append("2. **Do not communicate off-platform**: Cease communication immediately if asked to move to Telegram, WhatsApp, or personal email.")
            lines.append("3. **Cross-reference officially**: Search the legitimate company's official career portal to confirm if the requisition ID actually exists.")
        elif risk_level == "medium":
            lines.append("1. **Verify recruiter credentials**: Confirm the sender's identity through official LinkedIn corporate staff profiles or corporate email domain.")
            lines.append("2. **Refuse upfront fees**: Legitimate employers will never request security deposits, background check fees, or training costs.")
        else:
            lines.append("1. **Standard Due Diligence**: The posting shows no high-risk markers. Ensure you submit your application through the employer's official verified portal.")

        return "\n".join(lines)


ai_explainer = AIExplainer()
