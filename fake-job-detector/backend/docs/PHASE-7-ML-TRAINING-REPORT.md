# SentinelJob AI — Phase 7, 7B & 7C Production ML Dataset, Statistical Strengthening & Promotion Gate Report

---

> [!CAUTION]
> **STATISTICAL ADEQUACY & GENERALIZATION LIMITATION STATEMENT**:
> *“The current dataset (63 clean records) and contemporary holdout ($N=11$) are **UNDERPOWERED (Sample Size Limited)** with an estimated margin of error of $\pm 29.55\%$. Small holdout samples and high point-estimate scores are **not decisive** indicators of production performance across real-world adversarial fraud distributions. **`model-v2.0.0` has NOT been promoted and remains strictly on `[STANDBY]` in the model version registry.** The production runtime retains **`logisticregression-v1.0.0` as `[ACTIVE PRODUCTION]`**.”*

---

## 1. Dataset Ingestion, Scope & Provenance

The production ingestion pipeline (`app/ml/production_dataset.py`) aggregates verified postings across 11 vertical categories with documented provenance:

| Source Identifier | Sector / Threat Category | Primary Domain / Reference | Ingested Count | License Status |
| :--- | :--- | :--- | :--- | :--- |
| **`tech_enterprise`** | Enterprise Software & Cloud | Stripe, Vercel, AWS, Google Cloud, Cloudflare, Datadog, Snowflake, Netflix, Apple, Meta, Atlassian | 12 | `UNKNOWN / Public Corporate Posting` |
| **`academic_research`** | Higher Ed & University | Stanford AI Lab, Broad Institute of MIT, Cambridge, Oxford, CMU Robotics | 6 | `UNKNOWN / University Academic Notice` |
| **`healthcare`** | Clinical & Hospital Services | Mayo Clinic, Cleveland Clinic, Johns Hopkins, Kaiser Permanente, NHS England | 5 | `UNKNOWN / Hospital Healthcare Notice` |
| **`public_sector`** | Government & Defense | CISA, CDC, NASA Goddard, NIST, UK Civil Service | 5 | `UNKNOWN / US Government Public Domain` |
| **`borderline_startup`** | Startups & Early-Stage SaaS | Studio Bright, PixelCraft Labs, CognitiveForge AI, Kredivo, 37signals, PostHog | 7 | `UNKNOWN / Public Startup Listing` |
| **`advance_fee`** | Advance-Fee Job Fraud | FTC Consumer Alerts & IC3 Scam Bulletins (Registration, Uniform, Training Fees) | 7 | `UNKNOWN / Informational Advisory` |
| **`cashier_check`** | Check Overpayment & Mule Traps | USPS Postal Inspection & IC3 Check Fraud Bulletins (Mystery Shopper, Procurement) | 5 | `UNKNOWN / Informational Advisory` |
| **`crypto_task`** | Deposit-to-Withdraw Task Scams | FBI Cyber Division Task Scam Bulletins (USDT Tasks, Video Booster, Rating Tasks) | 5 | `UNKNOWN / Informational Advisory` |
| **`impersonation`** | Lookalike Portals & Webmail | Reported Threat Intelligence Feeds (Lookalike Domains, Typosquatted URLs) | 5 | `UNKNOWN / Threat Log` |
| **`pii_phishing`** | Credential & OTP Theft | FTC Credential Theft Bulletins (Netbanking Passwords, SSN Harvesting) | 3 | `UNKNOWN / Informational Advisory` |
| **`adversarial_evasion`** | Obfuscated & Paraphrased Evasions | Contemporary Holdout Threat Logs (Spaced Keywords, Disguised Deposits) | 4 | `UNKNOWN / Adversarial Research` |

---

## 2. Ingestion Quality & Deduplication

- **Total Ingested Records**: `64 raw records`
- **Deduplication Filtering**:
  - Exact duplicates dropped: `0`
  - Normalized duplicates dropped: `0`
  - Near-duplicates dropped ($\text{Jaccard} \ge 0.88$ overlap): `1 record`
- **Clean Accepted Records**: **`63 records`** ($35$ Legitimate, $28$ Fraudulent).
- **Documented Sources**: `15 distinct source entities` with zero unsupported licensing claims.

---

## 3. Leakage-Free Temporal / Stratified Partitioning

- **Historical Training Split ($70\%$)**: `43 records` ($24$ Legit, $19$ Fraud)
- **Validation Split ($15\%$)**: `9 records` ($5$ Legit, $4$ Fraud)
- **Contemporary Holdout Split ($15\%$)**: **`11 records`** ($6$ Legit, $5$ Fraud)
- **Zero Leakage**: Strict ID and hash validation confirms $\text{Train} \cap \text{Val} \cap \text{Holdout} = \emptyset$.

---

## 4. 5-Fold Stratified Cross-Validation on Development Data

5-Fold Stratified Cross-Validation executed on the historical training set ($N=43$):

| Evaluation Metric | 5-Fold CV Mean | Standard Deviation ($\sigma$) |
| :--- | :--- | :--- |
| **Accuracy** | `0.9306` | $\pm 0.0569$ |
| **Precision** | `1.0000` | $\pm 0.0000$ |
| **Recall** | `0.8333` | $\pm 0.1394$ |
| **F1-Score** | `0.9029` | $\pm 0.0820$ |
| **ROC-AUC** | `1.0000` | $\pm 0.0000$ |

---

## 5. Candidate Model Benchmark & Exact Calibration Reporting

```
Model Performance Benchmark on Contemporary Holdout (N=11):
-------------------------------------------------------------------------------------------------
Model Candidate                            | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Brier Loss | ECE Error
-------------------------------------------------------------------------------------------------
logisticregression-v1.0.0 (Baseline)       | 0.8182   | 0.8000    | 0.8000 | 0.8000   | 0.9333  | 0.1917     | 0.1697
logisticregression-v2.0.0-candidate        | 0.8182   | 0.8000    | 0.8000 | 0.8000   | 0.9333  | 0.1862     | 0.1840
linearsvm-v2.0.0-candidate (Platt Scaled)  | 0.8182   | 0.8000    | 0.8000 | 0.8000   | 0.9333  | 0.1409     | 0.1681
-------------------------------------------------------------------------------------------------
```

### Exact Calibration Interpretation:
- **Logistic Regression v1 (Baseline)**: $\text{Brier} = 0.1917$, $\text{ECE} = 0.1697$
- **Logistic Regression v2 (Candidate)**: $\text{Brier} = 0.1862$, $\text{ECE} = 0.1840$
- **Linear SVM + Platt Scaling (Candidate)**: $\text{Brier} = 0.1409$, $\text{ECE} = 0.1681$
- **Critical Assessment**: While Platt-scaled Linear SVM demonstrates lower Brier score due to sharper probability separation, **all three models exhibit an ECE between 0.1681 and 0.1840**. These error gaps indicate that predicted probabilities remain imperfectly calibrated on small holdouts. Model superiority is **never declared on Brier score alone**.

---

## 6. Non-Parametric Bootstrap Confidence Intervals ($B=1000$, $95\%$ CI)

Bootstrap resampling ($B=1000$) on the untouched contemporary holdout:

| Metric | Point Estimate | $95\%$ Bootstrap Confidence Interval | Interval Width |
| :--- | :--- | :--- | :--- |
| **Accuracy** | `0.8182` | `[0.5455, 1.0000]` | `0.4545` |
| **Precision** | `0.8000` | `[0.3975, 1.0000]` | `0.6025` |
| **Recall** | `0.8000` | `[0.3333, 1.0000]` | `0.6667` |
| **F1-Score** | `0.8000` | `[0.4000, 1.0000]` | `0.6000` |
| **False Positive Rate** | `0.1667` | `[0.0000, 0.5000]` | `0.5000` |
| **ROC-AUC** | `0.9333` | `[0.7000, 1.0000]` | `0.3000` |
| **PR-AUC** | `0.9267` | `[0.6667, 1.0000]` | `0.3333` |

*Note: The wide confidence intervals (e.g. Recall $95\%$ CI $[0.3333, 1.0000]$) quantitatively prove that the sample size is underpowered for production claims.*

---

## 7. Cost-Sensitive Threshold Grid Search (Validation Data Only)

Decision thresholds evaluated on the **Validation Split ($N=9$)**:

$$\text{Decision Loss} = 10.0 \times \text{False Negatives} + 1.0 \times \text{False Positives}$$

| Threshold ($\tau$) | Precision | Recall | F1-Score | Decision Loss | Matrix (TP, FP, FN, TN) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$\tau = 0.30$** | `1.0000` | `1.0000` | `1.0000` | **`0.0`** | $\text{TP}=4, \text{FP}=0, \text{FN}=0, \text{TN}=5$ |
| **$\tau = 0.40$** | `1.0000` | `1.0000` | `1.0000` | **`0.0`** | $\text{TP}=4, \text{FP}=0, \text{FN}=0, \text{TN}=5$ |
| **$\tau = 0.50$** | `1.0000` | `1.0000` | `1.0000` | **`0.0`** | $\text{TP}=4, \text{FP}=0, \text{FN}=0, \text{TN}=5$ |
| **$\tau = 0.60$** | `1.0000` | `1.0000` | `1.0000` | **`0.0`** | $\text{TP}=4, \text{FP}=0, \text{FN}=0, \text{TN}=5$ |
| **$\tau = 0.70$** | `1.0000` | `1.0000` | `1.0000` | **`0.0`** | $\text{TP}=4, \text{FP}=0, \text{FN}=0, \text{TN}=5$ |

- **Optimal Validation Threshold**: $\tau^* = 0.30$ (minimizes missed scams).
- **Single-Pass Untouched Holdout Evaluation at $\tau^* = 0.30$**:
  - Holdout Precision: `0.8000`
  - Holdout Recall: `0.8000`
  - Holdout F1-Score: `0.8000`
  - Holdout Decision Loss: `11.0` ($\text{TP}=4, \text{TN}=5, \text{FP}=1, \text{FN}=1$)

---

## 8. Statistical Power Adequacy & Promotion Gate Verdict

| Factor / Gate | Requirement | Candidate Result | Gate Status |
| :--- | :--- | :--- | :--- |
| **Gate 1: Generalization** | $\text{F1} \ge 0.90$, $\text{ROC-AUC} \ge 0.90$ on holdout | $\text{F1} = 0.8000$, $\text{ROC-AUC} = 0.9333$ | **`[FAIL]`** |
| **Gate 2: Low False Negatives** | $\text{Recall} \ge 0.95$ on fraud threats | $\text{Recall} = 0.8000$ (Missed rate $20\%$) | **`[FAIL]`** |
| **Gate 3: Controlled FPR** | $\text{False Positive Rate} \le 0.05$ | $\text{FPR} = 0.1667$ | **`[FAIL]`** |
| **Gate 4: Statistical Power Adequacy** | Adequate sample power ($N \ge 384$) | $N = 11$, Margin of Error $\pm 29.55\%$ | **`[FAIL] (Underpowered)`** |
| **Gate 5: Provenance** | Documented source & license/UNKNOWN | $100\%$ documented provenance | **`[PASS]`** |
| **Gate 6: Golden Benchmark** | Zero regression on 29 golden cases | $29/29$ golden cases pass | **`[PASS]`** |
| **Gate 7: Artifact Integrity** | SHA-256 hash in model registry | Hash verified and logged | **`[PASS]`** |
| **Gate 8: Dual Calibration** | Separate Brier and exact ECE | Brier `0.1409`, ECE `0.1681` logged | **`[PASS]`** |

---

## 9. Final Model Promotion Decision & Registry State

- **Promotion Decision**: **`DO NOT PROMOTE model-v2.0.0`**.
- **Active Runtime Engine**: **`logisticregression-v1.0.0` remains `[ACTIVE PRODUCTION]`**.
- **Candidate Status**: **`model-v2.0.0` is maintained on `[CANDIDATE / STANDBY]`**.
