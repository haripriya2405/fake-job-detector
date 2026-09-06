# SentinelJob AI — Reference UI & Product Gap Analysis

## Executive Summary
This document establishes the UI/UX, architectural, and intelligence gap analysis between the reference product demonstration specifications and the existing SentinelJob AI codebase.

---

## Matrix: Feature & Gap Analysis

| Ref Feature | Existing Implementation | Gap / Missing Implementation | Required Production Change | Priority |
| :--- | :--- | :--- | :--- | :---: |
| **8-Layer Signal Engine** | 8 signal layers computed in `job_scam_score_service.py` | Need unified stage tracking per layer with strict `VERIFIED`, `WARNING`, `FAILED`, `UNAVAILABLE`, `NOT_CHECKED` states. | Standardize 8-layer schema and response format. | High |
| **LLM Orchestration Layer** | Direct httpx calls in `ai_explainer.py` | Missing formal provider abstraction (OpenAI, Anthropic, Gemini, Local), retry logic, prompt versioning, structured Pydantic output, anti-prompt injection shielding, and fallback metrics. | Create `backend/app/llm/` module with full provider factory, telemetry, versioned prompts, and deterministic fallback. | Critical |
| **Scam Archetype Taxonomy** | Basic string indicators in rules engine | Missing explicit primary & secondary archetype classifications (`TASK_SCAM`, `FAKE_CHECK`, `ADVANCE_FEE`, `IDENTITY_HARVEST`, `GHOST_JOB`, `RESHIPPING`, `FAKE_RECRUITER`, `IMPERSONATION`, `CRYPTO_SCAM`, `PAYMENT_SCAM`, `INVESTMENT_SCAM`, `OTHER`). | Implement `ScamArchetypeService` and Pydantic schemas. | High |
| **13-Stage Pipeline** | Sequential service calls in `analysis_service.py` | Need structured telemetry logging per stage (status, duration, evidence, confidence, errors). | Implement `MultiStagePipeline` orchestrator. | High |
| **ML Governance Invariant** | Active: `logisticregression-v1.0.0`, Standby: `transformer-v1.0.0-candidate` | Must be strictly preserved with zero auto-promotion and intact rollback. | Verify promotion gate and registry invariances. | Critical |
| **Multi-Modal Scanning** | Text, URL, PDF, and Image/OCR supported | Ensure SSRF protection (localhost, private IP, metadata IP blocking) is applied uniformly. | Verify and test SSRF defenses across URL ingestion. | High |
| **Forensic Result UI** | 0-100 Risk Score, Verdict (SAFE, CAUTION, RISKY), 8-layer breakdown, salary matrix, domain RDAP | Ensure high-density obsidian/emerald visual design, evidence traceability, and verification certificates. | Enhance frontend presentation with archetype badges and stage telemetry. | High |
| **User Dashboard & History** | Scans saved to SQLite/Postgres with delete & detail viewing | Ensure pagination, filtering, search, and user authorization isolation. | Verify dashboard & history endpoints and UI filters. | Medium |
| **Red Flags Guide & Alerts** | Educational guide with scam categories and advisory feed | Clearly separate live feeds from documented advisory patterns; ensure rich guidance. | Update educational guide with full archetype breakdowns. | Medium |

---

## Architectural Invariants
1. **Model Governance**: `logisticregression-v1.0.0` remains the sole active production scoring model. Transformer remains STANDBY.
2. **Deterministic Primacy**: Hard security blocks and deterministic scam indicators cannot be overridden by LLM outputs.
3. **Graceful Degradation**: If an LLM provider times out or fails, the system returns `LLM_SYNTHESIS_UNAVAILABLE` and presents the complete deterministic + ML + 8-layer analysis without crashing.
