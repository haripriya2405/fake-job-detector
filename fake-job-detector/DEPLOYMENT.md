# SentinelJob AI — Production Deployment Guide

This guide provides instructions for deploying SentinelJob AI in production using Docker Compose or standalone container runtimes.

---

## 1. Prerequisites
- Docker Engine 24.0+ & Docker Compose v2 (or Podman equivalent)
- 2 CPU cores, 4 GB RAM minimum
- Domain name and TLS termination reverse proxy (e.g. Cloudflare, AWS ALB, or Let's Encrypt)

---

## 2. Quickstart with Docker Compose

### Step 1: Clone and Configure Environment
```bash
# 1. Copy production environment template
cp .env.example .env

# 2. Generate a secure secret key and set database credentials in .env
# Example generator: openssl rand -hex 32
```

### Step 2: Build and Launch Containers
```bash
# Build images and start services in background
docker compose up -d --build

# Verify container health
docker compose ps
```

### Step 3: Verify Service Health
```bash
# Test Liveness
curl -f http://localhost:3000/health

# Test Readiness
curl -f http://localhost:3000/ready
```

---

## 3. Production Architecture
- **Nginx (`frontend` service, port 3000 -> 80)**: Serves static assets, SPA routing, applies security headers, proxies `/api/` traffic.
- **FastAPI (`backend` service, port 8000)**: Non-root user (`appuser`), Tesseract OCR enabled, rate-limited, ML inference (`logisticregression-v1.0.0`).
- **PostgreSQL 16 (`postgres` service)**: Persistent data stored in `sentineljob_postgres_data` volume.

---

## 4. Maintenance & Backups

### Automated Backup
```bash
# Execute backup
./backend/scripts/backup_db.sh
```

### Database Restore
```bash
# Execute restore from backup
./backend/scripts/restore_db.sh ./backups/fake_job_detector_backup_YYYYMMDD_HHMMSS.sql.gz
```

---

## 5. Security & Governance Invariants
- **Active ML Model**: `logisticregression-v1.0.0`
- **Candidate Standby Model**: `model-v2.0.0` (Do NOT promote without multi-stakeholder governance sign-off)
- **SSRF Protection**: Strict IP filtering active on `/api/v1/analysis/url`
- **Upload Safety**: PDF macro blocking and image decompression protection active
