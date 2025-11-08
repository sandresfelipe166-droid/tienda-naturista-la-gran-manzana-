"""Sanitization utilities for Pydantic models and field validators.

Provides reusable validators for Pydantic that sanitize and validate
common field types (emails, phones, strings, etc.).
"""

import re
from html import escape as html_escape

from pydantic import BaseModel, ConfigDict, field_validator


class SanitizedString(str):
    """String type that automatically sanitizes on creation."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str, max_length: int = 500) -> "SanitizedString":
        """Validate and sanitize string."""
        if not isinstance(v, str):
            raise ValueError("Must be a string")

        v = v.strip()

        if len(v) == 0:
            raise ValueError("String cannot be empty")

        if len(v) > max_length:
            raise ValueError(f"String exceeds {max_length} characters")

        # Remove control characters
        v = "".join(char for char in v if ord(char) >= 32 or char in "\t\n\r")

        # HTML escape
        v = html_escape(v, quote=True)

        return cls(v)


def validate_email(v: str) -> str:
    """Validate email format."""
    if not isinstance(v, str):
        raise ValueError("Email must be a string")

    v = v.strip().lower()

    # RFC 5321 format
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

    if not email_pattern.match(v):
        raise ValueError("Invalid email format")

    if len(v) > 254:
        raise ValueError("Email exceeds 254 characters")

    return v


def validate_phone(v: str) -> str:
    """Validate phone number format."""
    if not isinstance(v, str):
        raise ValueError("Phone must be a string")

    v = v.strip()

    # Accept digits, spaces, hyphens, plus, parentheses
    phone_pattern = re.compile(r"^[\d\s\-\+\(\)]{7,20}$")

    if not phone_pattern.match(v):
        raise ValueError("Invalid phone format (7-20 digits/spaces/special chars)")

    return v


def validate_cedula(v: str) -> str:
    """Validate cedula/ID number."""
    if not isinstance(v, str):
        raise ValueError("Cedula must be a string")

    v = v.strip()

    cedula_pattern = re.compile(r"^\d{6,10}$")

    if not cedula_pattern.match(v):
        raise ValueError("Invalid cedula format (6-10 digits)")

    return v


def validate_username(v: str) -> str:
    """Validate username format."""
    if not isinstance(v, str):
        raise ValueError("Username must be a string")

    v = v.strip()

    username_pattern = re.compile(r"^[a-zA-Z0-9_-]{3,50}$")

    if not username_pattern.match(v):
        raise ValueError("Username must be 3-50 chars (alphanumeric, -, _ only)")

    return v


def sanitize_for_display(value: str, max_length: int = 500) -> str:
    """Sanitize string for safe HTML display."""
    if not isinstance(value, str):
        return ""

    value = value.strip()

    if len(value) > max_length:
        value = value[:max_length] + "..."

    # Remove control characters
    value = "".join(char for char in value if ord(char) >= 32 or char in "\t\n\r")

    # HTML escape
    value = html_escape(value, quote=True)

    return value


def detect_suspicious_input(value: str) -> str | None:
    """Detect common suspicious patterns in input.

    Returns error message if suspicious pattern found, None otherwise.
    """
    if not isinstance(value, str):
        return None

    value_lower = value.lower()

    # SQL injection patterns
    sql_patterns = [
        r"union.*select",
        r"(or|and).*(1=1|1=0)",
        r"--\s*$",
        r"/\*.*\*/",
        r"xp_cmdshell",
        r"exec\s*\(",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            return f"Suspicious SQL pattern detected: {pattern}"

    # XSS patterns
    xss_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
    ]

    for pattern in xss_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            return f"Suspicious XSS pattern detected: {pattern}"

    return None


class BaseModelSanitized(BaseModel):
    """Base model with common sanitization validators."""

    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class ClienteSanitized(BaseModelSanitized):
    """Sanitized client schema with validators."""

    nombre_cliente: str
    apellido_cliente: str
    cedula: str
    email: str | None = None
    telefono: str | None = None
    direccion: str | None = None

    @field_validator("nombre_cliente", "apellido_cliente")
    @classmethod
    def validate_nombre(cls, v: str) -> str:
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Name cannot be empty")
        if len(v) > 100:
            raise ValueError("Name cannot exceed 100 characters")
        # Allow letters (including accented), spaces, hyphens, apostrophes
        if not re.match(r"^[a-zA-Z\s\-'áéíóúñÁÉÍÓÚÑ]{1,100}$", v):
            raise ValueError("Name contains invalid characters")
        return v

    @field_validator("cedula")
    @classmethod
    def validate_cedula_field(cls, v: str) -> str:
        return validate_cedula(v)

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, v: str | None) -> str | None:
        if v:
            return validate_email(v)
        return v

    @field_validator("telefono")
    @classmethod
    def validate_telefono_field(cls, v: str | None) -> str | None:
        if v:
            return validate_phone(v)
        return v

    @field_validator("direccion")
    @classmethod
    def validate_direccion_field(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("Address cannot exceed 200 characters")
            suspicious = detect_suspicious_input(v)
            if suspicious:
                raise ValueError(suspicious)
            return v
        return v


class ProductoSanitized(BaseModelSanitized):
    """Sanitized producto schema with validators."""

    nombre_producto: str
    codigo_barras: str
    precio_compra: float
    stock_actual: int
    stock_minimo: int
    descripcion: str | None = None

    @field_validator("nombre_producto")
    @classmethod
    def validate_nombre_producto(cls, v: str) -> str:
        v = v.strip()
        if len(v) == 0:
            raise ValueError("Product name cannot be empty")
        if len(v) > 100:
            raise ValueError("Product name cannot exceed 100 characters")
        suspicious = detect_suspicious_input(v)
        if suspicious:
            raise ValueError(suspicious)
        return v

    @field_validator("codigo_barras")
    @classmethod
    def validate_codigo_barras(cls, v: str) -> str:
        v = v.strip()
        # Accept alphanumeric and common barcode separators
        if not re.match(r"^[a-zA-Z0-9\-_]{1,50}$", v):
            raise ValueError("Invalid barcode format")
        return v

    @field_validator("precio_compra", "stock_actual", "stock_minimo")
    @classmethod
    def validate_numeric(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Value cannot be negative")
        return v

    @field_validator("descripcion")
    @classmethod
    def validate_descripcion(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if len(v) > 200:
                raise ValueError("Description cannot exceed 200 characters")
            suspicious = detect_suspicious_input(v)
            if suspicious:
                raise ValueError(suspicious)
            return v
        return v
