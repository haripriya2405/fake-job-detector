# AI-Based Fake Job & Internship Detection Platform — Project Bible

## 1. Executive Summary & Mission
The Fake Job & Internship Detection Platform is an explainable AI-powered security and intelligence system designed to protect students, fresh graduates, and job seekers from fraudulent employment postings, deceptive internship scams, identity theft, and upfront-fee fraud.

The system does NOT claim absolute binary certainty ("100% fake" or "100% real"). Instead, it produces a calibrated **0–100 Suspiciousness / Risk Score** accompanied by granular evidence, explainable ML/rule score contributions, domain verification indicators, and concrete safety recommendations.

---

## 2. Risk Scoring Scale & Thresholds
- **0 – 29 | Low Risk (Safe / Legitimate Pattern)**: Standard corporate communications, verifiable corporate domain, standard application workflows, typical industry compensation.
- **30 – 59 | Medium Risk (Requires Caution)**: Minor red flags such as generic descriptions, personal email addresses (e.g. Gmail/Yahoo for a reputed brand), or slight salary inflation.
- **60 – 79 | High Risk (Suspicious Indicators Detected)**: Urgent hiring tactics, suspicious payment or equipment deposit requests, unverified domain, mismatching recruiter credentials.
- **80 – 100 | Critical Risk (High Scam Probability)**: Direct upfront payment / registration fee demands, Telegram / WhatsApp-only interview processes, fake checks/crypto transactions, phishing domains.

---

## 3. Technology Baseline & Architecture

### Frontend
- **Framework**: React 18+ with Vite
- **Styling**: Tailwind CSS (Dark AI/Cybersecurity Theme: `#070B14`, `#0F172A`, `#111827`, `#3B82F6`, `#06B6D4`, `#8B5CF6`)
- **Animation**: Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router v6
- **Charts & Data Viz**: Recharts
- **Networking**: Axios (with centralized API service & mock fallback)

### Backend (Future Integration Phase)
- **Framework**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn
- **Architecture**: Clean Modular Architecture (Routers, Services, ML Pipeline, Rule Engine, Data Access Layer)

### AI / Machine Learning (Future Integration Phase)
- **Baseline**: scikit-learn, TF-IDF Vectorizer + Calibrated Logistic Regression / Linear SVM trained on EMSCAD / Kaggle fake job datasets.
- **Explainability**: LIME / SHAP / Feature importance breakdown + Heuristic Rule Engine.
- **Advanced Phase**: Hugging Face DeBERTa / RoBERTa fine-tuned transformer.

### Database (Future Integration Phase)
- **Storage**: PostgreSQL + SQLAlchemy / Alembic migrations.

---

## 4. API Endpoints Contract
- `POST /api/v1/analysis`: Analyze plain text job posting
- `POST /api/v1/analysis/upload`: Analyze uploaded PDF / screenshot (OCR extract)
- `GET /api/v1/analysis/:id`: Retrieve specific analysis report by ID
- `GET /api/v1/analysis/history`: Retrieve past analyses with filtering and search
- `DELETE /api/v1/analysis/:id`: Delete a saved analysis report
- `POST /api/v1/auth/register`: User registration
- `POST /api/v1/auth/login`: User login / JWT issuance
- `GET /api/v1/auth/me`: Current user session and preferences
