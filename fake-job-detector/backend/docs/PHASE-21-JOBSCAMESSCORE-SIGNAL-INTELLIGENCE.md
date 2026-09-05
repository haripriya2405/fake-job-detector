# SentinelJob AI — Phase 21: JobScamScore 8-Layer Signal Intelligence & Market Verification

## Overview

In Phase 21, SentinelJob AI upgraded its detection and user experience to match the multi-layer security architecture and dark obsidian aesthetic of **JobScamScore**.

Rather than relying purely on text classifiers, the risk assessment is now synthesized through an **8-Layer Parallel Signal Intelligence Stack** evaluating company domain authority, official ATS live verification, recruiter identity, real-world market salary feasibility, threat databases, and cited Red/Green flag evidence.

---

## 1. The 8-Layer Signal Intelligence Stack

```mermaid
flowchart TD
    JobInput[Job Posting Input / URL / PDF / Image] --> Ingestion[Multi-Modal Ingestion Engine]
    Ingestion --> L1[Layer 1: Company Authentication & Domain Age]
    Ingestion --> L2[Layer 2: Official Careers Page & ATS Verification]
    Ingestion --> L3[Layer 3: Recruiter Identity & Free-Email Trap Detection]
    Ingestion --> L4[Layer 4: Real-World BLS/EMSCAD Salary Benchmarking]
    Ingestion --> L5[Layer 5: 30+ AI & Transformer Scam Pattern Recognition]
    Ingestion --> L6[Layer 6: Contact & FTC/IC3/BBB Threat Intelligence]
    Ingestion --> L7[Layer 7: Domain & SSL Infrastructure Intelligence]
    Ingestion --> L8[Layer 8: Live Trust Score & Reputation Engine]
    
    L1 & L2 & L3 & L4 & L5 & L6 & L7 & L8 --> Synthesis[Unified Multi-Factor Synthesis Engine]
    Synthesis --> Verdict[Verdict Category: SAFE | CAUTION | RISKY]
    Synthesis --> Evidence[Red Flags & Green Flags Evidence Panel]
```

### Layer Breakdown
1. **Layer 1: Company Authentication & Domain Age**:
   - Inspects domain creation timestamp via RDAP.
   - Domains $< 30$ days old receive immediate high-fraud penalties.
   - Domains $> 2$ years receive positive trust credits.
2. **Layer 2: Official Careers Page & ATS Verification**:
   - Live checks for Enterprise ATS hosts: Greenhouse (`boards.greenhouse.io`), Lever (`jobs.lever.co`), Workday (`myworkdayjobs.com`), Ashby (`jobs.ashbyhq.com`), SmartRecruiters, and BambooHR.
   - Validates whether job posting originates directly from verified corporate careers infrastructure.
3. **Layer 3: Recruiter Identity**:
   - Detects free/public webmail providers (`@gmail.com`, `@yahoo.com`, `@hotmail.com`, `@outlook.com`).
   - Flags unauthorized messaging funnels (Telegram, WhatsApp, Signal) used for off-platform interviews.
4. **Layer 4: Real-World Market Salary Benchmarking**:
   - Classifies job postings into empirical job families (Data Entry, Customer Support, Admin, Software Engineering, Data Science, Sales/Marketing, General Corporate).
   - Compares stated compensation against BLS 25th percentile, median, and 90th percentile bounds.
   - Flags $> 50\%$ above-market lures (e.g. \$75/hr data entry) as `UNREALISTIC_HIGH_TRAP`.
5. **Layer 5: Scam Pattern Recognition**:
   - Evaluates 30+ deterministic security rules and transformer manipulation spans covering registration fees, cashier check laundering, cryptocurrency recharge tasks, and PII harvesting.
6. **Layer 6: Contact & Threat Intelligence Validation**:
   - Cross-references identifiers against patterns cataloged by the FTC, FBI IC3, and Better Business Bureau.
7. **Layer 7: Domain & SSL Infrastructure Intelligence**:
   - Evaluates MX DNS mail exchange records, SSL certificates, typosquatting, and redirect chains.
8. **Layer 8: Live Threat Intelligence & Composite Trust Score**:
   - Computes ScamDoc-equivalent composite trust rating (0–100) and compiles structured Red/Green flag evidence lists.

---

## 2. Frontend UI Upgrades

- **Auth Screens (`LoginPage.jsx` & `RegisterPage.jsx`)**:
  - Matched JobScamScore's obsidian dark aesthetic (`#060b08` / `#0c1410`).
  - Added "Continue with Google" OAuth button.
  - Added language selector pill and sleek back-to-landing navigation.
- **Analysis Results (`AnalysisResultPage.jsx`)**:
  - Added **Red Flags & Green Flags Evidence Panel** citing exact reasons for trust or risk.
  - Added **8-Layer Signal Intelligence Stack Dashboard** (`SignalStack8Layer.jsx`) displaying all 50+ check results.
  - Added **Market Salary Benchmark Analysis Widget** (`SalaryBenchmarkCard.jsx`) with variance ratio and BLS median comparisons.

---

## 3. Verification & Test Suite

- **Python Version**: Python 3.14.7 (`backend/venv314/Scripts/python.exe`)
- **Backend Test Suite**: **197 / 197 tests passing (100%)**
- **Frontend Build**: Vite production build succeeded cleanly (`dist/` generated with zero errors).
