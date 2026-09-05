import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, GUID, TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis


class AnalysisIndicator(Base, TimestampMixin):
    __tablename__ = "analysis_indicators"

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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        default="medium",
        nullable=False,
    )  # "low", "medium", "high", "critical"
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    recommendation: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    risk_weight: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )  # e.g. "+35 pts"

    # Relationship
    analysis: Mapped["Analysis"] = relationship(
        "Analysis",
        back_populates="indicators",
    )
