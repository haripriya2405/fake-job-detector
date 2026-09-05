import uuid
from typing import Optional
from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, GUID, TimestampMixin


class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )  # e.g. "tfidf_logistic_regression"
    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )  # e.g. "v1.0.0"
    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )  # "LogisticRegression"
    training_dataset: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )  # "EMSCAD_benchmark_18k"
    accuracy: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    f1_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    artifact_path: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
