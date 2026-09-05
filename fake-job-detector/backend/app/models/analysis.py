import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.indicator import AnalysisIndicator
    from app.models.url import UrlAnalysis
    from app.models.verification import VerificationResult


class Analysis(Base, TimestampMixin):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    job_title: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    company_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        default="text",
        nullable=False,
        index=True,
    )  # "text", "pdf", "image", "url"
    raw_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    risk_score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
    )  # 0 - 100
    risk_level: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
        index=True,
    )  # "pending", "low", "medium", "high", "critical"
    ml_confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    rule_penalty_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    domain_trust_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    explanation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    analysis_engine: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )

    # Multi-Modal Metadata Fields (Phase 8)
    original_filename: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    page_count: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    extraction_method: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    extraction_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="analyses",
    )
    indicators: Mapped[List["AnalysisIndicator"]] = relationship(
        "AnalysisIndicator",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    url_analyses: Mapped[List["UrlAnalysis"]] = relationship(
        "UrlAnalysis",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
    verification_results: Mapped[List["VerificationResult"]] = relationship(
        "VerificationResult",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )
