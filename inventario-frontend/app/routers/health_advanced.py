"""
Health checks avanzados para producción.
"""
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.cache import cache_manager
from app.core.config import settings
from app.models.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def liveness_check() -> dict[str, Any]:
    """
    Liveness probe para Kubernetes/Docker.
    Verifica que la aplicación esté viva (no bloqueada).
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "inventario-backend",
    }


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Readiness probe para Kubernetes/Docker.
    Verifica que la aplicación esté lista para recibir tráfico.
    """
    checks: dict[str, Any] = {
        "database": False,
        "redis": False,
    }
    errors = []

    # Check Database
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency = round((time.time() - start) * 1000, 2)
        checks["database"] = True
        checks["database_latency_ms"] = db_latency
    except Exception as e:
        errors.append(f"Database: {str(e)}")
        checks["database_latency_ms"] = None

    # Check Redis (si está habilitado)
    redis_enabled = getattr(settings, "redis_enabled", False)
    if redis_enabled:
        try:
            start = time.time()
            cache_manager.set("health_check", "ok", ttl=10)
            result = cache_manager.get("health_check")
            redis_latency = round((time.time() - start) * 1000, 2)
            checks["redis"] = result == "ok"
            checks["redis_latency_ms"] = redis_latency
        except Exception as e:
            errors.append(f"Redis: {str(e)}")
            checks["redis_latency_ms"] = None
    else:
        checks["redis"] = True  # No requerido
        checks["redis_latency_ms"] = None

    # Determinar estado general
    all_healthy = checks["database"] and checks["redis"]
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if all_healthy else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "errors": errors if errors else None,
    }


@router.get("/startup", status_code=status.HTTP_200_OK)
async def startup_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Startup probe para Kubernetes.
    Verifica que la aplicación haya completado la inicialización.
    """
    checks: dict[str, Any] = {
        "database_connection": False,
        "database_migration": False,
    }
    errors = []

    # Check DB connection
    try:
        db.execute(text("SELECT 1"))
        checks["database_connection"] = True
    except Exception as e:
        errors.append(f"DB Connection: {str(e)}")

    # Check DB migrations (verifica tabla alembic_version)
    try:
        result = db.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
        version = result.scalar()
        checks["database_migration"] = version is not None
        checks["alembic_version"] = version
    except Exception as e:
        errors.append(f"DB Migration: {str(e)}")
        checks["alembic_version"] = None

    # Estado general
    all_ready = all(checks.values())
    status_code = status.HTTP_200_OK if all_ready else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "started" if all_ready else "starting",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks,
        "errors": errors if errors else None,
        "environment": settings.environment,
    }


@router.get("/detailed", response_model=dict)
def get_detailed_health(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Health check detallado con métricas del sistema.
    Incluye latencias, pool de conexiones, memoria, etc.
    """
    try:
        import psutil  # type: ignore[import-not-found]
    except ImportError:
        psutil = None  # type: ignore[assignment]

    checks: dict[str, Any] = {}
    process = None

    # Database
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        db_latency = round((time.time() - start) * 1000, 2)
        checks["database"] = {
            "status": "healthy",
            "latency_ms": db_latency,
            "pool_size": db.bind.pool.size(),  # type: ignore[union-attr]
            "pool_checked_in": db.bind.pool.checkedin(),  # type: ignore[union-attr]
            "pool_checked_out": db.bind.pool.checkedout(),  # type: ignore[union-attr]
            "pool_overflow": db.bind.pool.overflow(),  # type: ignore[union-attr]
        }
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # Redis
    if getattr(settings, "redis_enabled", False):  # type: ignore[arg-type]
        try:
            start = time.time()
            cache_manager.set("health_detailed", "ok", ttl=10)
            result = cache_manager.get("health_detailed")
            redis_latency = round((time.time() - start) * 1000, 2)
            checks["redis"] = {
                "status": "healthy" if result == "ok" else "unhealthy",
                "latency_ms": redis_latency,
            }
        except Exception as e:
            checks["redis"] = {"status": "unhealthy", "error": str(e)}

    # Sistema
    try:
        if psutil:
            process = psutil.Process()  # type: ignore[union-attr]
            memory_info = process.memory_info()
            checks["system"] = {
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
            }
    except Exception as e:
        checks["system"] = {"error": str(e)}

    # Uptime
    try:
        if psutil and process:
            checks["uptime_seconds"] = round(time.time() - process.create_time(), 2)  # type: ignore[union-attr]
    except Exception:
        checks["uptime_seconds"] = None

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": checks,
    }
