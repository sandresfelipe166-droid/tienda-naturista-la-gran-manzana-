"""
Router para exponer métricas de circuit breakers y rate limiting.

Endpoints para monitoreo y diagnóstico de resiliencia.
"""
from fastapi import APIRouter, Depends

from app.core.circuit_breaker import CircuitBreaker
from app.core.user_rate_limiter import user_rate_limiter

router = APIRouter()


@router.get("/circuit-breakers")
async def get_circuit_breakers_status():
    """
    Obtener estado de todos los circuit breakers.
    
    Útil para:
    - Monitoreo de salud de servicios externos
    - Diagnóstico de problemas de conectividad
    - Dashboards de observabilidad
    """
    return {
        "circuit_breakers": CircuitBreaker.get_all_states(),
        "total_services": len(CircuitBreaker._instances),
    }


@router.get("/circuit-breakers/{service_name}")
async def get_circuit_breaker_status(service_name: str):
    """
    Obtener estado de un circuit breaker específico.
    
    Args:
        service_name: Nombre del servicio (email_service, redis_service, external_api)
    """
    cb = CircuitBreaker.get_instance(service_name)
    
    if not cb:
        return {
            "error": f"Circuit breaker no encontrado: {service_name}",
            "available_services": list(CircuitBreaker._instances.keys())
        }
    
    return {
        "service_name": service_name,
        **cb.get_state_info()
    }


@router.get("/rate-limit/user/{user_id}")
async def get_user_rate_limit_usage(user_id: int):
    """
    Obtener estadísticas de rate limiting para un usuario.
    
    Args:
        user_id: ID del usuario
    """
    return user_rate_limiter.get_user_usage(user_id)
