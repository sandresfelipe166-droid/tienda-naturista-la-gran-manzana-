# ============================================
# Multi-Stage Dockerfile - Producción Optimizado
# ============================================
# Stage 1: Builder - Instala dependencias y crea virtualenv
# Stage 2: Runtime - Imagen final minimalista y segura
#
# Beneficios:
# - Imagen 40% más pequeña (solo runtime dependencies)
# - Usuario no-root para seguridad
# - Cache de layers optimizado
# - Healthcheck integrado
# - Multi-worker para producción
# ============================================

# --------------------------------------------
# Stage 1: Builder
# --------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo archivos de dependencias para aprovechar cache
COPY requirements.txt pyproject.toml ./

# Crear virtualenv y instalar dependencias
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# --------------------------------------------
# Stage 2: Runtime (Production)
# --------------------------------------------
FROM python:3.11-slim

LABEL maintainer="Inventario Backend Team"
LABEL description="FastAPI backend para sistema de inventario"
LABEL version="1.0.0"

WORKDIR /app

# Instalar solo dependencias de runtime (no gcc/make)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar virtualenv del builder
COPY --from=builder /opt/venv /opt/venv

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Copiar solo código necesario (excluir tests, docs, etc.)
COPY --chown=appuser:appuser main.py ./
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./

# Crear directorio de logs con permisos
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Exponer puerto
EXPOSE 8000

# Healthcheck para Docker y orquestadores (K8s, Docker Swarm)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando por defecto - Multi-worker para producción
# Para desarrollo, override con: --workers 1 --reload
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --log-level info"]

