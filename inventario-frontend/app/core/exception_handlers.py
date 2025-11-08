"""
Manejadores de excepciones centralizados para FastAPI
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import InventarioException

logger = logging.getLogger(__name__)


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] = None,
) -> JSONResponse:
    """Crea una respuesta de error uniforme."""
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
        "timestamp": datetime.utcnow().isoformat(),
        "path": request.url.path,
    }
    return JSONResponse(status_code=status_code, content=payload)


async def inventario_exception_handler(request: Request, exc: InventarioException) -> JSONResponse:
    """Manejador para excepciones personalizadas del inventario."""
    logger.error(
        f"InventarioException: {exc.error_code} - {exc.message}",
        extra={
            "extra_data": {
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method,
            }
        },
        exc_info=False,
    )
    return _error_response(
        request,
        status_code=exc.status_code,
        code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Manejador para errores de validación de Pydantic/FastAPI."""
    errors: list[dict[str, Any]] = []
    try:
        for err in exc.errors():
            field = ".".join(str(x) for x in err.get("loc", []))
            errors.append(
                {
                    "field": field,
                    "message": err.get("msg", ""),
                    "type": err.get("type", ""),
                }
            )
    except Exception:
        # fallback si el esquema de errores cambia
        errors = [{"message": "Invalid payload"}]

    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={"extra_data": {"validation_errors": errors}},
    )
    return _error_response(
        request,
        status_code=422,
        code="VALIDATION_ERROR",
        message="Error de validación en los datos enviados",
        details={"errors": errors},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manejador para HTTPException estándar."""
    # Derivar código simbólico básico por status
    status_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        429: "TOO_MANY_REQUESTS",
        500: "HTTP_ERROR",
    }
    code = status_map.get(exc.status_code, "HTTP_ERROR")

    # Normalizar message y details desde exc.detail
    message: str = "HTTP Error"
    details: dict[str, Any] = {}

    if isinstance(exc.detail, str):
        message = exc.detail
    elif isinstance(exc.detail, dict):
        message = str(exc.detail.get("message", code))
        # si ya viene una estructura tipo error, preservarla como details
        details = {k: v for k, v in exc.detail.items() if k != "message"}
    else:
        message = str(exc.detail or code)

    logger.warning(
        f"HTTPException {exc.status_code} on {request.method} {request.url.path}: {message}",
        extra={"extra_data": {"status_code": exc.status_code, "details": details}},
    )
    return _error_response(
        request,
        status_code=exc.status_code,
        code=code,
        message=message,
        details=details,
    )


async def database_exception_handler(
    request: Request, exc: IntegrityError | SQLAlchemyError
) -> JSONResponse:
    """Manejador para errores de base de datos."""
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "extra_data": {
                "exception_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method,
            }
        },
        exc_info=True,
    )

    # Determinar el tipo de error específico
    code = "DATABASE_ERROR"
    message = "Error interno de base de datos"
    details: dict[str, Any] = {"database_error": True}

    if isinstance(exc, IntegrityError):
        lower_msg = str(exc).lower()
        if "unique constraint" in lower_msg or "unique violation" in lower_msg:
            code = "DUPLICATE_ENTRY"
            message = "Ya existe un registro con estos datos"
        elif "foreign key constraint" in lower_msg or "foreign key violation" in lower_msg:
            code = "FOREIGN_KEY_VIOLATION"
            message = "Referencia a un registro que no existe"
        elif "not null constraint" in lower_msg:
            code = "REQUIRED_FIELD_MISSING"
            message = "Falta un campo requerido"
        else:
            code = "INTEGRITY_ERROR"
            message = "Error de integridad en la base de datos"

    return _error_response(
        request,
        status_code=500,
        code=code,
        message=message,
        details=details,
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador para excepciones no controladas."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "extra_data": {
                "exception_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method,
            }
        },
        exc_info=True,
    )
    return _error_response(
        request,
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="Error interno del servidor",
        details={"exception_type": type(exc).__name__},
    )
