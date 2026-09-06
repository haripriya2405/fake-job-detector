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
        """Call Gemini or OpenAI LLM API with strict factual grounding on verification signals."""
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

    @staticmethod
    def _is_indian_recruitment_context(text: str, title: Optional[str] = None, company: Optional[str] = None) -> bool:
        """Heuristic check if job posting or message originates from Indian recruitment ecosystem."""
        combined = f"{text} {title or ''} {company or ''}".lower()
        indian_tokens = [
            "₹", "rs.", "rs ", "inr", "lpa", "lakh", "crore", "ctc",
            "upi", "gpay", "phonepe", "paytm", "bhim",
            "aadhaar", "pan card", "1930", "cybercrime.gov.in", "i4c",
            "naukri", "internshala", "foundit", "shine.com", "apna.co",
            "bangalore", "bengaluru", "hyderabad", "pune", "mumbai", "gurgaon", "noida", "chennai", "delhi",
            "tcs", "infosys", "wipro", "hcl", "tata consultancy", "swiggy", "zomato", "flipkart",
        ]
        return any(tok in combined for tok in indian_tokens)

    @staticmethod
    async def generate_llm_explanation_async(
        raw_text: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
        risk_score: int = 0,
        risk_level: str = "low",
        verification_signals: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini or OpenAI LLM API with strict factual grounding on verification signals."""
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not gemini_key and not openai_key:
            return None

        is_indian = AIExplainer._is_indian_recruitment_context(raw_text, job_title, company_name)
        regional_context = (
            "REGIONAL CONTEXT: Indian recruitment ecosystem (INR ₹, LPA, UPI, Cybercrime India / 1930 helpline). "
            "If suspicious, emphasize that legitimate Indian employers (TCS, Infosys, Wipro, etc.) NEVER charge fees via UPI "
            "and candidates should report fraud to 1930 Helpline or cybercrime.gov.in."
            if is_indian else "REGIONAL CONTEXT: Global recruitment ecosystem (USD $, Wire transfers, Cashier checks, FTC / IC3)."
        )

        prompt = f"""
You are an expert Cybersecurity & Job Fraud Forensic Analyst. Analyze the following job posting telemetry and verification signals:

{regional_context}
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

        # 1. Try Gemini API
        if gemini_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
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
                logger.warning(f"Gemini API call failed: {e}")

        # 2. Try OpenAI API
        if openai_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    url = "https://api.openai.com/v1/chat/completions"
                    headers = {
                        "Authorization": f"Bearer {openai_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a cyber fraud forensic investigator. Output strictly valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.2
                    }
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        result = resp.json()
                        text_content = result["choices"][0]["message"]["content"]
                        return json.loads(text_content)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}")

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
        salary_explanation: Optional[str] = None,
        careers_explanation: Optional[str] = None,
        recruiter_email: Optional[str] = None,
        page_count: Optional[int] = None,
        extraction_method: Optional[str] = None,
    ) -> str:
        """Construct a structured, multi-section forensic explanation grounded on empirical evidence."""
        lines = []
        is_indian = AIExplainer._is_indian_recruitment_context(raw_text, job_title, company_name)

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
                f"• The Deep NLP Classifier detected strong linguistic manipulation patterns with **{ml_prob * 100:.1f}% statistical probability** of deceptive recruitment behavior."
            )
        elif ml_prob > 0.25:
            lines.append(
                f"• The Deep NLP Classifier flagged moderate non-standard phrasing with **{ml_prob * 100:.1f}% probability** of non-standard recruitment behavior."
            )
        else:
            lines.append(
                f"• The Deep NLP Classifier identified authentic, professional corporate recruitment terminology with **{(1 - ml_prob) * 100:.1f}% confidence** in its legitimacy."
            )

        # Highlighted Manipulative Spans
        if ml_highlights:
            lines.append("\n**Key Flagged Phrases:**")
            seen_spans = set()
            for h in ml_highlights[:5]:
                matched = h.get("matched_text", "")
                cat = h.get("category", "manipulation").replace("_", " ").title()
                if matched and matched.lower() not in seen_spans:
                    seen_spans.add(matched.lower())
                    ctx = h.get("context_sentence", "").strip()
                    ctx_str = f" — *\"{ctx}\"*" if ctx else ""
                    lines.append(f"  - **{cat}**: \"`{matched}`\"{ctx_str}")

        # 3. Rule Engine & Threat Signals
        if triggered_indicators:
            lines.append("\n#### Identified Threat Signals:")
            for ind in triggered_indicators[:6]:
                name = getattr(ind, "name", getattr(ind, "title", str(ind)))
                desc = getattr(ind, "explanation", getattr(ind, "description", ""))
                sev = getattr(ind, "severity", "medium").upper()
                lines.append(f"• **[{sev}] {name}**: {desc}")

        # 4. Domain & Identity Assessment
        if verification_signals:
            lines.append("\n#### Entity & Domain Verification:")
            for s in verification_signals[:4]:
                s_name = getattr(s, "name", str(s))
                s_desc = getattr(s, "description", "")
                lines.append(f"• **{s_name}**: {s_desc}")

        # 5. Compensation & Market Alignment
        if salary_explanation:
            lines.append(f"\n#### Market Compensation Benchmark:\n• {salary_explanation}")

        # 6. Careers Page & Channel Authenticity
        if careers_explanation:
            lines.append(f"\n#### Careers Page & Application Channel:\n• {careers_explanation}")

        # 7. Actionable Next Steps (Localized for Indian & Global users)
        lines.append("\n#### Recommended Next Steps:")
        if risk_level in ["critical", "high"]:
            if is_indian:
                lines.append("1. **Do not send money via UPI/QR code**: Major Indian IT enterprises (TCS, Infosys, Wipro, Cognizant, etc.) **never charge fees** for registration, laptop gatepass, or security deposits.")
                lines.append("2. **Protect Aadhaar & PAN**: Never share your Aadhaar OTP or banking passwords with unverified recruiters over WhatsApp or Telegram.")
                lines.append("3. **Report to Indian Authorities**: Lodge a complaint with the **National Cyber Crime Reporting Portal** at [cybercrime.gov.in](https://cybercrime.gov.in) or call the **1930 National Cybercrime Helpline**.")
                lines.append("4. **Cross-reference Official Careers**: Apply directly through verified enterprise career portals (e.g., `ibegin.tcs.com`, `careers.infosys.com`) or trusted portals (Naukri, Internshala).")
            else:
                lines.append("1. **Do not send money or banking info**: Never purchase equipment from vendor links, wire funds, or deposit cashier checks.")
                lines.append("2. **Do not communicate off-platform**: Cease communication immediately if asked to move to Telegram, WhatsApp, or personal email.")
                lines.append("3. **Cross-reference officially**: Search the legitimate company's official career portal to confirm if the requisition ID actually exists.")
                lines.append("4. **Report Scam**: File an alert with the FTC at [reportfraud.ftc.gov](https://reportfraud.ftc.gov) or FBI IC3.")
        elif risk_level == "medium":
            if is_indian:
                lines.append("1. **Verify Recruiter Credentials**: Ensure the recruiter uses an official company domain email (not generic `@gmail.com` or spoofed domains).")
                lines.append("2. **Refuse Upfront Charges**: Legitimate Indian companies do not require payment for software license keys, typing kits, or interview slots.")
                lines.append("3. **Check Official Portals**: Search for the job opening on official portals (Naukri, LinkedIn, or the employer's official website).")
            else:
                lines.append("1. **Verify recruiter credentials**: Confirm the sender's identity through official LinkedIn corporate staff profiles or corporate email domain.")
                lines.append("2. **Refuse upfront fees**: Legitimate employers will never request security deposits, background check fees, or training costs.")
                lines.append("3. **Cross-verify posting**: Check if this exact role is advertised on the company's verified primary domain.")
        else:
            if is_indian:
                lines.append("1. **Standard Due Diligence**: The posting exhibits clean enterprise markers. Submit your application directly through the employer's official portal or verified portal (Naukri, LinkedIn, Internshala).")
            else:
                lines.append("1. **Standard Due Diligence**: The posting shows clean metrics. Ensure you submit your application directly through the employer's official verified portal.")

        return "\n".join(lines)


ai_explainer = AIExplainer()
