"""Tests for sanitization and error response utilities."""

import pytest
from pydantic import ValidationError

from app.core.error_responses import (
    ConflictAPIException,
    ForbiddenAPIException,
    NotFoundAPIException,
    RateLimitAPIException,
    UnauthorizedAPIException,
    ValidationAPIException,
    format_error_response,
)
from app.core.sanitization import (
    ClienteSanitized,
    ProductoSanitized,
    detect_suspicious_input,
    sanitize_for_display,
    validate_cedula,
    validate_email,
    validate_phone,
    validate_username,
)


class TestEmailValidation:
    """Test email validation."""

    def test_valid_email(self):
        assert validate_email("user@example.com") == "user@example.com"

    def test_valid_email_lowercased(self):
        assert validate_email("User@Example.COM") == "user@example.com"

    def test_invalid_email_no_domain(self):
        with pytest.raises(ValueError):
            validate_email("user@")

    def test_invalid_email_no_at(self):
        with pytest.raises(ValueError):
            validate_email("user.example.com")


class TestPhoneValidation:
    """Test phone number validation."""

    def test_valid_phone(self):
        assert validate_phone("+1 (555) 123-4567") == "+1 (555) 123-4567"

    def test_invalid_phone_too_short(self):
        with pytest.raises(ValueError):
            validate_phone("123")

    def test_invalid_phone_special_chars(self):
        with pytest.raises(ValueError):
            validate_phone("abc-def-ghij")


class TestCedulaValidation:
    """Test cedula validation."""

    def test_valid_cedula(self):
        assert validate_cedula("12345678") == "12345678"

    def test_invalid_cedula_non_numeric(self):
        with pytest.raises(ValueError):
            validate_cedula("abc12345")

    def test_invalid_cedula_too_short(self):
        with pytest.raises(ValueError):
            validate_cedula("123")


class TestUsernameValidation:
    """Test username validation."""

    def test_valid_username(self):
        assert validate_username("john_doe-123") == "john_doe-123"

    def test_invalid_username_too_short(self):
        with pytest.raises(ValueError):
            validate_username("ab")

    def test_invalid_username_special_chars(self):
        with pytest.raises(ValueError):
            validate_username("john@doe")


class TestSuspiciousInputDetection:
    """Test detection of suspicious input patterns."""

    def test_detect_sql_injection_union(self):
        result = detect_suspicious_input("' UNION SELECT * FROM users")
        assert result is not None
        assert "SQL" in result

    def test_detect_xss_script(self):
        result = detect_suspicious_input("<script>alert('xss')</script>")
        assert result is not None
        assert "XSS" in result

    def test_detect_javascript_protocol(self):
        result = detect_suspicious_input("javascript:alert('xss')")
        assert result is not None
        assert "XSS" in result

    def test_clean_input_no_detection(self):
        result = detect_suspicious_input("This is a normal product name")
        assert result is None


class TestSanitizeForDisplay:
    """Test string sanitization for display."""

    def test_sanitize_normal_text(self):
        result = sanitize_for_display("Hello World")
        assert result == "Hello World"

    def test_sanitize_html_escape(self):
        result = sanitize_for_display("<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_sanitize_truncate_long_text(self):
        long_text = "a" * 600
        result = sanitize_for_display(long_text, max_length=500)
        assert len(result) <= 503  # 500 + "..."


class TestClienteSanitized:
    """Test sanitized cliente model."""

    def test_valid_cliente(self):
        cliente = ClienteSanitized(
            nombre_cliente="Juan",
            apellido_cliente="Pérez",
            cedula="12345678",
            email="juan@example.com",
            telefono="+1-555-1234",
            direccion="123 Main St",
        )
        assert cliente.nombre_cliente == "Juan"
        assert cliente.cedula == "12345678"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            ClienteSanitized(
                nombre_cliente="Juan",
                apellido_cliente="Pérez",
                cedula="12345678",
                email="invalid-email",
            )

    def test_invalid_cedula(self):
        with pytest.raises(ValidationError):
            ClienteSanitized(
                nombre_cliente="Juan",
                apellido_cliente="Pérez",
                cedula="abc",
            )


class TestProductoSanitized:
    """Test sanitized producto model."""

    def test_valid_producto(self):
        producto = ProductoSanitized(
            nombre_producto="Paracetamol",
            codigo_barras="5901234123457",
            precio_compra=10.5,
            stock_actual=100,
            stock_minimo=10,
            descripcion="Pain reliever",
        )
        assert producto.nombre_producto == "Paracetamol"

    def test_invalid_precio_negative(self):
        with pytest.raises(ValidationError):
            ProductoSanitized(
                nombre_producto="Paracetamol",
                codigo_barras="5901234123457",
                precio_compra=-10.5,
                stock_actual=100,
                stock_minimo=10,
            )

    def test_invalid_codigo_barras(self):
        with pytest.raises(ValidationError):
            ProductoSanitized(
                nombre_producto="Paracetamol",
                codigo_barras="invalid!!!barcode",
                precio_compra=10.5,
                stock_actual=100,
                stock_minimo=10,
            )


class TestErrorResponses:
    """Test error response classes."""

    def test_validation_exception(self):
        exc = ValidationAPIException("Field required", details={"field": "email"})
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400

    def test_not_found_exception(self):
        exc = NotFoundAPIException("Producto", "123")
        assert exc.error_code == "NOT_FOUND"
        assert "123" in exc.message
        assert exc.status_code == 404

    def test_unauthorized_exception(self):
        exc = UnauthorizedAPIException()
        assert exc.error_code == "UNAUTHORIZED"
        assert exc.status_code == 401

    def test_forbidden_exception(self):
        exc = ForbiddenAPIException("Access denied", required_role="admin")
        assert exc.error_code == "FORBIDDEN"
        assert "admin" in exc.message
        assert exc.status_code == 403

    def test_conflict_exception(self):
        exc = ConflictAPIException("Cliente", field="cedula", value="12345678")
        assert exc.error_code == "CONFLICT"
        assert "cedula" in exc.message
        assert exc.status_code == 409

    def test_rate_limit_exception(self):
        exc = RateLimitAPIException(retry_after=60)
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
        assert exc.status_code == 429
        assert exc.details.get("retry_after") == 60


class TestFormatErrorResponse:
    """Test error response formatting."""

    def test_format_error_response_basic(self):
        response = format_error_response(
            error_code="TEST_ERROR",
            message="Test error message",
            status_code=400,
        )
        assert response.success is False
        assert response.error == "TEST_ERROR"
        assert response.message == "Test error message"
        assert response.timestamp is not None

    def test_format_error_response_with_request_id(self):
        response = format_error_response(
            error_code="TEST_ERROR",
            message="Test",
            status_code=400,
            request_id="req-123",
        )
        assert response.request_id == "req-123"
