# SentinelJob AI — Phase 18: Production Hardening, Containerization & Deployment Readiness

## 1. System Architecture & Container Topology

SentinelJob AI is organized into a containerized 3-tier production architecture:
1. **Frontend Tier (Nginx 1.27 + React SPA)**: Serves the optimized multi-chunk Vite frontend, enforces HTTP security headers, manages client request limits (15 MB), and reverse proxies API traffic.
2. **Backend Tier (FastAPI + Uvicorn + Tesseract OCR)**: Multi-modal ingestion, deterministic heuristics, TF-IDF ML classifier, company & RDAP domain verification, risk engine, and structured logging. Runs as an unprivileged non-root user (`appuser`).
3. **Database Tier (PostgreSQL 16)**: Relational storage for user accounts, multi-modal analyses, extraction telemetry, forensic indicators, and domain verifications, with persistent volume storage (`sentineljob_postgres_data`).

```
                              Internet / Browser
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │    Nginx (Port 3000/80)   │
                        │    - Static SPA routing   │
                        │    - Security Headers     │
                        │    - Reverse Proxy        │
                        └─────────────┬─────────────┘
                                      │ /api/v1/*, /health, /ready
                                      ▼
                        ┌───────────────────────────┐
                        │   FastAPI ASGI (Port 8000)│
                        │   - Security Middlewares  │
                        │   - Request IDs (UUIDv4)  │
                        │   - Sliding Rate Limiter  │
                        │   - Multi-Modal Pipeline  │
                        │   - Tesseract OCR Engine  │
                        │   - ML Active: v1.0.0     │
                        └─────────────┬─────────────┘
                                      │ Connection Pool (SQLAlchemy 2.x)
                                      ▼
                        ┌───────────────────────────┐
                        │   PostgreSQL 16 Engine    │
                        │   (Persistent Volume)     │
                        └───────────────────────────┘
```

---

## 2. ML Model Governance Invariants

- **Production Active Model**: `logisticregression-v1.0.0` remains the sole **ACTIVE PRODUCTION** model.
- **Standby Candidate Model**: `model-v2.0.0` remains in **STANDBY** (strictly NOT promoted).
- **Dual Calibration & Safety**: All probabilistic outputs are strictly calibrated. Low-risk evaluations use conservative wording (*"No significant suspicious indicators detected"*) without asserting authenticity.

---

## 3. Security Hardening Specifications

### A. HTTP Security Headers
Every outgoing HTTP response from Nginx and FastAPI includes:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), camera=(), microphone=()`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains` (enforced in production & HTTPS)
- `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`

### B. Rate Limiting Architecture
- **Implementation**: In-memory sliding-window bucket algorithm configured per client IP.
- **Route Sensitivity Quotas**:
  - Authentication (`/auth/login`, `/auth/register`): `15 requests / minute`
  - Heavy Ingestion & Analysis (`/analysis`, `/analysis/upload`, `/analysis/url`): `20 requests / minute`
  - General Endpoints: `60 requests / minute`
  - Excluded from limiting: `/health`, `/ready`, `/docs`, `/openapi.json`
- **Exceeded Limit Response**: HTTP 429 Too Many Requests with `Retry-After: 60` and `request_id`.
- *Note on Distributed Scaling*: Process-local rate limiting protects single-instance deployments. For horizontal multi-worker clusters, Redis-backed rate limiting would be provisioned.

### C. Request Correlation & Observability
- Incoming requests receive an `X-Request-ID` header (or client-provided ID is preserved).
- Structured logs record: `[<request_id>] <METHOD> <PATH> -> <STATUS> (<LATENCY>ms) [client: <IP>]`.
- Passwords, JWT tokens, and sensitive document payloads are strictly excluded from logs.

### D. Multi-Modal Upload & Resource Protections
- **Max File Size**: 10 MB payload limit enforced at Nginx (15 MB buffer) and FastAPI.
- **Allowed MIME Types**: Whitelisted `application/pdf`, `image/png`, `image/jpeg`, `image/webp`.
- **Parser Security**: Safe PDF stream reading with zero macro/script execution; decompression bomb checks on images (`PIL.Image.MAX_IMAGE_PIXELS`).
- **OCR Timeout**: 10-second hard execution limit.

### E. SSRF Protection Firewall
- Strict pre-request and post-redirect IP filtering.
- Blocks: `localhost`, `127.0.0.1`, `::1`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`, `metadata.google.internal`, `.local`, `.corp`, `.internal`, `.lan`, and non-HTTP schemes (`ftp://`, `file://`).

---

## 4. Database Connection Pooling & Lifecycle

- **Engine**: SQLAlchemy 2.0 with connection pooling.
- **Pool Size**: 10 persistent connections (`DB_POOL_SIZE=10`).
- **Max Overflow**: 20 bursting connections (`DB_MAX_OVERFLOW=20`).
- **Pool Timeout**: 30 seconds (`DB_POOL_TIMEOUT=30`).
- **Pool Recycle**: 1800 seconds / 30 mins (`DB_POOL_RECYCLE=1800`).
- **Pre-Ping**: `pool_pre_ping=True` proactively validates connections before checkout.

---

## 5. Health & Readiness Probes

1. **Liveness Probe (`GET /health` and `GET /api/v1/health`)**:
   - Verifies process availability and general status.
   - Status: `200 OK` (`{"status": "healthy", "version": "1.0.0"}`).
2. **Readiness Probe (`GET /ready` and `GET /api/v1/ready`)**:
   - Executes a test query (`SELECT 1`) against PostgreSQL.
   - Status: `200 OK` (`{"status": "ready", "database": "operational"}`) when database is accessible.
   - Returns `503 Service Unavailable` (`{"status": "not_ready", "database": "unavailable"}`) when database is degraded.

---

## 6. Database Backup & Disaster Recovery Procedure

Automated backup and restore utilities are provided in `backend/scripts/`:
- `backup_db.sh` / `backup_db.ps1`: Generates gzip-compressed PostgreSQL dumps using `pg_dump --clean --if-exists --no-owner`.
- `restore_db.sh` / `restore_db.ps1`: Restores database state cleanly from a specified SQL backup file.

### Operational Commands:
```bash
# 1. Create a backup
./backend/scripts/backup_db.sh

# 2. Restore from a backup
./backend/scripts/restore_db.sh ./backups/fake_job_detector_backup_20260818_120000.sql.gz
```

---

## 7. Verification Summary

- **Backend Pytest Suite**: **145 / 145 PASSED (100%)**
  - 117 Baseline Tests
  - 21 Phase 17 E2E Tests
  - 7 Phase 18 Production Hardening Tests
- **Frontend Build**: **0 errors**, initial entry JS bundle **25.18 kB** (gzip: 7.51 kB) across 15 code-split chunks.
- **Python Compilation**: `python -m compileall app` succeeded with 0 compilation errors.
