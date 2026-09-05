# Architecture Decisions Record (ADR)

## ADR-001: Hybrid Scoring Engine (ML Model + Deterministic Rule Engine)
- **Context**: Relying solely on statistical NLP models can produce false positives on novel legitimate job postings, while missing hard indicators like explicit payment requests in Telegram.
- **Decision**: Combine calibrated ML probability scores (45% weight) with deterministic security rule flags (40% weight) and domain/company intelligence lookups (15% weight) to produce an explainable aggregate 0–100 risk score.
- **Consequences**: High explainability, robust defense against adversarial wording, clear attribution in UI.

## ADR-002: Frontend Architecture & Decoupled Mock Layer
- **Context**: Need a production-grade, highly responsive React frontend with instant interactive demos, even prior to backend deployment.
- **Decision**: Implement a clean service layer (`src/services/api.js` and `src/services/analysisService.js`) that checks environment variables and provides rich realistic mock telemetry when backend is unavailable.
- **Consequences**: Effortless transition to real FastAPI backend with zero changes to presentation components.

## ADR-003: UI Theme & Aesthetics
- **Context**: The platform serves high-stakes security analysis for professionals, students, and recruiters.
- **Decision**: Adopt a focused Dark Security/Cyber theme (#070B14 base, #0F172A surfaces, #3B82F6 primary, #8B5CF6 AI accent) with strict accessibility contrast, crisp typography, and purposeful data visualization without excessive clutter.
