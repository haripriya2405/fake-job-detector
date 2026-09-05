import json
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, or_, select
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.analysis import Analysis
from app.models.community_scam import CommunityScam
from app.schemas.community_scam import CommunityScamResponse


class CommunityScamService:
    """Service layer managing public community scam database, PII redaction, and threat intelligence."""

    DEFAULT_THREAT_CORPUS = [
        {
            "public_id": "SCAM-2026-1001",
            "job_title": "Remote Data Entry & Billing Assistant",
            "impostor_company": "Apex Global Logistics Inc (Impostor)",
            "impostor_domain": "apex-logistics-careers.net",
            "contact_platform": "Telegram (@ApexRecruit_Dave)",
            "scam_category": "TELEGRAM_INTERVIEW",
            "risk_score": 96,
            "risk_level": "critical",
            "description_snippet": "Immediate opening for remote data entry typist. Hourly pay $45.00/hr. Interview conducted exclusively via Telegram text chat with hiring manager Mr. Dave. No video call required.",
            "red_flags": [
                "Recruiter demanded interview via Telegram messaging app",
                "Unrealistic entry-level salary ($45/hr vs $18/hr market average)",
                "Recently registered lookalike domain (apex-logistics-careers.net < 14 days old)",
                "Refusal to conduct official video/phone interview"
            ],
            "evidence_summary": "Classic Telegram interview funnel redirecting applicants away from corporate verification to request fake check software deposits.",
            "community_confirmations": 42,
            "is_verified_threat": True,
            "source_dataset": "THREAT_INTEL",
        },
        {
            "public_id": "SCAM-2026-1002",
            "job_title": "Executive Virtual Assistant & Scheduler",
            "impostor_company": "Vertex Healthcare Solutions",
            "impostor_domain": "vertex-health-jobs.org",
            "contact_platform": "Direct Email / SMS",
            "scam_category": "CHECK_FRAUD",
            "risk_score": 98,
            "risk_level": "critical",
            "description_snippet": "We are mailing you an advance cashier check for $3,850.00 to purchase home office equipment (MacBook Pro, scanner) from our certified vendor. Deposit the check immediately and Zelle the remaining balance to vendor.",
            "red_flags": [
                "Advance cashier check mailed before employment contract",
                "Instruction to forward remaining funds via Zelle/Wire to 'certified vendor'",
                "Classic fake check overpayment scam targeting job seekers",
                "Job offer issued without formal background check"
            ],
            "evidence_summary": "Fake cashier check trap. The check bounces after 3-5 business days, leaving victim liable for the forwarded Zelle funds.",
            "community_confirmations": 89,
            "is_verified_threat": True,
            "source_dataset": "EMSCAD",
        },
        {
            "public_id": "SCAM-2026-1003",
            "job_title": "Product Review & Rating Specialist",
            "impostor_company": "OmniMedia Digital Marketing",
            "impostor_domain": "omnimediagroup-app.cc",
            "contact_platform": "WhatsApp Web Task App",
            "scam_category": "CRYPTO_TASK",
            "risk_score": 95,
            "risk_level": "critical",
            "description_snippet": "Earn 200-500 USDT daily rating e-commerce products online. Complete 38 tasks per day. Negative balance requires deposit of USDT recharge to unlock commission withdrawals.",
            "red_flags": [
                "Task rating optimization scam requiring crypto deposits",
                "Demands USDT/Cryptocurrency deposit to unlock locked commission earnings",
                "Fake commission portal hosted on untrusted .cc top-level domain",
                "Recruitment solicited via unsolicited WhatsApp messages"
            ],
            "evidence_summary": "Task-based optimization ponzi trap. Victims are coerced into escalating crypto recharges to unlock fabricated balances.",
            "community_confirmations": 67,
            "is_verified_threat": True,
            "source_dataset": "SPAM_SMS",
        },
        {
            "public_id": "SCAM-2026-1004",
            "job_title": "Junior Python / React Remote Intern",
            "impostor_company": "CloudForge Tech Academy",
            "impostor_domain": "cloudforge-internships.info",
            "contact_platform": "Email",
            "scam_category": "UPFRONT_FEE",
            "risk_score": 92,
            "risk_level": "high",
            "description_snippet": "Guaranteed remote software internship with stipend upon completion. A mandatory $199.00 screening onboarding registration & software license fee must be paid via Venmo/CashApp prior to offer letter release.",
            "red_flags": [
                "Mandatory upfront registration fee ($199) required to secure internship",
                "Payment requested via irreversible peer-to-peer apps (Venmo/CashApp)",
                "Legitimate employers never charge candidates for job application or onboarding",
                "Generic template offer letter sent within 10 minutes of resume submission"
            ],
            "evidence_summary": "Pay-to-work internship scheme exploiting students and early career developers.",
            "community_confirmations": 31,
            "is_verified_threat": True,
            "source_dataset": "COMMUNITY",
        },
        {
            "public_id": "SCAM-2026-1005",
            "job_title": "Customer Onboarding Specialist",
            "impostor_company": "BioPharm Diagnostics Group",
            "impostor_domain": "biopharm-careers@gmail.com",
            "contact_platform": "Freemail / Gmail",
            "scam_category": "DATA_HARVESTING",
            "risk_score": 88,
            "risk_level": "high",
            "description_snippet": "Immediate hire. Send photo ID, SSN, copy of driver license and deposit bank details to hr@gmail.com on Telegram to receive advance check for home equipment.",
            "red_flags": [
                "Demands SSN, driver's license, and banking details prior to any interview",
                "Official enterprise communications sent from free @gmail.com address",
                "High urgency pressure ('Must submit within 2 hours to hold spot')",
                "Identity theft harvesting funnel targeting job applicant credentials"
            ],
            "evidence_summary": "Identity harvesting attack collecting PII and banking information under the guise of pre-interview onboarding.",
            "community_confirmations": 54,
            "is_verified_threat": True,
            "source_dataset": "THREAT_INTEL",
        },
    ]

    @staticmethod
    def redact_pii(text: str) -> str:
        """Sanitize personal identifiable information (emails, phone numbers, SSNs, credit cards)."""
        if not text:
            return ""

        # Redact candidate specific emails (preserve domain name if corporate)
        def _mask_email(match):
            user, domain = match.group(1), match.group(2)
            masked_user = user[0] + "***" if len(user) > 1 else "***"
            return f"{masked_user}@{domain}"

        text = re.sub(r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b", _mask_email, text)

        # Redact US/international phone numbers
        text = re.sub(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", "[REDACTED PHONE]", text)

        # Redact Social Security Numbers (SSN)
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED SSN]", text)

        # Redact Credit card / Bank account patterns
        text = re.sub(r"\b(?:\d[ -]*?){13,16}\b", "[REDACTED ACCOUNT/CARD]", text)

        return text

    def ensure_seeded_corpus(self, db: Session) -> None:
        """Pre-populate default threat intelligence corpus if table is empty."""
        try:
            count = db.query(func.count(CommunityScam.id)).scalar() or 0

            if count == 0:
                logger.info("Pre-seeding Community Scam Threat Database with curated intelligence...")
                for item in self.DEFAULT_THREAT_CORPUS:
                    scam = CommunityScam(
                        public_id=item["public_id"],
                        job_title=item["job_title"],
                        impostor_company=item["impostor_company"],
                        impostor_domain=item.get("impostor_domain"),
                        contact_platform=item.get("contact_platform"),
                        scam_category=item["scam_category"],
                        risk_score=item["risk_score"],
                        risk_level=item["risk_level"],
                        description_snippet=self.redact_pii(item["description_snippet"]),
                        red_flags=json.dumps(item["red_flags"]),
                        evidence_summary=item.get("evidence_summary"),
                        community_confirmations=item.get("community_confirmations", 1),
                        is_verified_threat=item.get("is_verified_threat", True),
                        source_dataset=item.get("source_dataset", "THREAT_INTEL"),
                    )
                    db.add(scam)
                db.commit()
                logger.info(f"Successfully seeded {len(self.DEFAULT_THREAT_CORPUS)} threat records.")
        except Exception as e:
            logger.warning(f"Failed to seed community threat database: {e}")
            db.rollback()

    def get_scam_feed(
        self,
        db: Session,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_risk_score: Optional[int] = None,
        verified_only: bool = False,
        sort_by: str = "newest",
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """Query and paginate public community scam database with filters."""
        self.ensure_seeded_corpus(db)

        q = db.query(CommunityScam)

        # Filters
        if query and query.strip():
            clean_q = f"%{query.strip().lower()}%"
            q = q.filter(
                or_(
                    func.lower(CommunityScam.job_title).like(clean_q),
                    func.lower(CommunityScam.impostor_company).like(clean_q),
                    func.lower(CommunityScam.impostor_domain).like(clean_q),
                    func.lower(CommunityScam.description_snippet).like(clean_q),
                )
            )

        if category and category.upper() != "ALL":
            q = q.filter(CommunityScam.scam_category == category.upper())

        if min_risk_score is not None:
            q = q.filter(CommunityScam.risk_score >= min_risk_score)

        if verified_only:
            q = q.filter(CommunityScam.is_verified_threat == True)

        total = q.count()

        # Sorting
        if sort_by == "highest_risk":
            q = q.order_by(desc(CommunityScam.risk_score), desc(CommunityScam.created_at))
        elif sort_by == "most_confirmed":
            q = q.order_by(desc(CommunityScam.community_confirmations), desc(CommunityScam.created_at))
        else:  # newest
            q = q.order_by(desc(CommunityScam.created_at))

        # Pagination
        offset = (page - 1) * page_size
        rows = q.offset(offset).limit(page_size).all()

        items = []
        for r in rows:
            flags = []
            try:
                flags = json.loads(r.red_flags) if r.red_flags else []
            except Exception:
                flags = [r.red_flags] if r.red_flags else []

            items.append(
                CommunityScamResponse(
                    id=str(r.id),
                    public_id=r.public_id,
                    job_title=r.job_title,
                    impostor_company=r.impostor_company,
                    impostor_domain=r.impostor_domain,
                    contact_platform=r.contact_platform,
                    scam_category=r.scam_category,
                    risk_score=r.risk_score,
                    risk_level=r.risk_level,
                    description_snippet=r.description_snippet,
                    red_flags=flags,
                    evidence_summary=r.evidence_summary,
                    community_confirmations=r.community_confirmations,
                    flag_count=r.flag_count,
                    is_verified_threat=r.is_verified_threat,
                    source_dataset=r.source_dataset,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                )
            )

        total_pages = max(1, (total + page_size - 1) // page_size)

        # Global aggregate stats
        s_count = db.query(func.count(CommunityScam.id)).scalar() or 0
        s_avg_risk = db.query(func.avg(CommunityScam.risk_score)).scalar() or 93.4
        s_sum_conf = db.query(func.sum(CommunityScam.community_confirmations)).scalar() or 283

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "stats": {
                "total_threats": s_count,
                "avg_risk_score": round(float(s_avg_risk), 1),
                "total_community_confirmations": int(s_sum_conf),
            },
            "items": items,
        }

    def get_scam_by_id_or_public_id(
        self, db: Session, identifier: str
    ) -> Optional[CommunityScamResponse]:
        """Fetch single scam record by UUID or Public ID (e.g., SCAM-2026-1001)."""
        self.ensure_seeded_corpus(db)

        is_uuid = False
        try:
            uuid_val = uuid.UUID(identifier)
            is_uuid = True
        except ValueError:
            is_uuid = False

        if is_uuid:
            record = db.query(CommunityScam).filter(CommunityScam.id == uuid_val).first()
        else:
            record = (
                db.query(CommunityScam)
                .filter(
                    or_(
                        CommunityScam.public_id == identifier,
                        CommunityScam.public_id == f"SCAM-{identifier}",
                    )
                )
                .first()
            )

        if not record:
            return None

        flags = []
        try:
            flags = json.loads(record.red_flags) if record.red_flags else []
        except Exception:
            flags = [record.red_flags] if record.red_flags else []

        return CommunityScamResponse(
            id=str(record.id),
            public_id=record.public_id,
            job_title=record.job_title,
            impostor_company=record.impostor_company,
            impostor_domain=record.impostor_domain,
            contact_platform=record.contact_platform,
            scam_category=record.scam_category,
            risk_score=record.risk_score,
            risk_level=record.risk_level,
            description_snippet=record.description_snippet,
            red_flags=flags,
            evidence_summary=record.evidence_summary,
            community_confirmations=record.community_confirmations,
            flag_count=record.flag_count,
            is_verified_threat=record.is_verified_threat,
            source_dataset=record.source_dataset,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def confirm_threat(self, db: Session, identifier: str) -> Optional[int]:
        """Increment community confirmation counter for a threat."""
        self.ensure_seeded_corpus(db)

        is_uuid = False
        try:
            uuid_val = uuid.UUID(identifier)
            is_uuid = True
        except ValueError:
            is_uuid = False

        if is_uuid:
            record = db.query(CommunityScam).filter(CommunityScam.id == uuid_val).first()
        else:
            record = db.query(CommunityScam).filter(CommunityScam.public_id == identifier).first()

        if not record:
            return None

        record.community_confirmations += 1
        db.commit()
        db.refresh(record)
        return record.community_confirmations

    def publish_from_analysis(
        self,
        db: Session,
        analysis_id: str,
        custom_notes: Optional[str] = None,
    ) -> Optional[CommunityScamResponse]:
        """Anonymize and publish an analyzed scan report into the public threat database."""
        try:
            a_uuid = uuid.UUID(analysis_id)
        except ValueError:
            return None

        analysis = db.query(Analysis).filter(Analysis.id == a_uuid).first()
        if not analysis:
            return None

        # Redact raw text to preserve candidate privacy
        sanitized_content = self.redact_pii(analysis.raw_content or "")
        snippet = sanitized_content[:800] + ("..." if len(sanitized_content) > 800 else "")

        # Infer category
        category = "UNVERIFIED_FRAUD"
        lower_content = sanitized_content.lower()
        if "telegram" in lower_content:
            category = "TELEGRAM_INTERVIEW"
        elif "check" in lower_content or "cashier" in lower_content:
            category = "CHECK_FRAUD"
        elif "usdt" in lower_content or "crypto" in lower_content or "task" in lower_content:
            category = "CRYPTO_TASK"
        elif "fee" in lower_content or "deposit" in lower_content or "zelle" in lower_content:
            category = "UPFRONT_FEE"
        elif "ssn" in lower_content or "driver" in lower_content:
            category = "DATA_HARVESTING"

        # Generate unique public threat ID
        unique_suffix = str(uuid.uuid4().hex[:6]).upper()
        public_id = f"SCAM-{datetime.now().year}-{unique_suffix}"

        red_flags_list = []
        if analysis.explanation:
            red_flags_list.append(analysis.explanation)

        scam = CommunityScam(
            public_id=public_id,
            job_title=analysis.job_title or "Unspecified Job Title",
            impostor_company=analysis.company_name or "Unknown Impostor Entity",
            scam_category=category,
            risk_score=analysis.risk_score or 85,
            risk_level=analysis.risk_level or "high",
            description_snippet=snippet,
            red_flags=json.dumps(red_flags_list),
            evidence_summary=custom_notes or "Submitted by verified community scanner.",
            community_confirmations=1,
            is_verified_threat=(analysis.risk_score >= 70),
            source_dataset="COMMUNITY_SCAN",
        )
        db.add(scam)
        db.commit()
        db.refresh(scam)

        return self.get_scam_by_id_or_public_id(db, str(scam.id))


community_scam_service = CommunityScamService()
