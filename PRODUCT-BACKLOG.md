# Product Backlog — AI Fake Job & Internship Detector

## Epic 1: Frontend Interface & Visualization Engine
- **US-1.1**: Modern Cyber-AI Dark Themed Landing Page with feature highlights, sample scam indicators, and live demo preview.
- **US-1.2**: Authentication Flow (Login & Register) with JWT token lifecycle, validation, and demo mock accounts.
- **US-1.3**: Interactive Analyzer Workspace supporting 3 modalities: Raw Text/Job Description, PDF Document Upload, and Screenshot/Image Upload.
- **US-1.4**: Comprehensive Explainable Analysis Result Page featuring:
  - 0–100 Gauge/Radial Risk Score
  - 4-Tier Risk Categorization (Low, Medium, High, Critical)
  - Red Flag Indicators with Evidence Snippets & Severity Badges
  - Scoring Contribution Breakdown (Machine Learning Probability vs Heuristic Rules vs Domain Trust)
  - Company & Domain Verification Cards (WHOIS age, MX records, LinkedIn cross-reference)
  - Actionable Step-by-Step Safety Recommendations
- **US-1.5**: Analysis History Dashboard with search, risk filter, tag management, and quick re-inspection.
- **US-1.6**: Analysis Detail View & Export Report functionality (JSON / Printable Report).
- **US-1.7**: User Settings & API Key / Notification preference management.

## Epic 2: Backend API & Analysis Orchestrator
- **US-2.1**: FastAPI application lifecycle with CORS, rate limiting, and structured logging.
- **US-2.2**: Authentication router (OAuth2 password bearer + JWT).
- **US-2.3**: Analysis orchestrator combining ML inference, Rule Engine, Domain Verifier, and Text Preprocessing.
- **US-2.4**: Document extraction pipeline (PyPDF / pdfplumber for PDFs, Tesseract / OCR for screenshots).

## Epic 3: Machine Learning & Explainability Model
- **US-3.1**: Text preprocessor (stopword removal, URL extractor, contact extractor, salary normalizer).
- **US-3.2**: TF-IDF Vectorizer + Calibrated Logistic Regression model trained on EMSCAD benchmark dataset.
- **US-3.3**: Explainability module generating top feature token weights and contextual evidence spans.

## Epic 4: Heuristic Security Rule Engine
- **US-4.1**: Upfront fee / security deposit detection.
- **US-4.2**: Unofficial communication channels (Telegram, WhatsApp, free webmail like gmail/yahoo for corporate claims).
- **US-4.3**: Salary outlier & unrealistic compensation multiplier detection.
- **US-4.4**: Urgency and pressure tactics detection ("immediate hiring without interview").
