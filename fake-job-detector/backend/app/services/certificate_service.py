import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.analysis import Analysis
from app.schemas.certificate import VerificationCertificateResponse


class CertificateService:
    """Service for generating, validating, and rendering tamper-evident job verification certificates & badges."""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = (secret_key or getattr(settings, "SECRET_KEY", "sentinel-jobscamscore-secret-2026")).encode("utf-8")

    def generate_signature(
        self, analysis_id: str, risk_score: int, company_name: str, created_at: datetime
    ) -> str:
        """Generate HMAC-SHA256 tamper-evident digital signature."""
        ts_str = created_at.isoformat() if isinstance(created_at, datetime) else str(created_at)
        payload = f"{analysis_id}:{risk_score}:{company_name}:{ts_str}".encode("utf-8")
        return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()

    def verify_signature(
        self, signature: str, analysis_id: str, risk_score: int, company_name: str, created_at: datetime
    ) -> bool:
        """Verify HMAC-SHA256 signature against payload."""
        expected = self.generate_signature(analysis_id, risk_score, company_name, created_at)
        return hmac.compare_digest(signature, expected)

    def compute_sha256_fingerprint(self, raw_content: str) -> str:
        """Compute SHA-256 hash of job posting content."""
        return hashlib.sha256((raw_content or "").encode("utf-8")).hexdigest()

    def get_certificate_data(
        self, db: Session, identifier: str, base_url: str = "https://jobscamscore.com"
    ) -> Optional[VerificationCertificateResponse]:
        """Fetch analysis and build complete cryptographic certificate payload."""
        analysis = None

        # Try parsing as direct UUID
        try:
            uuid_val = uuid.UUID(identifier)
            analysis = db.query(Analysis).filter(Analysis.id == uuid_val).first()
        except ValueError:
            pass

        # Try matching if identifier is in certificate format e.g. JS-CERT-2026-XXXXXXXX
        if not analysis:
            clean_id = identifier.replace("JS-CERT-", "").replace("CERT-", "").strip()
            # If 8-hex prefix or year-prefix
            parts = clean_id.split("-")
            hex_part = parts[-1] if len(parts) > 1 else clean_id
            
            # Match UUID prefix
            for a in db.query(Analysis).order_by(Analysis.created_at.desc()).limit(100).all():
                if a.id.hex.upper().startswith(hex_part.upper()):
                    analysis = a
                    break

        if not analysis:
            return None

        # Determine Verdict and Color
        score = analysis.risk_score or 0
        if score <= 30:
            verdict = "VERIFIED_SAFE"
            badge_color = "emerald"
            summary = (
                f"Official security audit indicates high legitimacy for {analysis.company_name or 'the employer'}. "
                "No critical scam indicators, deceptive email domains, or payment coercion tactics were detected."
            )
        elif score <= 65:
            verdict = "CAUTION_ADVISED"
            badge_color = "amber"
            summary = (
                "Moderate risk indicators detected. We advise verifying this position directly on the employer's official "
                "careers portal before providing personal documents or responding to unverified communication channels."
            )
        else:
            verdict = "HIGH_RISK_SUSPICIOUS"
            badge_color = "crimson"
            summary = (
                "CRITICAL WARNING: High probability of recruitment fraud, advance check cashing trap, "
                "or deceptive impersonation. Do NOT send money, crypto, or sensitive personal credentials."
            )

        # Canonical Certificate ID
        cert_id = f"JS-CERT-{analysis.created_at.year}-{analysis.id.hex[:8].upper()}"

        # Digital Signature & Fingerprint
        sig = self.generate_signature(
            str(analysis.id), score, analysis.company_name or "Unknown", analysis.created_at
        )
        is_valid = self.verify_signature(
            sig, str(analysis.id), score, analysis.company_name or "Unknown", analysis.created_at
        )
        fingerprint = self.compute_sha256_fingerprint(analysis.raw_content or "")

        # Key Indicators
        indicators = []
        if analysis.explanation:
            indicators.append(analysis.explanation)
        for ind in getattr(analysis, "indicators", []):
            if getattr(ind, "description", None):
                indicators.append(ind.description)

        share_url = f"{base_url}/verify/{cert_id}"
        badge_svg_url = f"{base_url}/api/v1/verify/{cert_id}/badge.svg"

        embed_md = f"[![JobScamScore Verified]({badge_svg_url})]({share_url})"
        embed_html = f'<a href="{share_url}" target="_blank" rel="noopener noreferrer"><img src="{badge_svg_url}" alt="JobScamScore Verification Badge" /></a>'

        return VerificationCertificateResponse(
            certificate_id=cert_id,
            analysis_id=str(analysis.id),
            job_title=analysis.job_title or "Unspecified Job Title",
            company_name=analysis.company_name or "Unknown Entity",
            risk_score=score,
            risk_level=analysis.risk_level or "low",
            legitimacy_verdict=verdict,
            verdict_badge_color=badge_color,
            is_tamper_evident_valid=is_valid,
            digital_signature=sig,
            sha256_fingerprint=fingerprint,
            analyzed_at=analysis.created_at,
            verified_at=datetime.now(timezone.utc),
            summary=summary,
            key_indicators=indicators[:5],
            shareable_url=share_url,
            embed_badge_markdown=embed_md,
            embed_badge_html=embed_html,
            embed_badge_svg_url=badge_svg_url,
        )

    def render_svg_badge(self, cert: VerificationCertificateResponse) -> str:
        """Render high-resolution vector SVG trust badge."""
        if cert.verdict_badge_color == "emerald":
            bg_left = "#064e3b"
            bg_right = "#059669"
            label = "VERIFIED SAFE"
            score_text = f"{100 - cert.risk_score}/100 Legit"
        elif cert.verdict_badge_color == "amber":
            bg_left = "#78350f"
            bg_right = "#d97706"
            label = "CAUTION REQUIRED"
            score_text = f"{cert.risk_score}/100 Risk"
        else:
            bg_left = "#881337"
            bg_right = "#e11d48"
            label = "SUSPICIOUS FRAUD"
            score_text = f"{cert.risk_score}/100 Risk"

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="280" height="34" viewBox="0 0 280 34" fill="none" role="img" aria-label="JobScamScore: {label}">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="280" y2="34" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{bg_left}" />
      <stop offset="100%" stop-color="{bg_right}" />
    </linearGradient>
    <filter id="shadow" x="-2" y="-2" width="284" height="38" filterUnits="userSpaceOnUse">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>
  <rect width="280" height="34" rx="6" fill="url(#grad)" filter="url(#shadow)" stroke="#ffffff" stroke-opacity="0.2" stroke-width="1"/>
  <!-- Left Brand Tag -->
  <rect x="0" y="0" width="115" height="34" rx="6" fill="#090d16" fill-opacity="0.85"/>
  <rect x="110" y="0" width="5" height="34" fill="#090d16" fill-opacity="0.85"/>
  <line x1="115" y1="0" x2="115" y2="34" stroke="#ffffff" stroke-opacity="0.15" stroke-width="1"/>
  
  <!-- Brand Text -->
  <text x="12" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="700" fill="#38bdf8" letter-spacing="0.5">JobScamScore</text>
  
  <!-- Verdict Status & Score -->
  <text x="126" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="11" font-weight="800" fill="#ffffff" letter-spacing="0.3">{label}</text>
  <text x="268" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif" font-size="10" font-weight="600" fill="#ffffff" fill-opacity="0.85" text-anchor="end">{score_text}</text>
</svg>"""


certificate_service = CertificateService()
