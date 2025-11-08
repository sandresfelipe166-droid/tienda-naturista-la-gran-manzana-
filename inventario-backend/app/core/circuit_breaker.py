"""
Circuit Breaker Pattern para proteger contra fallos en cascada.

Implementa el patrón Circuit Breaker para servicios externos:
- Estado CLOSED: Operación normal
- Estado OPEN: Servicio caído, fallar rápido
- Estado HALF_OPEN: Probando recuperación

ROI: Reduce latencia en fallos de 30s → 100ms, evita saturación del sistema.
"""
import asyncio
import time
from collections import defaultdict
from enum import Enum
from functools import wraps
from typing import Any, Callable

from app.core.exceptions import InventarioException


class CircuitState(str, Enum):
    """Estados del Circuit Breaker"""
    CLOSED = "closed"  # Funcionamiento normal
    OPEN = "open"  # Servicio caído, rechazar inmediatamente
    HALF_OPEN = "half_open"  # Probando recuperación


class CircuitBreakerOpenError(InventarioException):
    """Error cuando el circuit breaker está abierto"""
    def __init__(self, service_name: str):
        super().__init__(
            message=f"Circuit breaker abierto para servicio: {service_name}",
            status_code=503,
            error_code="CIRCUIT_BREAKER_OPEN"
        )


class CircuitBreaker:
    """
    Circuit Breaker para proteger contra fallos en cascada.
    
    Ejemplo de uso:
        cb = CircuitBreaker("external_api", failure_threshold=5, recovery_timeout=60)
        
        @cb.call
        async def make_external_call():
            response = await httpx.get("https://api.example.com")
            return response.json()
    """
    
    # Diccionario global de circuit breakers por nombre
    _instances: dict[str, "CircuitBreaker"] = {}
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,  # Fallos antes de abrir
        recovery_timeout: int = 60,  # Segundos antes de probar recuperación
        success_threshold: int = 2,  # Éxitos necesarios para cerrar desde HALF_OPEN
        timeout: float = 30.0,  # Timeout por operación (segundos)
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        # Estado interno
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.last_state_change = time.time()
        
        # Métricas
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_timeouts = 0
        self.total_rejections = 0  # Llamadas rechazadas por estar OPEN
        
        # Registrar instancia
        CircuitBreaker._instances[name] = self
    
    @classmethod
    def get_instance(cls, name: str) -> "CircuitBreaker | None":
        """Obtener instancia existente por nombre"""
        return cls._instances.get(name)
    
    @classmethod
    def get_all_states(cls) -> dict[str, dict[str, Any]]:
        """Obtener estado de todos los circuit breakers"""
        return {
            name: cb.get_state_info()
            for name, cb in cls._instances.items()
        }
    
    def get_state_info(self) -> dict[str, Any]:
        """Obtener información del estado actual"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "total_timeouts": self.total_timeouts,
            "total_rejections": self.total_rejections,
            "last_state_change": self.last_state_change,
            "uptime_seconds": time.time() - self.last_state_change,
            "failure_rate": (
                self.total_failures / self.total_calls
                if self.total_calls > 0 else 0.0
            ),
        }
    
    def _should_attempt_reset(self) -> bool:
        """Verificar si es momento de intentar recuperación"""
        if self.state != CircuitState.OPEN:
            return False
        
        if self.last_failure_time is None:
            return False
        
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _record_success(self):
        """Registrar éxito"""
        self.total_calls += 1
        self.total_successes += 1
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close()
    
    def _record_failure(self):
        """Registrar fallo"""
        self.total_calls += 1
        self.total_failures += 1
        self.failure_count += 1
        self.success_count = 0
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self._open()
        elif self.failure_count >= self.failure_threshold:
            self._open()
    
    def _open(self):
        """Abrir circuit breaker"""
        if self.state != CircuitState.OPEN:
            self.state = CircuitState.OPEN
            self.last_state_change = time.time()
    
    def _close(self):
        """Cerrar circuit breaker"""
        if self.state != CircuitState.CLOSED:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_state_change = time.time()
    
    def _half_open(self):
        """Poner en modo HALF_OPEN"""
        if self.state != CircuitState.HALF_OPEN:
            self.state = CircuitState.HALF_OPEN
            self.success_count = 0
            self.last_state_change = time.time()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecutar función protegida por circuit breaker.
        
        Args:
            func: Función async a ejecutar
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la función
            
        Raises:
            CircuitBreakerOpenError: Si el circuit breaker está abierto
            asyncio.TimeoutError: Si la operación excede el timeout
        """
        # Verificar si debemos intentar recuperación
        if self._should_attempt_reset():
            self._half_open()
        
        # Rechazar si está abierto
        if self.state == CircuitState.OPEN:
            self.total_rejections += 1
            raise CircuitBreakerOpenError(self.name)
        
        # Ejecutar con timeout
        try:
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout
            )
            self._record_success()
            return result
        
        except asyncio.TimeoutError:
            self.total_timeouts += 1
            self._record_failure()
            raise
        
        except Exception as e:
            self._record_failure()
            raise e
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorador para funciones async.
        
        Ejemplo:
            cb = CircuitBreaker("my_service")
            
            @cb
            async def my_function():
                return await external_call()
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        
        return wrapper


# Instancias pre-configuradas para servicios comunes
email_circuit_breaker = CircuitBreaker(
    name="email_service",
    failure_threshold=3,
    recovery_timeout=120,  # 2 minutos
    timeout=10.0,
)

redis_circuit_breaker = CircuitBreaker(
    name="redis_service",
    failure_threshold=5,
    recovery_timeout=30,  # 30 segundos
    timeout=2.0,
)

external_api_circuit_breaker = CircuitBreaker(
    name="external_api",
    failure_threshold=5,
    recovery_timeout=60,
    timeout=30.0,
)
