# Root Dockerfile (copia temporal) - permite a Render localizar un Dockerfile
# Este archivo es una copia del Dockerfile del backend para evitar errores de lookup
# Se puede eliminar una vez que Render builde correctamente usando el `render.yaml`.

FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY inventario-backend/requirements.txt inventario-backend/pyproject.toml ./

RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

LABEL maintainer="Inventario Backend Team"
LABEL description="FastAPI backend para sistema de inventario"
LABEL version="1.0.0"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser inventario-backend/main.py ./
COPY --chown=appuser:appuser inventario-backend/app/ ./app/
COPY --chown=appuser:appuser inventario-backend/alembic/ ./alembic/
COPY --chown=appuser:appuser inventario-backend/alembic.ini ./

RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

USER appuser

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
