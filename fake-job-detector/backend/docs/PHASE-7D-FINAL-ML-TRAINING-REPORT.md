# Phase 7D — Final ML Training, Generalization & Robustness Report

**Date**: 2026-08-17  
**Status**: `COMPLETE & VERIFIED`  
**Active Production Model**: `logisticregression-v1.0.0` (Retained as Production Engine)  
**Candidate Standby Model**: `model-v2.0.0` (LinearSVM + Platt Sigmoid Scaling)  
**Automated Test Suite**: **103/103 Tests Passing (100% Pass Rate)**

---

## 1. Executive Summary

Phase 7D represents the complete, statistically rigorous conclusion to the Machine Learning lifecycle for SentinelJob AI. 

### Key Accomplishments:
1. **Curated & Documented Production Corpus**: Multi-category dataset containing **63 clean accepted records** across 11 vertical categories. Zero undocumented records or invented licenses; all unverified sources explicitly labeled `UNKNOWN`.
2. **Dedicated Adversarial Robustness Benchmark**: Created an isolated, standalone benchmark of **8 adversarial evasion cases** (spaced keywords, punctuation injection, paraphrased deposits, disguised task schemes, homoglyphs) evaluated separately to prevent holdout contamination.
3. **Leakage-Free Stratified Partitions**: Partitioned into **Historical Training (70%, $N=43$)**, **Validation Split (15%, $N=9$)**, and **Untouched Contemporary Holdout (15%, $N=11$)** with zero cross-split record, hash, or near-duplicate leakage ($\text{Train} \cap \text{Val} \cap \text{Holdout} = \emptyset$).
4. **5-Fold Stratified Cross-Validation on Development Data**:
   - Accuracy: $0.9306 \pm 0.0569$
   - Precision: $1.0000 \pm 0.0000$
   - Recall: $0.8333 \pm 0.1394$
   - F1-Score: $0.9029 \pm 0.0820$
   - ROC-AUC: $1.0000 \pm 0.0000$
5. **Non-Parametric Bootstrap Uncertainty (B=1000, 95% CI)**: Computed point estimates and 95% confidence intervals on the holdout.
6. **Validation Threshold Optimization**: Grid-searched $\tau \in [0.10, 0.90]$ with cost matrix ($10.0 \times \text{FN} + 1.0 \times \text{FP}$) on validation data only; single-pass holdout evaluation performed at $\tau^* = 0.30$.
7. **Dual Calibration Analysis**: Documented that Platt-scaled Linear SVM achieves Brier loss of $0.1409$ and ECE of $0.1681$ (vs Baseline Brier $0.1917$, ECE $0.1697$). Model superiority is not claimed on Brier score alone.
8. **Promotion Gate & Registry State**: The 12-factor statistical promotion gate blocked premature promotion due to statistical sample power limits ($N=11$ vs target $N \ge 384$). `logisticregression-v1.0.0` is strictly retained as **`[ACTIVE PRODUCTION]`**; candidate model `model-v2.0.0` is safely serialized to `artifacts/models/` and registered on **`[STANDBY]`**.

---

## 2. Dataset Provenance & Category Distribution

### Real-World Production Corpus ($N=63$ Clean Records)
- **Legitimate Class ($N=35, 55.6\%$)**:
  - `Enterprise Tech`: Stripe, Google Cloud, AWS, Vercel, Datadog, Snowflake, Apple, Netflix, Meta, Atlassian, Cloudflare, Figma ($12$ records)
  - `Higher Education & Academic Research`: Stanford AI Lab, Broad Institute/MIT, Cambridge, Oxford, CMU ($5$ records)
  - `Healthcare & Clinical Systems`: Mayo Clinic, Cleveland Clinic, Johns Hopkins, Kaiser Permanente, NHS ($5$ records)
  - `Public Sector & Government`: CISA, NASA JPL, CDC, NIST, UK Civil Service ($5$ records)
  - `Borderline & High-Salary Startups`: Early-stage AI, Remote consulting, Series-A startups ($8$ records)
- **Fraudulent Class ($N=28, 44.4\%$)**:
  - `Advance-Fee & Security Deposits`: Registration, onboarding background check fees ($6$ records)
  - `Cashier Check & Overpayment Schemes`: Equipment purchasing, money mule wiring ($4$ records)
  - `Cryptocurrency & Task Traps`: Telegram VIP task recharge, USDT hotel rating ($4$ records)
  - `Brand Impersonation & Phishing`: Executive lookalikes, typosquatted portals ($5$ records)
  - `PII & Credential Harvesting`: Direct banking login / OTP theft, identity theft ($5$ records)
  - `Messaging Funnels & Unsolicited WhatsApp/Signal Outreach`: ($4$ records)

### Provenance Safeguards
- **100% Documented Sources**: 15 distinct corporate, institutional, and research sources.
- **Licensing**: All unverified commercial or open-web job postings marked explicitly as **`UNKNOWN / Public Corporate Posting`** or **`UNKNOWN / ATS Listing`**.
- **Deduplication**: 0 exact duplicates, 0 normalized duplicates, 1 near-duplicate dropped ($\text{Jaccard} \ge 0.88$).

---

## 3. Dedicated Adversarial Robustness Benchmark ($N=8$)

Adversarial synthetic patterns are isolated from real-world training/holdout sets:

| Case ID | Attack Type | Evasion Description | Model Prediction | Result |
| :--- | :--- | :--- | :--- | :--- |
| `ADV-SPACE-01` | Spaced Keywords | `r e g i s t r a t i o n` fee & `T e l e g r a m` handle | Prob: $0.9821$ | **`[CAUGHT]`** |
| `ADV-SPACE-02` | Spaced Crypto | `U S D T` transfer to company `w a l l e t` | Prob: $0.9542$ | **`[CAUGHT]`** |
| `ADV-PUNCT-01` | Punctuation Injection | `c.a.s.h.i.e.r - c.h.e.c.k` & `W.e.s.t.e.r.n U.n.i.o.n` | Prob: $0.9610$ | **`[CAUGHT]`** |
| `ADV-PARAPH-01`| Paraphrased Advance Fee | `refundable transit courier insurance contribution` | Prob: $0.9125$ | **`[CAUGHT]`** |
| `ADV-PARAPH-02`| Paraphrased Task Fraud | `merchant workstation balance funding` | Prob: $0.9204$ | **`[CAUGHT]`** |
| `ADV-PII-01`   | Credential Theft | Demanding online banking password + 6-digit OTP | Prob: $0.9940$ | **`[CAUGHT]`** |
| `ADV-IMPER-01` | Lookalike Domain | Typosquatted `.xyz` subdomain + verification fee | Prob: $0.9730$ | **`[CAUGHT]`** |
| `ADV-HOMO-01`  | Cyrillic Homoglyphs | Visual Cyrillic character substitution | Prob: $0.9850$ | **`[CAUGHT]`** |

**Adversarial Robustness Score**: **`100.0% (8/8 Detected)`**

---

## 4. Multi-Model Benchmark & Holdout Generalization

Evaluated on the untouched contemporary holdout split ($N=11$):

| Metric | Logistic Regression v1.0.0 (Baseline) | Logistic Regression v2.0.0 (Candidate) | Linear SVM v2.0.0 (Platt Scaled) |
| :--- | :--- | :--- | :--- |
| **Accuracy** | `0.8182` | `0.8182` | `0.8182` |
| **Precision** | `0.8000` | `0.8000` | `0.8000` |
| **Recall (Threat Catch)** | `0.8000` | `0.8000` | `0.8000` |
| **F1-Score** | `0.8000` | `0.8000` | `0.8000` |
| **False Positive Rate** | `0.1667` | `0.1667` | `0.1667` |
| **ROC-AUC** | `0.9333` | `0.9333` | `0.9333` |
| **PR-AUC** | `0.9267` | `0.9267` | `0.9267` |
| **Brier Score** | `0.1917` | `0.1862` | **`0.1409`** |
| **Expected Calibration Error** | `0.1697` | `0.1840` | `0.1681` |

---

## 5. Non-Parametric Bootstrap Confidence Intervals ($B=1000$, 95% CI)

| Metric | Point Estimate | 95% Bootstrap CI | CI Width |
| :--- | :--- | :--- | :--- |
| **Accuracy** | `0.8182` | `[0.5455, 1.0000]` | `0.4545` |
| **Precision** | `0.8000` | `[0.3975, 1.0000]` | `0.6025` |
| **Recall** | `0.8000` | `[0.3333, 1.0000]` | `0.6667` |
| **F1-Score** | `0.8000` | `[0.4000, 1.0000]` | `0.6000` |
| **FPR** | `0.1667` | `[0.0000, 0.5000]` | `0.5000` |
| **ROC-AUC** | `0.9333` | `[0.7000, 1.0000]` | `0.3000` |
| **PR-AUC** | `0.9267` | `[0.6667, 1.0000]` | `0.3333` |

---

## 6. Validation Threshold Optimization & Holdout Result

Grid search across $\tau \in [0.10, 0.90]$ with cost weights ($10.0 \times \text{FN} + 1.0 \times \text{FP}$):

| Validation Threshold ($\tau$) | Precision | Recall | F1-Score | Validation Decision Loss |
| :--- | :--- | :--- | :--- | :--- |
| $\tau = 0.10$ | `0.8000` | `1.0000` | `0.8889` | `1.0` ($\text{FP}=1, \text{FN}=0$) |
| $\tau = 0.20$ | `0.8000` | `1.0000` | `0.8889` | `1.0` ($\text{FP}=1, \text{FN}=0$) |
| **$\tau = 0.30$ (Optimal)** | **`1.0000`** | **`1.0000`** | **`1.0000`** | **`0.0`** ($\text{FP}=0, \text{FN}=0$) |
| $\tau = 0.40$ | `1.0000` | `1.0000` | `1.0000` | `0.0` |
| $\tau = 0.50$ | `1.0000` | `1.0000` | `1.0000` | `0.0` |
| $\tau = 0.60$ | `1.0000` | `1.0000` | `1.0000` | `0.0` |
| $\tau = 0.70$ | `1.0000` | `1.0000` | `1.0000` | `0.0` |
| $\tau = 0.80$ | `1.0000` | `0.7500` | `0.8571` | `10.0` ($\text{FP}=0, \text{FN}=1$) |
| $\tau = 0.90$ | `1.0000` | `0.5000` | `0.6667` | `20.0` ($\text{FP}=0, \text{FN}=2$) |

**Single-Pass Untouched Holdout Evaluation at $\tau^* = 0.30$**:
- Holdout Precision: `0.8000`
- Holdout Recall: `0.8000`
- Holdout F1-Score: `0.8000`
- Holdout Decision Loss: `11.0` ($\text{TP}=4, \text{TN}=5, \text{FP}=1, \text{FN}=1$)

---

## 7. Model Promotion Gate Evaluation

| Factor / Gate | Requirement | Candidate Result | Gate Status |
| :--- | :--- | :--- | :--- |
| **Gate 1: Generalization** | $\text{F1} \ge 0.90$, $\text{ROC-AUC} \ge 0.90$ | $\text{F1} = 0.8000$, $\text{ROC-AUC} = 0.9333$ | **`[FAIL]`** |
| **Gate 2: Low False Negatives** | $\text{Recall} \ge 0.95$ on fraud threats | $\text{Recall} = 0.8000$ (Missed threat rate: $20\%$) | **`[FAIL]`** |
| **Gate 3: Controlled FPR** | $\text{False Positive Rate} \le 0.05$ | $\text{FPR} = 0.1667$ | **`[FAIL]`** |
| **Gate 4: Statistical Power Adequacy** | Adequately powered sample ($N \ge 384$) | $N = 11$, Margin of Error $\pm 29.55\%$ | **`[FAIL] (Underpowered)`** |
| **Gate 5: Provenance** | Documented source & license/UNKNOWN | $100\%$ documented provenance | **`[PASS]`** |
| **Gate 6: Golden Benchmark** | Zero regression on 29 golden cases | $29/29$ golden cases pass | **`[PASS]`** |
| **Gate 7: Artifact Integrity** | SHA-256 hash in model registry | Hash verified and logged | **`[PASS]`** |
| **Gate 8: Dual Calibration** | Separate Brier and exact ECE | Brier `0.1409`, ECE `0.1681` logged | **`[PASS]`** |
| **Gate 9: Adversarial Robustness** | Separate benchmark evaluation | $100\%$ detection ($8/8$ evasions caught) | **`[PASS]`** |
| **Gate 10: Reproducibility** | Seeds, configs, parameters logged | Seeds $=42$, TF-IDF parameters logged | **`[PASS]`** |
| **Gate 11: Rollback Safety** | Verified instant fallback to baseline | Verified in registry test suite | **`[PASS]`** |
| **Gate 12: Security Isolation** | Safe deserialization & no token leaks | Verified in API security tests | **`[PASS]`** |

**Final Promotion Verdict**: **`DO NOT PROMOTE model-v2.0.0`**.  
`logisticregression-v1.0.0` remains **`[ACTIVE PRODUCTION]`**. `model-v2.0.0` remains on **`[STANDBY]`**.

---

## 8. Known Limitations

1. **Sample Size Power**: While the corpus covers 11 diverse categories with 100% provenance, $N=63$ (and holdout $N=11$) is statistically underpowered relative to theoretical asymptotic requirements ($N \ge 384$ for $\le 5\%$ error at $95\%$ CI).
2. **Probability Calibration**: ECE remains $\sim 0.1681$ across models. High-stakes binary decisions must remain mediated by the deterministic RuleEngine and RiskEngine rather than relying solely on raw ML probabilities.

---

## 9. Reproducibility Guide

```bash
# Execute full production training, threshold optimization & registry sync
python train_production_model.py

# Execute full automated test suite (103 tests)
pytest -v
```
