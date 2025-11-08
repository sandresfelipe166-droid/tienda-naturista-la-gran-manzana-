"""
Sistema de auditoría para registrar operaciones sensibles y cambios importantes
"""

from typing import Any

from app.core.logging_config import inventario_logger

logger = inventario_logger


class AuditLogger:
    """Logger para auditoría de operaciones"""

    def log_audit_event(
        self,
        event: str,
        user_id: int = None,
        ip_address: str = None,
        details: dict[str, Any] = None,
    ):
        """Registrar evento de auditoría"""
        logger.log_business_event(
            event, {"user_id": user_id, "ip_address": ip_address, "details": details or {}}
        )


audit_logger = AuditLogger()
