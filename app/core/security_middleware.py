"""
Middleware de seguridad avanzada para el API
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import secrets
import time
from typing import Dict, Any
from app.core.config import settings
from app.core.logging_config import inventario_logger
from app.core.exceptions import SecurityException

logger = inventario_logger

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = settings.security_headers.copy()

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Agregar headers de seguridad
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value

        # Headers adicionales específicos
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Headers de información
        response.headers["X-Powered-By"] = "Inventario-Backend"
        response.headers["X-Environment"] = settings.environment

        return response

class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware para protección CSRF"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.csrf_secret = settings.csrf_secret
        self.csrf_token_expire = settings.csrf_token_expire_minutes * 60

    async def dispatch(self, request: Request, call_next) -> Response:
        # Solo aplicar CSRF a métodos que modifican estado
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Verificar token CSRF para requests que no son API
            if not request.url.path.startswith("/api/"):
                csrf_token = request.headers.get("X-CSRF-Token")
                if not csrf_token:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF token missing"}
                    )

                # Validar token (simplificado - en producción usar validación real)
                if not self._validate_csrf_token(csrf_token):
                    logger.log_security_event(
                        "csrf_token_invalid",
                        ip_address=request.client.host if request.client else "unknown",
                        path=request.url.path
                    )
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF token invalid"}
                    )

        response = await call_next(request)

        # Agregar token CSRF a responses si es necesario
        if request.method == "GET" and not request.url.path.startswith("/api/"):
            new_token = self._generate_csrf_token()
            response.set_cookie(
                "csrf_token",
                new_token,
                httponly=False,
                secure=settings.session_cookie_secure,
                samesite=settings.session_cookie_samesite
            )

        return response

    def _generate_csrf_token(self) -> str:
        """Generar token CSRF"""
        return secrets.token_urlsafe(32)

    def _validate_csrf_token(self, token: str) -> bool:
        """Validar token CSRF (simplificado)"""
        # En producción, implementar validación real con timestamp y firma
        return len(token) >= 32 and token.isalnum()

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware para validación de API Key"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Solo validar API key si está habilitada
        if settings.api_key_enabled:
            api_key = request.headers.get("X-API-Key")
            if not api_key or api_key != settings.api_key_secret:
                logger.log_security_event(
                    "api_key_invalid",
                    ip_address=request.client.host if request.client else "unknown",
                    path=request.url.path
                )
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid API key"}
                )

        return await call_next(request)

class SecurityEventLogger(BaseHTTPMiddleware):
    """Middleware para logging de eventos de seguridad"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Log de solicitud
        logger.log_request(
            method=request.method,
            path=request.url.path,
            user_id=getattr(request.state, 'user_id', None),
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("User-Agent", "")
        )

        response = await call_next(request)

        # Calcular tiempo de respuesta
        duration = time.time() - start_time

        # Log de respuesta si es lenta o error
        if duration > 5.0 or response.status_code >= 400:
            logger.log_business_event(
                "slow_or_error_response",
                {
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration": duration,
                    "ip_address": request.client.host if request.client else "unknown"
                }
            )

        return response

class SecurityException(Exception):
    """Excepción personalizada para errores de seguridad"""
    pass
