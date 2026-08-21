# ==============================================================================
# FORENZA: Forensic Evidence Operating System
# Backend Microservices Engine - Multi-Stage Air-Gapped Production Dockerfile
# ==============================================================================

# --- Stage 1: Build Dependencies ---
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r requirements.txt

# --- Stage 2: Final Production Runtime ---
FROM python:3.12-slim-bookworm AS runner

LABEL maintainer="FORENZA Biocomputational Intelligence Team <forenza@yusufcalisir.dev>"
LABEL description="FORENZA Air-Gapped Biocomputational Forensic Intelligence Engine"
LABEL version="2.0.0"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/backend:/app" \
    PORT=8000 \
    AIRGAP_MODE=true \
    OFFLINE_SIMULATION=true

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root unprivileged service user
RUN groupadd -g 10001 forenza && \
    useradd -u 10001 -g forenza -s /bin/bash -m forenza

# Copy python virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy backend codebase and research datasets
COPY --chown=forenza:forenza backend /app/backend
COPY --chown=forenza:forenza research /app/research

# Switch to unprivileged user
USER forenza

WORKDIR /app/backend

# Expose internal service port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=20s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Start production uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--access-log"]
