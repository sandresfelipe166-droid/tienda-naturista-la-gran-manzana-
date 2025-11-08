"""
Middleware de seguridad avanzada para el API
"""

import secrets
import string
import time
from typing import Literal, cast

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.csrf import generate_csrf_token, validate_csrf_token
from app.core.logging_config import inventario_logger

logger = inventario_logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = settings.security_headers.copy()

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Agregar headers de seguridad (sin sobrescribir si ya existen)
        for header_name, header_value in self.security_headers.items():
            if header_name not in response.headers:
                response.headers[header_name] = header_value

        # Compatibilidad: asegurar headers comunes si no están presentes desde settings
        defaults = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "no-referrer-when-downgrade",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }
        for k, v in defaults.items():
            if k not in response.headers:
                response.headers[k] = v

        # Headers de información
        if getattr(settings, "send_x_powered_by", True):
            response.headers["X-Powered-By"] = getattr(
                settings, "powered_by_header", "Inventario-Backend"
            )
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
                # Prefer header, fallback to cookie
                csrf_token = request.headers.get("X-CSRF-Token") or request.cookies.get(
                    "csrf_token"
                )
                if not csrf_token:
                    return JSONResponse(status_code=403, content={"detail": "CSRF token missing"})

                valid, ts = validate_csrf_token(csrf_token)
                if not valid:
                    logger.log_security_event(
                        "csrf_token_invalid",
                        ip_address=request.client.host if request.client else "unknown",
                        path=request.url.path,
                        request_id=getattr(request.state, "request_id", None),
                    )
                    return JSONResponse(
                        status_code=403, content={"detail": "CSRF token invalid or expired"}
                    )

        response = await call_next(request)

        # Agregar token CSRF a responses si es necesario (para clientes web)
        if request.method == "GET" and not request.url.path.startswith("/api/"):
            new_token = generate_csrf_token()
            # Normalizar samesite a valores admitidos por Starlette ('lax'|'strict'|'none')
            samesite_raw = str(getattr(settings, "session_cookie_samesite", "lax")).lower()
            if samesite_raw not in ("lax", "strict", "none"):
                samesite_raw = "lax"
            response.set_cookie(
                "csrf_token",
                new_token,
                httponly=False,
                secure=bool(getattr(settings, "session_cookie_secure", True)),
                samesite=cast(Literal["lax", "strict", "none"], samesite_raw),
            )
            # También enviar en header para SPAs que lean XHR
            response.headers["X-CSRF-Token"] = new_token

        return response

    def _generate_csrf_token(self) -> str:
        """Generar token CSRF"""
        return secrets.token_urlsafe(32)

    def _validate_csrf_token(self, token: str) -> bool:
        """Validar token CSRF (simplificado) compatible con token_urlsafe"""
        # En producción, implementar validación real con timestamp y firma
        if not token or len(token) < 32:
            return False
        allowed = set(string.ascii_letters + string.digits + "-_")
        return all(c in allowed for c in token)


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
                    path=request.url.path,
                    request_id=getattr(request.state, 'request_id', None),
                )
                return JSONResponse(status_code=401, content={"detail": "Invalid API key"})

        return await call_next(request)


class SecurityEventLogger(BaseHTTPMiddleware):
    """Middleware para logging de eventos de seguridad"""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Log de solicitud
        # Tipado seguro para Pylance: user_id como int y request_id como str
        _user_id_val = getattr(request.state, "user_id", None)
        user_id_int = _user_id_val if isinstance(_user_id_val, int) else 0
        request_id_str = (
            str(getattr(request.state, "request_id", ""))
            if getattr(request.state, "request_id", None)
            else ""
        )
        logger.log_request(
            method=request.method,
            path=request.url.path,
            user_id=user_id_int,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("User-Agent", ""),
            request_id=request_id_str,
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
                    "ip_address": request.client.host if request.client else "unknown",
                    "request_id": request_id_str,
                },
            )

        return response
