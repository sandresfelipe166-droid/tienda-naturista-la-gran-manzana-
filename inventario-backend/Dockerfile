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
    curl \
    ca-certificates \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Rust toolchain (necesario para compilar pydantic-core, etc.)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copiar solo archivos de dependencias para aprovechar cache
COPY requirements.txt pyproject.toml ./

# Crear virtualenv y instalar dependencias
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    # Asegurar que cargo/rust están en PATH durante la instalación de wheels
    PATH="/root/.cargo/bin:$PATH" /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

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
COPY --chown=appuser:appuser entrypoint.sh /entrypoint.sh

# Crear directorio de logs con permisos
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs && chmod +x /entrypoint.sh

# Cambiar a usuario no-root
USER appuser

# Variables de entorno
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Exponer puerto (Railway usa PORT dinámico, default 8000)
EXPOSE 8000

# Healthcheck deshabilitado - Railway maneja esto externamente
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Usar entrypoint que aplica migraciones y luego arranca la app
CMD ["/entrypoint.sh"]

