import uuid
from typing import Optional
from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, GUID, TimestampMixin


class CommunityScam(Base, TimestampMixin):
    __tablename__ = "community_scams"
    __table_args__ = (
        Index("idx_scams_cat_confirm", "scam_category", "community_confirmations"),
        Index("idx_scams_risk_created", "risk_score", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    public_id: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
        nullable=False,
    )
    job_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    impostor_company: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    impostor_domain: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    contact_platform: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    scam_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )  # CHECK_FRAUD, TELEGRAM_INTERVIEW, UPFRONT_FEE, CRYPTO_TASK, DATA_HARVESTING, PHISHING
    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=85,
        nullable=False,
        index=True,
    )
    risk_level: Mapped[str] = mapped_column(
        String(50),
        default="high",
        nullable=False,
        index=True,
    )
    description_snippet: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    red_flags: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )  # JSON-encoded list
    evidence_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    community_confirmations: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        index=True,
    )
    flag_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    is_verified_threat: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    source_dataset: Mapped[str] = mapped_column(
        String(100),
        default="COMMUNITY",
        nullable=False,
        index=True,
    )
