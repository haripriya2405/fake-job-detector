# SentinelJob AI — Final Production Architecture (Phase 22)

## 1. System Architecture Overview

SentinelJob AI is an explainable enterprise recruitment fraud intelligence platform architected around a **13-Stage Verification Pipeline** and an **8-Layer Intelligence Stack**:

```
                       USER SUBMISSION
              (Text / URL / Image / PDF)
                         |
                         v
       +------------------------------------+
       |   Stage 1 & 2: Input & Normalizer  |
       +------------------------------------+
                         |
      +------------------+------------------+
      |                  |                  |
      v                  v                  v
[Deterministic]      [Scikit-Learn]     [Domain / DNS]
[Scam Rules   ]      [LinearSVM/LogReg] [RDAP & MX   ]
      |                  |                  |
      +------------------+------------------+
                         |
                         v
       +------------------------------------+
       |    Stage 5-10: 8-Layer Signal Stack|
       |  (ATS, Salary Matrix, Contact, etc)|
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |   Stage 11: LLM Evidence Synthesis |
       |   (Gemini / OpenAI / Claude / Fall)|
       +------------------------------------+
                         |
                         v
       +------------------------------------+
       |  Stage 12 & 13: Risk Fusion & Cert |
       +------------------------------------+
                         |
                         v
                EXPLAINABLE REPORT
           (Score, Archetypes, Badges)
```

---

## 2. 13-Stage Pipeline Breakdown

| Stage | Name | Role & Methodology |
| :--- | :--- | :--- |
| **01** | **Input Validation** | MIME inspection, size enforcement (<=10MB), and payload bounds. |
| **02** | **Text Normalization** | Unicode normalization, whitespace collapsing, and delimiter escaping. |
| **03** | **Deterministic Rules** | High-precision regex pattern match (UPI QR, advance fees, check overpayments). |
| **04** | **ML Classification** | Fast CPU inference on active production model (`logisticregression-v1.0.0`). |
| **05** | **Domain Verification** | RDAP registration age, WHOIS analysis, and DNS resolution. |
| **06** | **Recruiter Verification** | Disposable email blocklist and corporate domain matching. |
| **07** | **ATS Verification** | Cross-referencing against verified ATS boards (Greenhouse, Lever, Workday). |
| **08** | **Salary Benchmarking** | Percentile analysis against Indian (`LPA`/`INR`) and Global (`USD`) compensation matrices. |
| **09** | **Contact Validation** | Area code mapping, carrier identification, and VoIP burner detection. |
| **10** | **Threat Intelligence** | Live cross-referencing with I4C 1930 Helpline, FTC, BBB, and FBI IC3 advisories. |
| **11** | **LLM Evidence Synthesis**| Structured Pydantic synthesis via Gemini 1.5 Flash / OpenAI with zero-failure fallback. |
| **12** | **Composite Risk Fusion** | Calibrated multi-factor risk scoring with non-linear penalties. |
| **13** | **Explainable Report** | PDF proof generation, cryptographic hash signing, and actionable checklist. |

---

## 3. ML Model Governance Invariant

- **Active Production Model**: `logisticregression-v1.0.0` (Platt Scaled)
- **Candidate Model**: `transformer-v1.0.0-candidate` (DeBERTa-v3/ONNX)
- **Status**: Standby (Auto-promotion disabled; qualification gates strictly preserved).
- **Rollback**: Fully operational via model registry metadata.
