"""
Log context utilities: request-scoped contextvars and logging filters.

- request_id_var: ContextVar used to propagate request id into log records
- RequestIdFilter: logging.Filter that injects request_id into LogRecord
"""

from __future__ import annotations

import logging
from contextvars import ContextVar

# Context variable to hold the current request id
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """
    Logging filter that injects the current request_id into log records.

    The JSONFormatter in logging_config.py already looks for record.request_id.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rid = request_id_var.get()
        except Exception:
            rid = None
        # Attach as attribute for formatters
        record.request_id = rid
        return True


def set_request_id(request_id: str | None) -> None:
    """Set current request id in contextvar."""
    try:
        request_id_var.set(request_id)
    except Exception:
        # Do not crash logging if contextvar cannot be set
        pass


def get_request_id() -> str | None:
    """Get current request id from contextvar."""
    try:
        return request_id_var.get()
    except Exception:
        return None


def clear_request_id() -> None:
    """Clear request id from contextvar."""
    try:
        request_id_var.set(None)
    except Exception:
        pass


__all__ = [
    "request_id_var",
    "RequestIdFilter",
    "set_request_id",
    "get_request_id",
    "clear_request_id",
]
