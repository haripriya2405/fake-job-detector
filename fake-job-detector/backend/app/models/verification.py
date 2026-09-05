import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis


class VerificationResult(Base, TimestampMixin):
    __tablename__ = "verification_results"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    domain_checked: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="unverified",
        nullable=False,
    )  # "verified", "warning", "unverified", "inconsistent", "partially_verified"
    domain_age_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    mx_record_valid: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    linkedin_match: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    details_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="verification_results",
    )
