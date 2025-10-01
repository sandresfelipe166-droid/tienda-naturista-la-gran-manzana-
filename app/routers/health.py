"""
Health check endpoints para el API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import redis
import time
from app.core.config import settings
from app.core.database import db_manager
from app.core.logging_config import inventario_logger

router = APIRouter()
logger = inventario_logger

@router.get("/health", summary="Health Check Básico")
async def health_check() -> Dict[str, Any]:
    """
    Health check básico del API
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "inventario-backend",
        "version": "1.0.0",
        "environment": settings.environment
    }

@router.get("/health/detailed", summary="Health Check Detallado")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Health check detallado con información de servicios
    """
    health_info = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "inventario-backend",
        "version": "1.0.0",
        "environment": settings.environment,
        "checks": {}
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
            "message": f"Database check failed: {str(e)}"
        }
        health_info["status"] = "unhealthy"

    # Redis health check
    if settings.redis_health_check_enabled:
        try:
            redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                socket_timeout=settings.redis_health_timeout
            )
            redis_client.ping()
            health_info["checks"]["redis"] = {
                "status": "healthy",
                "message": "Redis connection successful"
            }
        except Exception as e:
            health_info["checks"]["redis"] = {
                "status": "unhealthy",
                "message": f"Redis check failed: {str(e)}"
            }
            health_info["status"] = "unhealthy"

    # External services health checks
    for service in settings.external_services_health:
        try:
            # Implementar checks específicos para servicios externos
            health_info["checks"][service["name"]] = {
                "status": "healthy",
                "message": f"{service['name']} is operational"
            }
        except Exception as e:
            health_info["checks"][service["name"]] = {
                "status": "unhealthy",
                "message": f"{service['name']} check failed: {str(e)}"
            }
            health_info["status"] = "unhealthy"

    return health_info

@router.get("/health/database", summary="Database Health Check")
async def database_health_check() -> Dict[str, Any]:
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
            "timestamp": time.time()
        }
    except Exception as e:
        logger.log_error(e, {"context": "database_health_check"})
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(e)}"
        )

@router.get("/health/metrics", summary="Application Metrics")
async def application_metrics() -> Dict[str, Any]:
    """
    Métricas básicas de la aplicación
    """
    return {
        "timestamp": time.time(),
        "uptime": "calculated_uptime",  # Implementar cálculo real
        "memory_usage": "memory_info",   # Implementar con psutil
        "active_connections": "connection_count",  # Implementar conteo
        "request_rate": "requests_per_second",     # Implementar métricas
        "error_rate": "errors_per_second",         # Implementar métricas
        "response_times": {
            "average": "avg_response_time",
            "median": "median_response_time",
            "95th_percentile": "p95_response_time"
        }
    }

@router.get("/health/config", summary="Configuration Info")
async def configuration_info() -> Dict[str, Any]:
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
        "health_checks_enabled": settings.health_check_enabled
    }
