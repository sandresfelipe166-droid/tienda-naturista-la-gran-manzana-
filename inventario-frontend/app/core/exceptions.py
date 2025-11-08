"""
Sistema de excepciones personalizadas para el inventario
"""

from typing import Any


class InventarioException(Exception):
    """Excepción base para el sistema de inventario"""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(InventarioException):
    """Excepción para errores de validación"""

    def __init__(self, message: str, field: str = None, details: dict[str, Any] = None):
        super().__init__(
            message=message, error_code="VALIDATION_ERROR", status_code=422, details=details or {}
        )
        if field:
            self.details["field"] = field


class NotFoundError(InventarioException):
    """Excepción para recursos no encontrados"""

    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} no encontrado"
        if identifier:
            message += f" con ID: {identifier}"

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier},
        )


class StockInsuficienteException(InventarioException):
    """Excepción para stock insuficiente"""

    def __init__(self, producto_id: int, stock_actual: int, cantidad_solicitada: int):
        super().__init__(
            message=f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad_solicitada}",
            error_code="INSUFFICIENT_STOCK",
            status_code=400,
            details={
                "producto_id": producto_id,
                "stock_actual": stock_actual,
                "cantidad_solicitada": cantidad_solicitada,
            },
        )


class ProductoVencidoException(InventarioException):
    """Excepción para productos vencidos"""

    def __init__(self, producto_id: int, lote_id: int, fecha_vencimiento: str):
        super().__init__(
            message=f"El producto del lote {lote_id} está vencido desde {fecha_vencimiento}",
            error_code="EXPIRED_PRODUCT",
            status_code=400,
            details={
                "producto_id": producto_id,
                "lote_id": lote_id,
                "fecha_vencimiento": fecha_vencimiento,
            },
        )


class DuplicateResourceException(InventarioException):
    """Excepción para recursos duplicados"""

    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            message=f"{resource} ya existe con {field}: {value}",
            error_code="DUPLICATE_RESOURCE",
            status_code=409,
            details={"resource": resource, "field": field, "value": value},
        )


class AuthenticationException(InventarioException):
    """Excepción para errores de autenticación"""

    def __init__(self, message: str = "Credenciales inválidas"):
        super().__init__(message=message, error_code="AUTHENTICATION_ERROR", status_code=401)


class AuthorizationException(InventarioException):
    """Excepción para errores de autorización"""

    def __init__(self, message: str = "No tiene permisos para realizar esta acción"):
        super().__init__(message=message, error_code="AUTHORIZATION_ERROR", status_code=403)


class DatabaseException(InventarioException):
    """Excepción para errores de base de datos"""

    def __init__(self, message: str, operation: str = None):
        super().__init__(
            message=f"Error de base de datos: {message}",
            error_code="DATABASE_ERROR",
            status_code=500,
            details={"operation": operation} if operation else {},
        )


class ExternalServiceException(InventarioException):
    """Excepción para errores de servicios externos"""

    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"Error en servicio externo {service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=503,
            details={"service": service},
        )


class RateLimitException(InventarioException):
    """Excepción para límite de tasa excedido"""

    def __init__(self, limit: int, window: int):
        super().__init__(
            message=f"Límite de {limit} solicitudes por {window} segundos excedido",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"limit": limit, "window": window},
        )


class SecurityException(Exception):
    """Excepción para errores de seguridad (CSRF, API Key, autorización)."""

    def __init__(self, message: str = "Security error", status_code: int = 403):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
