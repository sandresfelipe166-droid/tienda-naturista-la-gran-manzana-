"""
Sistema de rate limiting avanzado para el API
"""

import asyncio
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.exceptions import RateLimitException
from app.core.logging_config import inventario_logger

logger = inventario_logger

# Try to import Redis adapter; it's optional and used when settings.rate_limit_use_redis is True
try:
    from app.core.rate_limiter_redis import RedisRateLimiter  # type: ignore
except Exception:
    RedisRateLimiter = None


class InMemoryRateLimiter:
    """Rate limiter en memoria usando sliding window"""

    def __init__(self):
        self.requests: dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Verificar si la solicitud está permitida"""
        async with self.lock:
            now = time.time()
            window_start = now - window

            # Limpiar solicitudes fuera de la ventana
            while self.requests[key] and self.requests[key][0] <= window_start:
                self.requests[key].popleft()

            # Verificar si se excede el límite
            if len(self.requests[key]) >= limit:
                return False

            # Agregar la solicitud actual
            self.requests[key].append(now)
            return True

    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Obtener solicitudes restantes"""
        async with self.lock:
            now = time.time()
            window_start = now - window

            # Limpiar solicitudes fuera de la ventana
            while self.requests[key] and self.requests[key][0] <= window_start:
                self.requests[key].popleft()

            return max(0, limit - len(self.requests[key]))

    async def get_reset_time(self, key: str, window: int) -> datetime | None:
        """Obtener tiempo de reset de la ventana"""
        async with self.lock:
            if not self.requests[key]:
                return None

            oldest_request = self.requests[key][0]
            reset_time = datetime.fromtimestamp(oldest_request + window)
            return reset_time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting avanzado"""

    def __init__(self, app, limiter: InMemoryRateLimiter | None = None):
        super().__init__(app)
        # Choose limiter based on settings: Redis if enabled and available, else provided limiter or in-memory
        if getattr(settings, "rate_limit_use_redis", False) and RedisRateLimiter is not None:
            # Create a simple async wrapper that forwards to Redis-based limiter
            self._redis_limiter: Any | None = RedisRateLimiter()
            self.limiter: InMemoryRateLimiter | None = None
        else:
            self._redis_limiter: Any | None = None
            self.limiter: InMemoryRateLimiter | None = limiter or InMemoryRateLimiter()
        self.default_limit = settings.rate_limit_requests
        self.default_window = settings.rate_limit_window

        # Configuración específica por endpoint desde settings
        self.endpoint_limits = settings.endpoint_rate_limits

        # Configuración adicional por método HTTP
        self.method_limits = {
            "GET": {"limit": 200, "window": 60},  # Más permisivo para lectura
            "POST": {"limit": 50, "window": 60},  # Moderado para creación
            "PUT": {"limit": 30, "window": 60},  # Moderado para actualización
            "DELETE": {"limit": 10, "window": 60},  # Restrictivo para eliminación
            "PATCH": {"limit": 20, "window": 60},  # Moderado para parches
        }

    def get_client_identifier(self, request: Request) -> str:
        """Obtener identificador único del cliente"""
        # Priorizar IP real si está detrás de proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        # Incluir user agent para mayor granularidad
        user_agent = request.headers.get("User-Agent", "")[:50]  # Limitar longitud

        return f"{client_ip}:{hash(user_agent)}"

    def get_rate_limit_config(self, path: str, method: str = "GET") -> dict[str, int]:
        """Obtener configuración de rate limit para un path y método"""
        # Buscar configuración específica por endpoint
        for endpoint, method_configs in self.endpoint_limits.items():
            if path.startswith(endpoint):
                # method_configs expected to be a mapping from HTTP method to config dict
                candidate = method_configs.get(method) if isinstance(method_configs, dict) else None
                if isinstance(candidate, dict):
                    return candidate  # type: ignore[return-value]
                else:
                    # Fallback a configuración por método HTTP si existe
                    if method in self.method_limits:
                        return self.method_limits[method]
                    # Si el método no está configurado, usar por defecto global
                    return {"limit": self.default_limit, "window": self.default_window}

        # Fallback a configuración por método HTTP si no hay match de endpoint
        if method in self.method_limits:
            return self.method_limits[method]

        # Usar configuración por defecto global
        return {"limit": self.default_limit, "window": self.default_window}

    async def dispatch(self, request: Request, call_next) -> Response:
        """Procesar solicitud con rate limiting"""

        # Obtener identificador del cliente
        client_id = self.get_client_identifier(request)

        # Obtener configuración de rate limit
        config = self.get_rate_limit_config(request.url.path, request.method)
        limit = config["limit"]
        window = config["window"]

        # Crear clave única para el rate limit
        rate_limit_key = f"{client_id}:{request.url.path}"

        try:
            # Verificar si la solicitud está permitida (Redis o InMemory)
            if self._redis_limiter is not None:
                is_allowed = await self._redis_limiter.is_allowed(rate_limit_key, limit, window)
            else:
                assert self.limiter is not None
                is_allowed = await self.limiter.is_allowed(rate_limit_key, limit, window)

            if not is_allowed:
                # Log del evento de rate limiting
                logger.log_security_event(
                    event="rate_limit_exceeded",
                    ip_address=client_id.split(":")[0],
                    path=request.url.path,
                    limit=limit,
                    window=window,
                )

                # Obtener información adicional para headers
                if self._redis_limiter is not None:
                    remaining = await self._redis_limiter.get_remaining(
                        rate_limit_key, limit, window
                    )
                    reset_time = await self._redis_limiter.get_reset_time(rate_limit_key, window)
                else:
                    assert self.limiter is not None
                    remaining = await self.limiter.get_remaining(rate_limit_key, limit, window)
                    reset_time = await self.limiter.get_reset_time(rate_limit_key, window)

                # Crear respuesta de error
                raise RateLimitException(limit, window)

            # Procesar solicitud
            response = await call_next(request)

            # Agregar headers de rate limiting
            if self._redis_limiter is not None:
                remaining = await self._redis_limiter.get_remaining(rate_limit_key, limit, window)
                reset_time = await self._redis_limiter.get_reset_time(rate_limit_key, window)
            else:
                assert self.limiter is not None
                remaining = await self.limiter.get_remaining(rate_limit_key, limit, window)
                reset_time = await self.limiter.get_reset_time(rate_limit_key, window)

            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = str(window)

            if reset_time:
                response.headers["X-RateLimit-Reset"] = reset_time.isoformat()

            return response

        except RateLimitException:
            # Re-lanzar excepción de rate limit
            raise
        except Exception as e:
            # Log de errores inesperados
            logger.log_error(
                e,
                {
                    "middleware": "RateLimitMiddleware",
                    "client_id": client_id,
                    "path": request.url.path,
                },
            )
            # Continuar con la solicitud en caso de error del rate limiter
            return await call_next(request)


class RateLimitDecorator:
    """Decorador para aplicar rate limiting a endpoints específicos"""

    def __init__(self, limit: int, window: int, per: str = "ip"):
        self.limit = limit
        self.window = window
        self.per = per  # "ip", "user", "ip_and_user"
        self.limiter = InMemoryRateLimiter()

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Obtener request del contexto
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # Si no hay request, ejecutar sin rate limiting
                return await func(*args, **kwargs)

            # Crear clave según el tipo de rate limiting
            if self.per == "ip":
                key = request.client.host if request.client else "unknown"
            elif self.per == "user":
                # Implementar lógica para obtener user_id del token
                key = "user_based"  # Placeholder
            else:  # ip_and_user
                ip = request.client.host if request.client else "unknown"
                key = f"{ip}:user_based"  # Placeholder

            # Verificar rate limit
            is_allowed = await self.limiter.is_allowed(key, self.limit, self.window)

            if not is_allowed:
                raise RateLimitException(self.limit, self.window)

            return await func(*args, **kwargs)

        return wrapper


# Instancia global del rate limiter
rate_limiter = InMemoryRateLimiter()


def rate_limit(limit: int, window: int, per: str = "ip"):
    """Decorador de rate limiting"""
    return RateLimitDecorator(limit, window, per)
