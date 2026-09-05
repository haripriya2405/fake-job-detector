"""Test Suite for Transformer Fine-Tuning Components and Focal Loss Engine."""

import pandas as pd
import pytest
import torch
from app.ml.transformer_trainer import FocalLoss, TransformerModelTrainer
from app.ml.calibration import ModelCalibrator


def test_focal_loss_numerical_properties():
    """Verify Focal Loss calculates finite, positive loss with class weighting."""
    criterion = FocalLoss(alpha=0.75, gamma=2.0)
    logits = torch.tensor([[2.0, -1.0], [-1.5, 3.0]], dtype=torch.float32)
    targets = torch.tensor([0, 1], dtype=torch.long)

    loss = criterion(logits, targets)
    assert isinstance(loss, torch.Tensor)
    assert not torch.isnan(loss)
    assert not torch.isinf(loss)
    assert float(loss) > 0.0


def test_focal_loss_heavier_penalty_for_misclassification():
    """Verify Focal Loss penalizes confident wrong predictions much harder than correct predictions."""
    criterion = FocalLoss(alpha=0.5, gamma=2.0)

    # Confident correct prediction
    correct_logits = torch.tensor([[10.0, -10.0]], dtype=torch.float32)
    correct_targets = torch.tensor([0], dtype=torch.long)
    correct_loss = float(criterion(correct_logits, correct_targets))

    # Confident wrong prediction
    wrong_logits = torch.tensor([[-10.0, 10.0]], dtype=torch.float32)
    wrong_targets = torch.tensor([0], dtype=torch.long)
    wrong_loss = float(criterion(wrong_logits, wrong_targets))

    assert wrong_loss > correct_loss
    assert wrong_loss / (correct_loss + 1e-8) > 100.0


def test_transformer_trainer_adversarial_augmentation():
    """Verify trainer injects adversarial test cases into seed training stream."""
    trainer = TransformerModelTrainer(base_model_name="microsoft/deberta-v3-small")
    initial_df = pd.DataFrame([
        {"raw_text": "Clean legitimate job 1", "label": 0},
        {"raw_text": "Clean legitimate job 2", "label": 0},
    ])
    augmented = trainer.augment_with_adversarial_corpus(initial_df)

    assert len(augmented) > len(initial_df)
    assert any(augmented["dataset_source"] == "adversarial_robustness_corpus")
    assert all(col in augmented.columns for col in ["raw_text", "label"])


def test_model_calibrator_with_transformer_probabilities():
    """Verify ModelCalibrator evaluates Brier score and ECE on uncalibrated model probabilities."""
    calibrator = ModelCalibrator()
    uncalibrated_probs = [0.05, 0.12, 0.88, 0.95, 0.40, 0.60]
    true_labels = [0, 0, 1, 1, 0, 1]

    metrics = calibrator.evaluate_calibration(true_labels, uncalibrated_probs)
    assert "brier_score" in metrics
    assert "expected_calibration_error" in metrics
    assert 0.0 <= metrics["brier_score"] <= 1.0
    assert 0.0 <= metrics["expected_calibration_error"] <= 1.0
