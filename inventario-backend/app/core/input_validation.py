"""
Middleware de validación de entrada para proteger contra ataques comunes
"""

import re
from typing import Any
from urllib.parse import unquote

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.exceptions import ValidationException
from app.core.logging_config import inventario_logger

logger = inventario_logger


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware para validar entradas y prevenir ataques comunes"""

    def __init__(self, app, exclude_paths: list[str] | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json"]

        # Patrones de ataque comunes
        self.sql_injection_patterns = [
            r';\s*--',  # Comentarios SQL
            r';\s*/\*',  # Comentarios multilinea
            r'union\s+select',  # UNION SELECT
            r'exec\s*\(',  # EXEC
            r'xp_cmdshell',  # XP_CMDSHELL
            r'1=1',  # Condición siempre verdadera
            r'\'\s*or\s*\'',  # OR con comillas
            r'--',  # Comentarios
            r'/\*',  # Comentarios multilinea
        ]

        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',  # Scripts
            r'javascript:',  # JavaScript URLs
            r'on\w+\s*=',  # Event handlers
            r'<iframe[^>]*>.*?</iframe>',  # Iframes
            r'<object[^>]*>.*?</object>',  # Objects
            r'<embed[^>]*>.*?</embed>',  # Embeds
            r'eval\s*\(',  # Eval
            r'document\.cookie',  # Cookie access
            r'document\.location',  # Location manipulation
        ]

        self.path_traversal_patterns = [
            r'\.\./',  # Directory traversal
            r'\.\.\\',  # Windows directory traversal
            r'%2e%2e%2f',  # URL encoded ../
            r'%2e%2e%5c',  # URL encoded ..\
        ]

        self.command_injection_patterns = [
            r';\s*rm\s',  # Remove commands
            r';\s*del\s',  # Delete commands
            r';\s*format\s',  # Format commands
            r'&&\s*rm\s',  # Chained remove
            r'&&\s*del\s',  # Chained delete
            r'\|\s*rm\s',  # Piped remove
            r'\|\s*del\s',  # Piped delete
        ]

    def _check_patterns(self, value: str, patterns: list[str], attack_type: str) -> list[str]:
        """Verificar si un valor contiene patrones de ataque"""
        violations = []
        value_lower = value.lower()

        for pattern in patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                violations.append(f"Patrón detectado: {pattern}")

        return violations

    def _validate_value(self, value: Any, field_name: str = "") -> list[str]:
        """Validar un valor individual"""
        violations = []

        if isinstance(value, str):
            # Verificar longitud máxima razonable
            if len(value) > 10000:  # 10KB máximo
                violations.append(f"Campo '{field_name}' excede longitud máxima (10000 caracteres)")

            # Verificar caracteres de control
            if any(ord(c) < 32 and c not in '\t\n\r' for c in value):
                violations.append(
                    f"Campo '{field_name}' contiene caracteres de control no permitidos"
                )

            # Verificar patrones de ataque
            sql_violations = self._check_patterns(
                value, self.sql_injection_patterns, "SQL Injection"
            )
            violations.extend(sql_violations)

            xss_violations = self._check_patterns(value, self.xss_patterns, "XSS")
            violations.extend(xss_violations)

            traversal_violations = self._check_patterns(
                value, self.path_traversal_patterns, "Path Traversal"
            )
            violations.extend(traversal_violations)

            cmd_violations = self._check_patterns(
                value, self.command_injection_patterns, "Command Injection"
            )
            violations.extend(cmd_violations)

        # Use tuple for runtime isinstance; keep tuple and silence Ruff suggestion
        elif isinstance(value, (list, dict)):  # noqa: UP038
            # Validar recursivamente estructuras anidadas
            if isinstance(value, dict):
                for k, v in value.items():
                    nested_violations = self._validate_value(v, f"{field_name}.{k}")
                    violations.extend(nested_violations)
            else:  # list
                for i, item in enumerate(value):
                    nested_violations = self._validate_value(item, f"{field_name}[{i}]")
                    violations.extend(nested_violations)

        return violations

    def _validate_request_data(self, request: Request) -> list[str]:
        """Validar datos de la solicitud"""
        violations = []

        # Validar query parameters
        for key, values in request.query_params.multi_items():
            for value in values:
                decoded_value = unquote(value)
                param_violations = self._validate_value(decoded_value, f"query.{key}")
                violations.extend(param_violations)

        # Validar path parameters
        path_params = getattr(request, 'path_params', {})
        for key, value in path_params.items():
            if isinstance(value, str):
                param_violations = self._validate_value(value, f"path.{key}")
                violations.extend(param_violations)

        # Validar headers sensibles
        sensitive_headers = ['authorization', 'cookie', 'x-api-key']
        for header_name in sensitive_headers:
            header_value = request.headers.get(header_name)
            if header_value:
                # Solo verificar longitud y caracteres básicos para headers sensibles
                if len(header_value) > 1000:
                    violations.append(f"Header '{header_name}' excede longitud máxima")

        return violations

    async def dispatch(self, request: Request, call_next) -> Response:
        """Procesar solicitud con validación de entrada"""

        # Excluir rutas específicas
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        try:
            # Validar datos de la solicitud
            violations = self._validate_request_data(request)

            if violations:
                # Log de violaciones de seguridad
                logger.log_security_event(
                    event="input_validation_failed",
                    ip_address=request.client.host if request.client else "unknown",
                    path=request.url.path,
                    violations=violations[:5],  # Limitar para evitar logs demasiado largos
                    user_agent=request.headers.get("User-Agent", "")[:100],
                )

                # Lanzar excepción de validación
                raise ValidationException(
                    message="Entrada inválida detectada", details={"violations": violations}
                )

            # Continuar con la solicitud
            response = await call_next(request)
            return response

        except ValidationException:
            # Re-lanzar excepciones de validación
            raise
        except Exception as e:
            # Log de errores inesperados
            logger.log_error(
                e,
                {
                    "middleware": "InputValidationMiddleware",
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else "unknown",
                },
            )
            # Continuar sin validación en caso de error
            return await call_next(request)


# Instancia global del middleware
input_validation_middleware = InputValidationMiddleware
