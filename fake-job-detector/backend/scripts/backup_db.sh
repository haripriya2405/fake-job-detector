#!/usr/bin/env bash
# ==============================================================================
# SentinelJob AI — PostgreSQL Automated Database Backup Script (Phase 18)
# ==============================================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="${CONTAINER_NAME:-sentineljob-postgres}"
DB_NAME="${POSTGRES_DB:-fake_job_detector}"
DB_USER="${POSTGRES_USER:-postgres}"
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[INFO] Starting database backup for '${DB_NAME}' from container '${CONTAINER_NAME}'..."

if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Executing pg_dump inside container '${CONTAINER_NAME}'..."
    docker exec -t "${CONTAINER_NAME}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists --no-owner | gzip > "${BACKUP_FILE}"
else
    echo "[INFO] Container not detected. Attempting local pg_dump..."
    pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists --no-owner | gzip > "${BACKUP_FILE}"
fi

# Verify backup integrity
if [ -s "${BACKUP_FILE}" ]; then
    SIZE_KB=$(du -k "${BACKUP_FILE}" | cut -f1)
    echo "[SUCCESS] Database backup completed successfully: ${BACKUP_FILE} (${SIZE_KB} KB)"
else
    echo "[ERROR] Backup file is empty or missing: ${BACKUP_FILE}" >&2
    exit 1
fi
