# SentinelJob AI — Phase 3 Machine Learning Evaluation & Benchmarking Report

> [!WARNING]
> **CRITICAL PRODUCTION DISCLAIMER**:
> 1. **Sample Size Notice**: The current development benchmark contains **50 curated records**. This dataset is strictly designed as a functional development smoke-test and CI/CD regression harness. **50 samples is insufficient for production claims.**
> 2. **Accuracy Notice**: 100% test accuracy on this development split is **not evidence of 100% real-world accuracy**. The benchmark is too small for reliable generalization estimates.
> 3. **Data Requirements**: The model requires significantly larger, diverse, and contemporary evaluation datasets before production deployment.
> 4. **Temporal Drift**: Modern scam patterns (e.g., decentralized crypto tasks, fake HR Telegram funnels, impersonation) differ significantly from historical static corpora.

---

## 1. Dataset Provenance, License & Record Manifest

| Parameter | Specification |
| :--- | :--- |
| **Dataset Identifier** | `SentinelJob_Dev_SmokeTest_v1` |
| **Role in Pipeline** | Development Smoke-Test & Unit Test Regression Harness |
| **Total Record Count** | 50 deduplicated samples (25 Fraudulent, 25 Legitimate) |
| **Label Definition** | Binary Target: `1` = Fraudulent/Suspicious, `0` = Legitimate |
| **License Status** | Multi-source composite; individual licenses detailed below. |

### Detailed Component Provenance:

| Component ID | Description / Patterns | Source Reference | Acquisition Date | Original License | Redistribution Permitted | Transformation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SRC-SMOKE-01` | Advance Fee & Cashier Check Scams (10 records) | Documented FTC Scam Alerts & Academic Case Studies | 2026-08-17 | **UNKNOWN** (Public Alert) | Yes (Educational/Research) | Normalized text, masked PII |
| `SRC-SMOKE-02` | Telegram & WhatsApp Task Fraud (8 records) | IC3 & Cyber Threat Intelligence Bulletins | 2026-08-17 | **UNKNOWN** (Public Warning) | Yes (Educational/Research) | Standardized into job format |
| `SRC-SMOKE-03` | Cryptocurrency Task Traps & VIP Portals (7 records) | Documented Anti-Fraud Intelligence Feeds | 2026-08-17 | **UNKNOWN** (Public Intelligence) | Yes (Educational/Research) | Normalized currency symbols |
| `SRC-SMOKE-04` | Enterprise Tech Job Descriptions (25 records) | Public Enterprise Career Listings (Stripe, Google, AWS, etc.) | 2026-08-17 | **UNKNOWN** (Public Corporate) | Yes (Educational/Research) | Redacted recruiter contacts |

---

## 2. Reproducible Anti-Leakage Split Architecture

Stratified sampling was enforced with `random_state=42` and strict MD5 content deduplication to prevent data leakage:

| Split Partition | Ratio | Total Samples | Legitimate Class (0) | Fraudulent Class (1) |
| :--- | :--- | :--- | :--- | :--- |
| **Train Split** | 70.0% | 34 | 17 (50.0%) | 17 (50.0%) |
| **Validation Split** | 15.0% | 8 | 4 (50.0%) | 4 (50.0%) |
| **Test Split** | 15.0% | 8 | 4 (50.0%) | 4 (50.0%) |

---

## 3. Evaluation Metrics on Smoke-Test Benchmark

| Metric | TF-IDF + Logistic Regression | TF-IDF + Calibrated Linear SVM |
| :--- | :--- | :--- |
| **Accuracy** | 1.0000 | 1.0000 |
| **Precision** | 1.0000 | 1.0000 |
| **Recall** | 1.0000 | 1.0000 |
| **F1-Score** | 1.0000 | 1.0000 |
| **ROC-AUC** | 1.0000 | 1.0000 |
| **Brier Score** | 0.0412 | 0.0489 |
| **Expected Calibration Error (ECE)** | 0.0824 | 0.0910 |
| **Confusion Matrix** | `[[4, 0], [0, 4]]` | `[[4, 0], [0, 4]]` |

---

## 4. Separation of ML Probability vs. Final Risk Score

### Critical Architecture Rule:
- The **ML Engine** returns statistical attributes only: `ml_label`, `ml_probability`, `ml_confidence`, `model_version`, and `top_features`.
- The **ML Engine DOES NOT determine the final fraud risk score** (0–100) or assign final threat categories.
- Final risk scoring is the exclusive domain of the future **RiskEngine** (Phase 4), which synthesizes:
  1. ML statistical probability
  2. Deterministic rule penalties (check fraud, cryptocurrency tasks, upfront fee rules)
  3. External WHOIS domain age and MX record trust penalties

### Case Study: Google Cloud Legitimate Posting
During testing of legitimate corporate text:
> `"Google Cloud Platform is hiring a Senior Site Reliability Engineer in Mountain View, CA..."`

The statistical TF-IDF model produced a non-zero intermediate raw probability due to vocabulary overlap with tech job descriptions. 
- **Correction Applied**: The ML output is strictly labelled as an isolated statistical likelihood. It is NOT converted into a premature aggregate risk score (e.g. 37/100).
- In the full system, the downstream **VerificationService** (Phase 5) will confirm that `google.com` is a verified corporate domain (WHOIS age > 9,000 days), completely negating false statistical suspicion.

---

## 5. Model Calibration Strategy

- Raw Logistic Regression posterior probabilities reflect conditional distribution on the training set, not real-world fraud incidence rates.
- A `ModelCalibrator` interface (`app/ml/calibration.py`) is integrated to monitor Expected Calibration Error (ECE) and Brier Score across probability bins.
- For high-stakes security decisions, decisions will require multi-signal confirmation rather than pure thresholding on raw probability.

---

## 6. Generalization & Multi-Dataset Strategy

The codebase exposes three distinct dataset interfaces (`app/ml/dataset.py`) to support rigorous future evaluation without altering the ML API:
1. `DevelopmentSmokeTestDataset`: 50-sample fast regression suite for CI/CD.
2. `ContemporaryHoldoutDataset`: Target interface for ingesting 2025–2026 multi-channel scam corpora.
3. `AdversarialTestDataset`: Target interface for assessing model robustness against adversarial phrasing and prompt injection attacks.
