# ==============================================================================
# SentinelJob AI — Production Root Dockerfile for Render Deployment
# Python 3.11-slim with Tesseract OCR & non-root execution
# ==============================================================================

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Install essential system dependencies, PostgreSQL client libraries, and Tesseract OCR engine
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    libpq5 \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY fake-job-detector/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser

# Copy application codebase and artifacts
COPY --chown=appuser:appgroup fake-job-detector/backend/app ./app
COPY --chown=appuser:appgroup fake-job-detector/backend/artifacts ./artifacts
COPY --chown=appuser:appgroup fake-job-detector/backend/alembic.ini ./alembic.ini
COPY --chown=appuser:appgroup fake-job-detector/backend/alembic ./alembic

# Switch to non-root user
USER appuser

# Expose HTTP ASGI service port
EXPOSE 8000

# Container Healthcheck
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production ASGI server launch
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
