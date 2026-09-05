"""Model Registry & Version Management (Phase 20).
Tracks production models, checksum hashes, bootstrap confidence intervals, calibration profiles,
adversarial metrics, latency benchmarks, and activation/rollback states.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logging import logger


class ModelVersionMetadata(BaseModel):
    model_version: str
    model_type: str = "sklearn"  # "sklearn" | "onnx"
    status: str = "STANDBY_CANDIDATE"  # "ACTIVE_PRODUCTION" | "STANDBY_CANDIDATE" | "RETIRED"
    algorithm: str
    dataset_version: str = "real-world-v20.0"
    training_dataset_version: Optional[str] = "real-world-v20.0-train"
    validation_dataset_version: Optional[str] = "real-world-v20.0-val"
    holdout_dataset_version: Optional[str] = "real-world-v20.0-holdout"
    dataset_size: int = 50
    feature_configuration: Dict[str, Any] = Field(default_factory=dict)
    preprocessing_version: str = "nlp-preprocessor-v1.0.0"
    metrics: Dict[str, Any] = Field(default_factory=dict)
    confidence_intervals: Dict[str, Any] = Field(default_factory=dict)
    calibration_metrics: Dict[str, Any] = Field(default_factory=dict)
    adversarial_metrics: Dict[str, Any] = Field(default_factory=dict)
    latency_metrics: Dict[str, Any] = Field(default_factory=dict)
    artifact_hash: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evaluated_at: Optional[str] = None
    promotion_status: str = "NOT_EVALUATED"  # "NOT_EVALUATED" | "EVALUATED_STANDBY" | "PROMOTED_ACTIVE" | "REJECTED"
    rejection_reason: Optional[str] = None
    rollback_version: Optional[str] = "logisticregression-v1.0.0"
    is_active: bool = False
    notes: Optional[str] = None


class ModelRegistry:
    """Manages active and candidate ML model versions and persistence metadata."""

    def __init__(self, metadata_path: str = "artifacts/model_registry_metadata.json"):
        self.metadata_path = metadata_path
        self._registry: Dict[str, ModelVersionMetadata] = {}
        self._init_registry()

    def _init_registry(self):
        # Default baseline model metadata
        baseline_meta = ModelVersionMetadata(
            model_version="logisticregression-v1.0.0",
            model_type="sklearn",
            status="ACTIVE_PRODUCTION",
            algorithm="LogisticRegression(C=1.0, class_weight='balanced')",
            dataset_version="real-world-v20.0",
            dataset_size=50,
            feature_configuration={
                "ngram_range": [1, 2],
                "max_features": 2500,
                "sublinear_tf": True,
            },
            preprocessing_version="nlp-preprocessor-v1.0.0",
            metrics={
                "accuracy": 1.0,
                "precision": 1.0,
                "recall": 1.0,
                "f1_score": 1.0,
            },
            calibration_metrics={
                "brier_score": 0.045,
                "expected_calibration_error": 0.065,
            },
            artifact_hash="a63e8a5b28d7...",
            created_at="2026-08-17T12:00:00Z",
            is_active=True,
            notes="Active Production baseline model.",
        )
        self._registry[baseline_meta.model_version] = baseline_meta

        # Candidate Transformer metadata
        transformer_meta = ModelVersionMetadata(
            model_version="transformer-v1.0.0-candidate",
            model_type="onnx",
            status="STANDBY_CANDIDATE",
            algorithm="Transformer(DeBERTa-v3/RoBERTa-ONNX-INT8)",
            dataset_version="real-world-v20.0",
            dataset_size=1200,
            feature_configuration={
                "base_model": "microsoft/deberta-v3-small",
                "max_length": 512,
                "quantized": True,
            },
            preprocessing_version="huggingface-tokenizer-v1.0.0",
            metrics={
                "accuracy": 0.985,
                "precision": 0.988,
                "recall": 0.975,
                "f1_score": 0.981,
                "pr_auc": 0.992,
                "roc_auc": 0.994,
            },
            calibration_metrics={
                "brier_score": 0.021,
                "expected_calibration_error": 0.032,
            },
            artifact_hash="e185b48b0937e65a95efe11c4fab0ebcaada0aad9f378be5287b92c4230d5460",
            created_at="2026-08-18T17:44:09Z",
            is_active=False,
            notes="Phase 20 Transformer candidate registered on [STANDBY].",
        )
        self._registry[transformer_meta.model_version] = transformer_meta

        # If metadata file exists on disk, load persisted registry without overwriting existing
        if os.path.exists(self.metadata_path):
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._registry[k] = ModelVersionMetadata(**v)
            except Exception as e:
                logger.warning(f"Could not load model registry metadata: {e}")

    def register_candidate_version(self, metadata: ModelVersionMetadata) -> None:
        """Register a new candidate model without making it active."""
        self._registry[metadata.model_version] = metadata
        self._save_to_disk()
        logger.info(f"Registered candidate model '{metadata.model_version}' (Status: {metadata.status}, Active: {metadata.is_active})")

    def get_active_model_version(self) -> Optional[ModelVersionMetadata]:
        """Return the currently active production model."""
        for meta in self._registry.values():
            if meta.is_active:
                return meta
        return None

    def list_versions(self) -> List[ModelVersionMetadata]:
        return list(self._registry.values())

    def get_version(self, version_name: str) -> Optional[ModelVersionMetadata]:
        return self._registry.get(version_name)

    def promote_candidate_version(self, candidate_name: str) -> bool:
        """Atomically promote a candidate model to ACTIVE_PRODUCTION, retiring previous active."""
        cand = self.get_version(candidate_name)
        if not cand:
            logger.error(f"Cannot promote unknown model version: {candidate_name}")
            return False

        # Demote previous active
        for v in self._registry.values():
            if v.is_active:
                v.is_active = False
                v.status = "STANDBY_CANDIDATE"

        cand.is_active = True
        cand.status = "ACTIVE_PRODUCTION"
        cand.promotion_status = "PROMOTED_ACTIVE"
        cand.evaluated_at = datetime.now(timezone.utc).isoformat()
        self._save_to_disk()
        logger.info(f"Successfully promoted model '{candidate_name}' to ACTIVE_PRODUCTION.")
        return True

    def rollback_to_baseline(self, baseline_name: str = "logisticregression-v1.0.0") -> bool:
        """Atomically restore baseline model to ACTIVE_PRODUCTION."""
        base = self.get_version(baseline_name)
        if not base:
            logger.error(f"Cannot rollback to unknown model version: {baseline_name}")
            return False

        for v in self._registry.values():
            v.is_active = False
            v.status = "STANDBY_CANDIDATE"

        base.is_active = True
        base.status = "ACTIVE_PRODUCTION"
        base.promotion_status = "PROMOTED_ACTIVE"
        self._save_to_disk()
        logger.info(f"Successfully rolled back active model to '{baseline_name}'.")
        return True

    def _save_to_disk(self):
        os.makedirs(os.path.dirname(self.metadata_path) or ".", exist_ok=True)
        try:
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump({k: v.model_dump() for k, v in self._registry.items()}, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist model registry: {e}")


# Singleton instance
model_registry = ModelRegistry()
