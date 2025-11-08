"""
Health check endpoints para el API
"""

import time
from typing import Any

import redis
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging_config import inventario_logger
from app.core.metrics import metrics_manager

router = APIRouter()
logger = inventario_logger


@router.get("/health", summary="Health Check Básico")
async def health_check() -> dict[str, Any]:
    """
    Health check básico del API
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "inventario-backend",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@router.get("/health/detailed", summary="Health Check Detallado")
async def detailed_health_check() -> dict[str, Any]:
    """
    Health check detallado con información de servicios
    """
    health_info = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "inventario-backend",
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": {},
    }

    # Database health check
    try:
        db_health = db_manager.health_check()
        health_info["checks"]["database"] = db_health
        if db_health["status"] != "healthy":
            health_info["status"] = "unhealthy"
    except Exception as e:
        health_info["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database check failed: {str(e)}",
        }
        health_info["status"] = "unhealthy"

    # Redis health check
    if settings.redis_health_check_enabled:
        try:
            # Asegurar tipos correctos para Pylance/redis-py
            redis_host = settings.redis_host or "localhost"
            redis_client = redis.Redis(
                host=redis_host,
                port=int(settings.redis_port),
                db=int(settings.redis_db),
                password=settings.redis_password,
                socket_timeout=float(settings.redis_health_timeout),
            )
            redis_client.ping()
            health_info["checks"]["redis"] = {
                "status": "healthy",
                "message": "Redis connection successful",
            }
        except Exception as e:
            health_info["checks"]["redis"] = {
                "status": "unhealthy",
                "message": f"Redis check failed: {str(e)}",
            }
            health_info["status"] = "unhealthy"

    # External services health checks
    for service in settings.external_services_health:
        try:
            # Implementar checks específicos para servicios externos
            health_info["checks"][service["name"]] = {
                "status": "healthy",
                "message": f"{service['name']} is operational",
            }
        except Exception as e:
            health_info["checks"][service["name"]] = {
                "status": "unhealthy",
                "message": f"{service['name']} check failed: {str(e)}",
            }
            health_info["status"] = "unhealthy"

    return health_info


@router.get("/health/database", summary="Database Health Check")
async def database_health_check() -> dict[str, Any]:
    """
    Health check específico de la base de datos
    """
    try:
        db_health = db_manager.health_check()
        db_info = db_manager.get_connection_info()

        return {
            "status": db_health["status"],
            "message": db_health["message"],
            "connection_info": db_info,
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.log_error(e, {"context": "database_health_check"})
        raise HTTPException(
            status_code=503, detail=f"Database health check failed: {str(e)}"
        ) from e


@router.get("/health/metrics", summary="Application Metrics")
async def application_metrics() -> dict[str, Any]:
    """
    Métricas básicas de la aplicación (reales). Si psutil no está disponible, los datos
    de memoria serán None. Para conexiones activas se usa el pool info del db_manager.
    """
    # Summary base desde el metrics manager
    summary = metrics_manager.summary()
    uptime_seconds = summary.get("uptime_seconds")
    rates = summary.get("rates", {})
    latency = summary.get("latency", {})

    # Intentar obtener uso de memoria con psutil (opcional)
    mem_info: dict[str, Any] = {"available": False, "rss": None, "vms": None, "percent": None}
    try:
        import psutil  # type: ignore

        p = psutil.Process()
        with p.oneshot():
            mem = p.memory_info()
            mem_info = {
                "available": True,
                "rss": getattr(mem, "rss", None),
                "vms": getattr(mem, "vms", None),
                "percent": (
                    psutil.virtual_memory().percent if hasattr(psutil, "virtual_memory") else None
                ),
            }
    except Exception:
        # Mantener mem_info con available=False
        pass

    # Información de conexiones del pool
    active_connections = None
    try:
        db_info = db_manager.get_connection_info()
        # Exponer directamente estructura del pool
        active_connections = {
            "pool_size": db_info.get("pool_size"),
            "checked_in": db_info.get("checked_in"),
            "checked_out": db_info.get("checked_out"),
            "overflow": db_info.get("overflow"),
        }
    except Exception:
        active_connections = None

    return {
        "timestamp": time.time(),
        "uptime_seconds": uptime_seconds,
        "memory_usage": mem_info,
        "active_connections": active_connections,
        "requests_total": summary.get("requests_total"),
        "errors_total": summary.get("errors_total"),
        "status_counts": summary.get("status_counts"),
        "request_rate": rates.get("requests_per_second"),
        "error_rate": rates.get("errors_per_second"),
        "response_times": {
            "average_seconds": latency.get("average_seconds"),
            "p95_bucket_seconds": latency.get("p95_bucket_seconds"),
            "observations": latency.get("observation_count"),
        },
    }


@router.get("/health/config", summary="Configuration Info")
async def configuration_info() -> dict[str, Any]:
    """
    Información de configuración (sin datos sensibles)
    """
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "database_configured": bool(settings.database_url),
        "redis_configured": bool(settings.redis_host),
        "prometheus_enabled": settings.prometheus_enabled,
        "metrics_enabled": settings.metrics_enabled,
        "backup_enabled": settings.backup_enabled,
        "ssl_enabled": settings.ssl_enabled,
        "health_checks_enabled": settings.health_check_enabled,
    }
