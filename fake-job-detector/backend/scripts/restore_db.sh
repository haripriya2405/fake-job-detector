#!/usr/bin/env bash
# ==============================================================================
# SentinelJob AI — PostgreSQL Automated Database Restore Script (Phase 18)
# ==============================================================================
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path_to_backup_file.sql.gz>" >&2
    exit 1
fi

BACKUP_FILE="$1"
CONTAINER_NAME="${CONTAINER_NAME:-sentineljob-postgres}"
DB_NAME="${POSTGRES_DB:-fake_job_detector}"
DB_USER="${POSTGRES_USER:-postgres}"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "[ERROR] Backup file not found: ${BACKUP_FILE}" >&2
    exit 1
fi

echo "[INFO] Restoring database '${DB_NAME}' from backup: ${BACKUP_FILE}..."

if command -v docker >/dev/null 2>&1 && docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "[INFO] Executing restore inside container '${CONTAINER_NAME}'..."
    gunzip -c "${BACKUP_FILE}" | docker exec -i "${CONTAINER_NAME}" psql -U "${DB_USER}" -d "${DB_NAME}"
else
    echo "[INFO] Executing local psql restore..."
    gunzip -c "${BACKUP_FILE}" | psql -U "${DB_USER}" -d "${DB_NAME}"
fi

echo "[SUCCESS] Database restoration completed successfully from: ${BACKUP_FILE}"
