"""Tests for audit trail functionality."""

import pytest
from datetime import datetime, timedelta

from app.core.audit_trail import (
    AuditLogger,
    AuditAction,
    AuditLog,
    AuditQueryBuilder,
)


class TestAuditLogger:
    """Tests for AuditLogger."""

    def test_log_create_operation(self, db_session):
        """Test logging a CREATE operation."""
        audit = AuditLogger.log_create(
            db=db_session,
            user_id=1,
            username="admin",
            resource_type="Producto",
            resource_id=123,
            data={"name": "Paracetamol", "price": 10.5},
            ip_address="192.168.1.1",
            request_id="req-123",
        )

        assert audit.action == "CREATE"
        assert audit.resource_type == "Producto"
        assert audit.resource_id == 123
        assert audit.username == "admin"
        assert audit.status == "SUCCESS"
        assert audit.changes["created"]["name"] == "Paracetamol"

    def test_log_update_operation(self, db_session):
        """Test logging an UPDATE operation."""
        changes = {
            "before": {"price": 10.5},
            "after": {"price": 12.0},
        }

        audit = AuditLogger.log_update(
            db=db_session,
            user_id=1,
            username="admin",
            resource_type="Producto",
            resource_id=123,
            changes=changes,
            ip_address="192.168.1.1",
        )

        assert audit.action == "UPDATE"
        assert audit.changes["before"]["price"] == 10.5
        assert audit.changes["after"]["price"] == 12.0

    def test_log_delete_operation(self, db_session):
        """Test logging a DELETE operation."""
        audit = AuditLogger.log_delete(
            db=db_session,
            user_id=1,
            username="admin",
            resource_type="Producto",
            resource_id=123,
            data={"name": "Paracetamol", "price": 10.5},
            ip_address="192.168.1.1",
        )

        assert audit.action == "DELETE"
        assert audit.resource_id == 123
        assert audit.changes["deleted"]["name"] == "Paracetamol"

    def test_log_login_success(self, db_session):
        """Test logging successful login."""
        audit = AuditLogger.log_login(
            db=db_session,
            username="admin",
            ip_address="192.168.1.1",
            success=True,
        )

        assert audit.action == "LOGIN"
        assert audit.status == "SUCCESS"
        assert audit.username == "admin"

    def test_log_login_failure(self, db_session):
        """Test logging failed login."""
        audit = AuditLogger.log_login(
            db=db_session,
            username="admin",
            ip_address="192.168.1.1",
            success=False,
        )

        assert audit.action == "AUTH_FAILURE"
        assert audit.status == "FAILURE"

    def test_log_permission_denied(self, db_session):
        """Test logging permission denied."""
        audit = AuditLogger.log_permission_denied(
            db=db_session,
            user_id=2,
            username="user",
            resource_type="Producto",
            action="DELETE",
            ip_address="192.168.1.2",
        )

        assert audit.action == "PERMISSION_DENIED"
        assert audit.status == "FAILURE"
        assert "DELETE" in audit.message


class TestAuditQueryBuilder:
    """Tests for AuditQueryBuilder."""

    @pytest.fixture(autouse=True)
    def setup_audit_data(self, db_session):
        """Setup test audit data."""
        # Create some audit logs
        for i in range(5):
            AuditLogger.log_create(
                db=db_session,
                user_id=1,
                username="admin",
                resource_type="Producto",
                resource_id=100 + i,
                data={"name": f"Product{i}"},
                ip_address="192.168.1.1",
            )

        AuditLogger.log_login(
            db=db_session,
            username="user",
            ip_address="192.168.1.2",
            success=True,
        )

    def test_query_by_user(self, db_session):
        """Test query by user ID."""
        builder = AuditQueryBuilder(db_session)
        results = builder.by_user(1).all()
        assert len(results) > 0
        assert all(r.user_id == 1 for r in results)

    def test_query_by_username(self, db_session):
        """Test query by username."""
        builder = AuditQueryBuilder(db_session)
        results = builder.by_username("admin").all()
        assert len(results) > 0
        assert all(r.username == "admin" for r in results)

    def test_query_by_action(self, db_session):
        """Test query by action."""
        builder = AuditQueryBuilder(db_session)
        results = builder.by_action(AuditAction.CREATE).all()
        assert len(results) == 5
        assert all(r.action == "CREATE" for r in results)

    def test_query_by_resource_type(self, db_session):
        """Test query by resource type."""
        builder = AuditQueryBuilder(db_session)
        results = builder.by_resource_type("Producto").all()
        assert len(results) == 5
        assert all(r.resource_type == "Producto" for r in results)

    def test_query_by_resource_id(self, db_session):
        """Test query by resource ID."""
        builder = AuditQueryBuilder(db_session)
        result = builder.by_resource_id(100).first()
        assert result is not None
        assert result.resource_id == 100

    def test_query_order_by_recent(self, db_session):
        """Test order by most recent."""
        builder = AuditQueryBuilder(db_session)
        results = builder.order_by_recent().limit(2).all()
        assert len(results) >= 1
        if len(results) > 1:
            assert results[0].timestamp >= results[1].timestamp

    def test_query_limit_and_offset(self, db_session):
        """Test limit and offset."""
        builder1 = AuditQueryBuilder(db_session)
        results1 = builder1.limit(3).all()

        builder2 = AuditQueryBuilder(db_session)
        results2 = builder2.limit(3).offset(2).all()

        assert len(results1) == 3
        assert len(results2) <= 3

    def test_query_count(self, db_session):
        """Test count query."""
        builder = AuditQueryBuilder(db_session)
        count = builder.by_action(AuditAction.CREATE).count()
        assert count == 5

    def test_query_chaining(self, db_session):
        """Test chaining multiple filters."""
        builder = AuditQueryBuilder(db_session)
        results = (
            builder.by_user(1)
            .by_action(AuditAction.CREATE)
            .by_resource_type("Producto")
            .order_by_recent()
            .limit(2)
            .all()
        )

        assert len(results) == 2
        assert all(r.user_id == 1 for r in results)
        assert all(r.action == "CREATE" for r in results)
