"""Standardized error response handlers and custom exceptions.

Provides consistent error responses across all API endpoints and
custom exception classes for common error scenarios.
"""

from datetime import UTC
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging_config import inventario_logger as logger

# ==================== Error Response Models ====================


class ErrorDetail(BaseModel):
    """Details about a specific error."""

    code: str
    message: str
    field: str | None = None


class ErrorResponse(BaseModel):
    """Standard error response format."""

    success: bool = False
    error: str
    message: str
    details: list[ErrorDetail] | None = None
    request_id: str | None = None
    timestamp: str | None = None


# ==================== Custom Exceptions ====================


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationAPIException(APIException):
    """Exception for validation errors."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class NotFoundAPIException(APIException):
    """Exception for not found errors."""

    def __init__(
        self,
        resource: str,
        resource_id: str | None = None,
    ):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"

        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedAPIException(APIException):
    """Exception for unauthorized access."""

    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenAPIException(APIException):
    """Exception for forbidden access."""

    def __init__(
        self,
        message: str = "Access forbidden",
        required_role: str | None = None,
    ):
        if required_role:
            message += f" (required: {required_role})"

        super().__init__(
            message=message,
            error_code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictAPIException(APIException):
    """Exception for conflict/duplicate errors."""

    def __init__(
        self,
        resource: str,
        field: str | None = None,
        value: str | None = None,
    ):
        message = f"Resource conflict: {resource} already exists"
        if field and value:
            message += f" ({field}: {value})"

        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=status.HTTP_409_CONFLICT,
        )


class RateLimitAPIException(APIException):
    """Exception for rate limit errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"retry_after": retry_after} if retry_after else {},
        )


class DatabaseAPIException(APIException):
    """Exception for database errors."""

    def __init__(self, message: str = "Database error"):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ExternalServiceAPIException(APIException):
    """Exception for external service errors."""

    def __init__(
        self,
        service_name: str,
        message: str = "External service error",
    ):
        full_message = f"{service_name}: {message}"

        super().__init__(
            message=full_message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ==================== Error Handlers ====================


def format_error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | list[ErrorDetail] | None = None,
    request_id: str | None = None,
) -> ErrorResponse:
    """Format error response in standard format."""
    from datetime import datetime

    error_details = None

    if details:
        if isinstance(details, dict):
            error_details = [
                ErrorDetail(
                    code=details.get("code", "UNKNOWN"),
                    message=details.get("message", "Unknown error"),
                    field=details.get("field"),
                )
            ]
        elif isinstance(details, list):
            error_details = details

    return ErrorResponse(
        success=False,
        error=error_code,
        message=message,
        details=error_details,
        request_id=request_id,
        timestamp=datetime.now(UTC).isoformat(),
    )


def register_error_handlers(app: FastAPI) -> None:
    """Register error handlers with FastAPI app."""

    # Handle custom API exceptions
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        request_id = getattr(request.state, "request_id", None)

        logger.log_error(
            exc,
            {
                "error_code": exc.error_code,
                "request_path": request.url.path,
                "request_id": request_id,
            },
        )

        error_response = format_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(),
        )

    # Handle Pydantic validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)

        # Extract field-level errors
        error_details = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"][1:])
            error_details.append(
                ErrorDetail(
                    code="VALIDATION_ERROR",
                    message=error["msg"],
                    field=field,
                )
            )

        logger.log_warning(
            f"Validation error on {request.url.path}",
            {
                "error_count": len(exc.errors()),
                "request_id": request_id,
                "errors": error_details,
            },
        )

        error_response = format_error_response(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=error_details,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(),
        )

    # Handle generic exceptions
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)

        logger.log_error(
            exc,
            {
                "request_path": request.url.path,
                "request_id": request_id,
                "exception_type": type(exc).__name__,
            },
        )

        error_response = format_error_response(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(),
        )
