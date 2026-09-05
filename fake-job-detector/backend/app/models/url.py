import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis


class UrlAnalysis(Base, TimestampMixin):
    __tablename__ = "url_analyses"

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
    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )
    domain: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    domain_age_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    mx_record_valid: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
    )
    is_suspicious: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    flags_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationship
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="url_analyses",
    )
