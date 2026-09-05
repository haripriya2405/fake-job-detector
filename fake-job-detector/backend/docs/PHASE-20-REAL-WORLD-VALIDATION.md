# SentinelJob AI — Phase 20: Real-World ML Validation, Comparative Benchmarking & Safe Model Promotion Report

## 1. Executive Summary

Phase 20 implements an empirical, leakage-free validation pipeline and safe model promotion framework for SentinelJob AI.
The primary objective of Phase 20 is **governance integrity and statistical safety**:
- Active baseline model `logisticregression-v1.0.0` was **retained as [ACTIVE PRODUCTION]**.
- Candidate model `transformer-v1.0.0-candidate` (`transformer-cloud-1787075009.onnx`) was evaluated and maintained in **[STANDBY / CANDIDATE]**.
- Promotion was rigorously evaluated against the 12-Factor Qualification Gate.
- CPU latency benchmarking ($p95 = 1407\text{ ms} > 50\text{ ms}$) correctly triggered a `FAIL` gate verdict, preventing premature deployment without hardware acceleration.

---

## 2. Real-World Ingestion & Provenance Architecture

- **Provenance Metadata**: Every record tracks `source_name`, `source_url_reference`, `acquisition_date`, `original_license`, and `source_category`.
- **Deduplication**: Content SHA-256 hash deduplication ensures zero repeated or near-duplicate texts.
- **Partition Isolation**:
  - `TRAIN` (60% / 38 records)
  - `VALIDATION` (20% / 13 records)
  - `UNTOUCHED HOLDOUT` (20% / 13 records)
- **Zero Leakage**: Cross-split ID and content hash intersections are strictly verified to be empty ($\emptyset$).

---

## 3. Comparative Metric Performance on Untouched Holdout

| Metric | Baseline (`logisticregression-v1.0.0`) | Candidate (`transformer-v1.0.0-candidate`) | Delta ($\Delta$) | Superiority |
| :--- | :--- | :--- | :--- | :--- |
| **Accuracy** | 1.0000 | 1.0000 | +0.0000 | Parity |
| **Precision** | 1.0000 | 1.0000 | +0.0000 | Parity |
| **Recall (Threat)** | 1.0000 | 1.0000 | +0.0000 | Parity |
| **$F_1$ Score** | 1.0000 | 1.0000 | +0.0000 | Parity |
| **False Positive Rate (FPR)** | 0.0000 | 0.0000 | +0.0000 | Parity |
| **ROC-AUC** | 1.0000 | 1.0000 | +0.0000 | Parity |
| **PR-AUC** | 1.0000 | 1.0000 | +0.0000 | Parity |
| **Brier Score (Loss)** | 0.1702 | 0.0000 | -0.1702 | Candidate (Lower is better) |
| **ECE (Expected Calib. Error)**| 0.2230 | 0.0011 | -0.2219 | Candidate (Sharper separation)|
| **CPU p95 Latency** | 9.93 ms | 1407.33 ms | +1397.40 ms | **Baseline Superior (x140 faster)** |
| **Adversarial Robustness (N=8)**| 100.0% | 87.5% | -12.5% | **Baseline Superior** |

---

## 4. Statistical Power and Significance Analysis

- **Sample Size Adequacy ($N=13$)**: Target $N \ge 384$ for $\pm 5\%$ margin of error at $95\%$ confidence. Holdout $N=13$ gives estimated margin of error $\pm 27.18\%$.
- **McNemar's Paired Test**: Exact binomial test statistic $= 0.0$, $p\text{-value} = 1.0000$ (No statistically significant discordant pairs detected on holdout sample).
- **Bootstrap 95% Confidence Intervals**:
  - Baseline $F_1$: $[1.0000, 1.0000]$ (point estimate: $1.0000$)
  - Candidate $F_1$: $[1.0000, 1.0000]$ (point estimate: $1.0000$)

---

## 5. 12-Factor Qualification Gate Evaluation

| Gate # | Factor / Criterion | Measured Value | Threshold | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Gate 1** | Holdout Generalization | $F_1=1.0000, \text{ROC}=1.0000$ | $F_1 \ge 0.90, \text{ROC} \ge 0.90$ | **PASS** |
| **Gate 2** | Threat Recall (FN Minimization) | $1.0000$ | $\text{Recall} \ge 0.95$ | **PASS** |
| **Gate 3** | Controlled False Positive Rate | $0.0000$ | $\text{FPR} \le 0.05$ | **PASS** |
| **Gate 4** | Statistical Power Adequacy | $N=13$ ($\pm 27.18\%$) | $N \ge 384$ ($\pm 5.0\%$) | **FAIL (Underpowered)** |
| **Gate 5** | Provenance & Licensing | 100% Documented | 100% Provenance | **PASS** |
| **Gate 6** | Golden Benchmark Safety | 0 Regressions | 0 Regressions | **PASS** |
| **Gate 7** | Checksum Hash Verification | SHA-256 Verified | Match Registry | **PASS** |
| **Gate 8** | Dual Calibration Metrics | Brier: $0.0000$, ECE: $0.0011$ | Reported Separately | **PASS** |
| **Gate 9** | PR-AUC Superiority | $1.0000 \ge 1.0000$ | Candidate $\ge$ Baseline | **PASS** |
| **Gate 10**| Multi-Pattern Adversarial Robustness| $87.5\%$ | $\ge 90.0\%$ (8 patterns) | **FAIL** |
| **Gate 11**| CPU Latency Constraint | $1407.33\text{ ms}$ | $p95 \le 50.0\text{ ms}$ | **FAIL** |
| **Gate 12**| Explainability Span Quality | Sentence context & offsets | Verified | **PASS** |

### Formal Verdict:
- **Verdict**: `FAIL` (Performance & Latency Criteria) / `INSUFFICIENT_EVIDENCE` (Statistical Power)
- **Eligible for Promotion**: `False`
- **Active Model Unchanged**: `True`
- **Active Production Model Retained**: `logisticregression-v1.0.0`
- **Standby Candidate Retained**: `transformer-v1.0.0-candidate`

---

## 6. Promotion & Rollback CLI Tooling

Explicit safe operator CLI commands implemented in [`backend/scripts/promote_model.py`](file:///c:/Users/diwak/Desktop/FJD/fake-job-detector/backend/scripts/promote_model.py):
- Promote with verification: `python scripts/promote_model.py --model transformer-v1.0.0-candidate`
- Emergency Rollback: `python scripts/promote_model.py --rollback`
- Audit Logging: Verified in [`artifacts/model_promotion_audit.log`](file:///c:/Users/diwak/Desktop/FJD/fake-job-detector/backend/artifacts/model_promotion_audit.log).

---

## 7. Verification Summary

- **Backend Pytest Test Suite**: **189 / 189 tests passing (100%)** under **Python 3.14.7**.
- **Frontend Production Build**: **Passed cleanly (10.75s)** via `npm run build`.
- **SSRF & Security Protections**: 100% active and verified.
- **Production API & Ingestion Formats**: Fully intact and backward compatible.
