import uuid
from typing import Optional
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, GUID, TimestampMixin


class RuleVersion(Base, TimestampMixin):
    __tablename__ = "rule_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )  # e.g. "core_fraud_rules"
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )  # e.g. "v1.2.0"
    rule_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    rules_definition_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
