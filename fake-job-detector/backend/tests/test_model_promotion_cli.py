"""Test Suite for Explicit Model Promotion & Rollback CLI Tool (Phase 20)."""

import os
import pytest
from app.ml.registry import ModelRegistry, ModelVersionMetadata, model_registry
from scripts.promote_model import AUDIT_LOG_PATH, execute_promotion, execute_rollback


def test_promotion_cli_unknown_model_returns_false():
    """Verify promotion fails safely when given an unknown model identifier."""
    result = execute_promotion("non-existent-model-xyz", auto_confirm=True)
    assert result is False


def test_promotion_and_rollback_lifecycle(tmp_path):
    """Verify full promotion to active and rollback restores baseline."""
    # Ensure baseline is currently active
    active = model_registry.get_active_model_version()
    assert active is not None

    # Rollback explicitly to baseline
    rb_success = execute_rollback(baseline_name="logisticregression-v1.0.0", auto_confirm=True)
    assert rb_success is True

    active_now = model_registry.get_active_model_version()
    assert active_now.model_version == "logisticregression-v1.0.0"

    # Verify audit log was created
    if os.path.exists(AUDIT_LOG_PATH):
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        assert "ACTION=ROLLBACK" in content
