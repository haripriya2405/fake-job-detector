# SentinelJob AI — Phase 19: Advanced Transformer ML Subsystem

## Overview
Phase 19 upgrades SentinelJob AI's machine learning core to support state-of-the-art Transformer architectures (`microsoft/deberta-v3-small` / `roberta-base`) exported into dynamic INT8 quantized ONNX Runtime graphs, with token-level explainability spans and a 12-factor model qualification gate.

---

## Key Achievements & Invariants

### 1. Python 3.14 Environment Alignment
- **Python Version**: `Python 3.14.7`
- **Virtual Environment**: `backend/venv314`
- **Zero Regressions**: 168/168 backend unit, integration, golden evaluation, and ML tests passing 100%.

### 2. Model Governance & Production Active Safety Invariant
- **Active Production Model**: `logisticregression-v1.0.0` remains the default active production model.
- **Standby Candidate Models**: `transformer-v1.0.0-candidate` (ONNX) and `model-v2.0.0` (Calibrated SVM) are registered strictly in `[STANDBY]` mode until formally qualified.
- **Rollback Safety**: `ModelPromotionGate.rollback_to_baseline()` guarantees instantaneous, zero-downtime rollback to verified baselines.

### 3. Asymmetric Focal Loss & Adversarial Fine-Tuning
- **`TransformerModelTrainer`** (`backend/app/ml/transformer_trainer.py`):
  - Integrates Asymmetric Focal Loss ($\alpha=0.75, \gamma=2.0$) to heavily penalize false positives and handle severe class imbalance.
  - Augments seed data streams with curated multi-pattern adversarial mutations (`ADVERSARIAL_ROBUSTNESS_CORPUS`).
  - Exports trained PyTorch sequences directly to ONNX format with dynamic INT8 weight quantization.

### 4. 12-Factor Model Promotion Gate
`ModelPromotionGate` (`backend/app/ml/promotion_gate.py`) evaluates candidate models against active baselines across 12 criteria:
1. **Generalization**: Holdout $F_1 \ge 0.90$ & $\text{ROC-AUC} \ge 0.90$.
2. **Threat Recall**: Recall $\ge 0.95$ on known scam vectors.
3. **Controlled False Positive Rate**: $\text{FPR} \le 0.05$.
4. **Statistical Power Adequacy**: Minimum sample size ($N \ge 384$) or documented margin-of-error bounds.
5. **Provenance & Licensing**: 100% verified dataset sources and licenses.
6. **Golden Benchmark Regression Safety**: 0 regressions across all golden test cohorts.
7. **Artifact Integrity**: SHA-256 hash verified against metadata manifest.
8. **Dual Calibration**: Separate reporting of Brier Score and Expected Calibration Error (ECE).
9. **PR-AUC Superiority**: Candidate PR-AUC $\ge$ baseline PR-AUC or $\ge 0.95$.
10. **Multi-pattern Adversarial Robustness**: Detection rate $\ge 90\%$ across 8 adversarial mutation patterns.
11. **Inference Latency Constraint**: CPU p95 inference latency $\le 50\text{ms}$.
12. **Explainability Quality**: Accurate character offsets (`start_char`, `end_char`), context sentences, and feature weights.

### 5. Safe Token & Span Explainability
- Evaluates raw text for deceptive manipulation patterns (fake cashier checks, upfront fees, Telegram diversions, crypto brush task schemes, credential phishing).
- Emits character offsets and sentence context for UI highlight rendering.

---

## Verification & Test Summary
- **Backend Tests**: 168 passed (100%)
- **Golden Evaluation Cases**: 31 passed (100%)
- **Transformer Test Suite**: 23 passed (100%)
- **Frontend Build**: Vite production build succeeded (`dist/index.html` created)
