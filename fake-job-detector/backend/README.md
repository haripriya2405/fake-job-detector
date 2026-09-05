# SentinelJob AI — Backend Foundation API

FastAPI-powered explainable intelligence backend for detecting fraudulent employment offers, deceptive internships, and recruitment scams.

---

## 1. Stack & Architecture

- **Runtime**: Python 3.12+
- **API Framework**: FastAPI, Pydantic v2, Uvicorn
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM & Alembic migrations
- **Authentication**: JWT tokens (HMAC-SHA256) with bcrypt password hashing
- **Testing**: pytest & httpx TestClient

---

## 2. Directory Layout

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # /api/v1/auth (register, login, me)
│   │       ├── analysis.py      # /api/v1/analysis (create, upload, get, history, delete)
│   │       ├── health.py        # /api/v1/health & /health
│   │       └── router.py        # Root v1 router aggregation
│   ├── core/
│   │   ├── config.py            # Pydantic Settings & environment variables
│   │   ├── security.py          # bcrypt password hashing & JWT token management
│   │   ├── logging.py           # Structured system logging
│   │   └── exceptions.py        # Typed HTTP error hierarchy
│   ├── db/
│   │   ├── base.py              # DeclarativeBase, GUID type decorator & TimestampMixin
│   │   └── session.py           # Engine & get_db dependency injection
│   ├── models/                  # SQLAlchemy 2.x Database Models
│   │   ├── user.py              # User entity
│   │   ├── analysis.py          # Analysis record entity
│   │   ├── indicator.py         # AnalysisIndicator red-flag entity
│   │   ├── url.py               # UrlAnalysis link inspection entity
│   │   ├── verification.py      # VerificationResult entity
│   │   ├── model_version.py     # ModelVersion ML metadata entity
│   │   ├── rule_version.py      # RuleVersion heuristic metadata entity
│   │   └── audit_log.py         # AuditLog security trail entity
│   ├── schemas/                 # Pydantic v2 Request & Response contracts
│   ├── services/                # Business logic services
│   ├── ml/                      # Machine Learning interfaces (Phase 3 ready)
│   ├── rules/                   # Heuristic security rule interfaces (Phase 3 ready)
│   ├── verification/            # WHOIS & domain verification interfaces (Phase 3 ready)
│   └── main.py                  # FastAPI application factory & CORS configuration
├── alembic/                     # Database migration scripts
├── tests/                       # Automated pytest suite
├── requirements.txt
├── .env.example
└── .env
```

---

## 3. Running Locally

### Activate Virtual Environment
```bash
cd backend
.\venv\Scripts\Activate.ps1
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Generate & Apply Migrations
```bash
alembic revision --autogenerate -m "initial_schema"
alembic upgrade head
```

### Start Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 4. Running Test Suite

```bash
pytest
```

---

## 5. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Root health check |
| `GET` | `/api/v1/health` | Telemetry & database connectivity |
| `POST` | `/api/v1/auth/register` | Register new user account |
| `POST` | `/api/v1/auth/login` | Authenticate & receive JWT |
| `GET` | `/api/v1/auth/me` | Current user profile (Bearer token) |
| `POST` | `/api/v1/analysis` | Ingest raw job text for risk evaluation |
| `POST` | `/api/v1/analysis/upload` | Upload PDF or Screenshot offer |
| `GET` | `/api/v1/analysis/:id` | Retrieve forensic analysis report |
| `GET` | `/api/v1/analysis/history` | List user scan ledger |
| `DELETE` | `/api/v1/analysis/:id` | Delete scan report |
