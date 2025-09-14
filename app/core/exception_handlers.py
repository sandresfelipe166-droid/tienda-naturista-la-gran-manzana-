"""
Manejadores de excepciones centralizados para FastAPI
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import logging
from typing import Union

from app.core.exceptions import InventarioException

logger = logging.getLogger(__name__)


async def inventario_exception_handler(request: Request, exc: InventarioException) -> JSONResponse:
    """Manejador para excepciones personalizadas del inventario"""
    
    # Log del error
    logger.error(
        f"InventarioException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Manejador para errores de validación de Pydantic"""
    
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error on {request.method} {request.url.path}",
        extra={"validation_errors": errors}
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Error de validación en los datos enviados",
                "details": {
                    "errors": errors
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manejador para excepciones HTTP de FastAPI"""
    
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "details": {}
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def database_exception_handler(request: Request, exc: Union[IntegrityError, SQLAlchemyError]) -> JSONResponse:
    """Manejador para errores de base de datos"""
    
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    # Determinar el tipo de error específico
    if isinstance(exc, IntegrityError):
        if "unique constraint" in str(exc).lower():
            error_code = "DUPLICATE_ENTRY"
            message = "Ya existe un registro con estos datos"
        elif "foreign key constraint" in str(exc).lower():
            error_code = "FOREIGN_KEY_VIOLATION"
            message = "Referencia a un registro que no existe"
        elif "not null constraint" in str(exc).lower():
            error_code = "REQUIRED_FIELD_MISSING"
            message = "Falta un campo requerido"
        else:
            error_code = "INTEGRITY_ERROR"
            message = "Error de integridad en la base de datos"
    else:
        error_code = "DATABASE_ERROR"
        message = "Error interno de base de datos"
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": {
                    "database_error": True
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador para excepciones no controladas"""
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Error interno del servidor",
                "details": {
                    "exception_type": type(exc).__name__
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )
