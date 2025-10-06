"""
Request ID middleware

- Ensures every request has a stable request_id available as request.state.request_id
- Echoes/generates X-Request-Id header on responses
- If an incoming X-Request-Id header exists, uses a safe, validated value; otherwise generates a new UUID4
"""
from __future__ import annotations

from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request, Response
import uuid
import string
from app.core.log_context import set_request_id, clear_request_id


REQUEST_ID_HEADER = "X-Request-Id"


def _is_safe_request_id(value: str) -> bool:
    """Validate request id value for safety (alphanum, dash, underscore, max length)."""
    if not value or len(value) > 128:
        return False
    allowed = set(string.ascii_letters + string.digits + "-_")
    return all(ch in allowed for ch in value)


def _generate_request_id() -> str:
    """Generate a new UUID4-based request id (without braces)."""
    return str(uuid.uuid4())


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Starlette/FastAPI middleware to attach a request id to request.state and response headers.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Try to get incoming request id
        incoming: Optional[str] = request.headers.get(REQUEST_ID_HEADER)
        if incoming and _is_safe_request_id(incoming):
            request_id = incoming
        else:
            request_id = _generate_request_id()

        # Attach to request state for downstream middlewares/handlers
        setattr(request.state, "request_id", request_id)
        # Also set into contextvar so log filter can inject it into all log records
        set_request_id(request_id)

        try:
            # Process downstream
            response = await call_next(request)

            # Ensure header is present on responses
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            # Clear contextvar to avoid leaking between requests
            clear_request_id()
