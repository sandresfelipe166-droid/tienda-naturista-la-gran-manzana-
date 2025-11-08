"""Audit trail and compliance utilities.

Provides comprehensive audit logging for critical operations:
- User authentication and authorization changes
- Data modifications (create, update, delete)
- Sensitive operations
- Compliance reporting
"""

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session

from app.core.logging_config import inventario_logger as logger
from app.models.database import Base


class AuditAction(str, Enum):
    """Types of audit actions."""

    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    AUTH_FAILURE = "AUTH_FAILURE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    CONFIG_CHANGE = "CONFIG_CHANGE"


class AuditLog(Base):
    """Audit log model for tracking critical operations."""

    __tablename__ = "audit_log"

    id_audit = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(50), index=True)
    resource_type = Column(String(100), index=True)  # e.g., "Producto", "Usuario", "Venta"
    resource_id = Column(Integer, index=True, nullable=True)
    ip_address = Column(String(45), index=True, nullable=True)  # Supports IPv6
    status = Column(String(20), default="SUCCESS")  # SUCCESS, FAILURE
    changes = Column(JSON, nullable=True)  # Before and after values
    message = Column(Text, nullable=True)
    request_id = Column(String(100), nullable=True)


class AuditLogger:
    """Logger for audit trail operations."""

    @staticmethod
    def log_audit(
        db: Session,
        user_id: int | None = None,
        username: str | None = None,
        action: AuditAction = AuditAction.READ,
        resource_type: str = "",
        resource_id: int | None = None,
        ip_address: str | None = None,
        status: str = "SUCCESS",
        changes: dict[str, Any] | None = None,
        message: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        """Log an audit event.

        Args:
            db: Database session
            user_id: ID of user performing action
            username: Username of user performing action
            action: Type of action (CREATE, UPDATE, DELETE, LOGIN, etc.)
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            ip_address: IP address of client
            status: Status of operation (SUCCESS, FAILURE)
            changes: Dictionary of changes (before/after values)
            message: Additional message
            request_id: Request ID for correlation

        Returns:
            AuditLog object
        """
        audit_entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            username=username,
            action=action.value if isinstance(action, AuditAction) else action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            status=status,
            changes=changes,
            message=message,
            request_id=request_id,
        )

        db.add(audit_entry)
        db.commit()
        db.refresh(audit_entry)

        # Log to application logger
        log_message = f"[AUDIT] {action.value if isinstance(action, AuditAction) else action} on {resource_type}"

        if username:
            log_message += f" by {username}"

        if ip_address:
            log_message += f" from {ip_address}"

        if status != "SUCCESS":
            log_message += f" - Status: {status}"

        logger.log_info(
            log_message,
            {
                "action": action.value if isinstance(action, AuditAction) else action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "status": status,
                "changes": changes,
                "request_id": request_id,
            },
        )

        return audit_entry

    @staticmethod
    def log_create(
        db: Session,
        user_id: int | None,
        username: str | None,
        resource_type: str,
        resource_id: int,
        data: dict[str, Any],
        ip_address: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        """Log resource creation."""
        return AuditLogger.log_audit(
            db=db,
            user_id=user_id,
            username=username,
            action=AuditAction.CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            changes={"created": data},
            request_id=request_id,
        )

    @staticmethod
    def log_update(
        db: Session,
        user_id: int | None,
        username: str | None,
        resource_type: str,
        resource_id: int,
        changes: dict[str, Any],
        ip_address: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        """Log resource update."""
        return AuditLogger.log_audit(
            db=db,
            user_id=user_id,
            username=username,
            action=AuditAction.UPDATE,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            changes=changes,
            request_id=request_id,
        )

    @staticmethod
    def log_delete(
        db: Session,
        user_id: int | None,
        username: str | None,
        resource_type: str,
        resource_id: int,
        data: dict[str, Any],
        ip_address: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        """Log resource deletion."""
        return AuditLogger.log_audit(
            db=db,
            user_id=user_id,
            username=username,
            action=AuditAction.DELETE,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            changes={"deleted": data},
            request_id=request_id,
        )

    @staticmethod
    def log_login(
        db: Session,
        username: str,
        ip_address: str | None = None,
        success: bool = True,
        request_id: str | None = None,
    ) -> AuditLog:
        """Log login attempt."""
        action = AuditAction.LOGIN if success else AuditAction.AUTH_FAILURE
        status = "SUCCESS" if success else "FAILURE"

        return AuditLogger.log_audit(
            db=db,
            username=username,
            action=action,
            resource_type="AUTH",
            ip_address=ip_address,
            status=status,
            message=f"Login {'successful' if success else 'failed'} for user {username}",
            request_id=request_id,
        )

    @staticmethod
    def log_permission_denied(
        db: Session,
        user_id: int | None,
        username: str | None,
        resource_type: str,
        action: str,
        ip_address: str | None = None,
        request_id: str | None = None,
    ) -> AuditLog:
        """Log permission denied event."""
        return AuditLogger.log_audit(
            db=db,
            user_id=user_id,
            username=username,
            action=AuditAction.PERMISSION_DENIED,
            resource_type=resource_type,
            ip_address=ip_address,
            status="FAILURE",
            message=f"Permission denied for {action} on {resource_type}",
            request_id=request_id,
        )


class AuditQueryBuilder:
    """Builder for audit log queries with common filters."""

    def __init__(self, db: Session):
        self.db = db
        self.query = db.query(AuditLog)

    def by_user(self, user_id: int) -> "AuditQueryBuilder":
        """Filter by user ID."""
        self.query = self.query.filter(AuditLog.user_id == user_id)
        return self

    def by_username(self, username: str) -> "AuditQueryBuilder":
        """Filter by username."""
        self.query = self.query.filter(AuditLog.username == username)
        return self

    def by_action(self, action: AuditAction) -> "AuditQueryBuilder":
        """Filter by action."""
        action_str = action.value if isinstance(action, AuditAction) else action
        self.query = self.query.filter(AuditLog.action == action_str)
        return self

    def by_resource_type(self, resource_type: str) -> "AuditQueryBuilder":
        """Filter by resource type."""
        self.query = self.query.filter(AuditLog.resource_type == resource_type)
        return self

    def by_resource_id(self, resource_id: int) -> "AuditQueryBuilder":
        """Filter by resource ID."""
        self.query = self.query.filter(AuditLog.resource_id == resource_id)
        return self

    def by_date_range(self, start_date: datetime, end_date: datetime) -> "AuditQueryBuilder":
        """Filter by date range."""
        self.query = self.query.filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date,
        )
        return self

    def by_status(self, status: str) -> "AuditQueryBuilder":
        """Filter by status."""
        self.query = self.query.filter(AuditLog.status == status)
        return self

    def by_ip_address(self, ip_address: str) -> "AuditQueryBuilder":
        """Filter by IP address."""
        self.query = self.query.filter(AuditLog.ip_address == ip_address)
        return self

    def order_by_recent(self) -> "AuditQueryBuilder":
        """Order by most recent first."""
        self.query = self.query.order_by(AuditLog.timestamp.desc())
        return self

    def limit(self, limit: int) -> "AuditQueryBuilder":
        """Limit results."""
        self.query = self.query.limit(limit)
        return self

    def offset(self, offset: int) -> "AuditQueryBuilder":
        """Offset results (for pagination)."""
        self.query = self.query.offset(offset)
        return self

    def all(self) -> list[AuditLog]:
        """Execute query and return all results."""
        return self.query.all()

    def first(self) -> AuditLog | None:
        """Execute query and return first result."""
        return self.query.first()

    def count(self) -> int:
        """Execute query and return count."""
        return self.query.count()
