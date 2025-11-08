"""Tests para el validador de configuración."""

import pytest
from unittest.mock import MagicMock

from app.core.config_validator import ConfigValidationError, ConfigValidator


def test_config_validator_secret_key_too_short():
    """Test que secret_key corto causa error."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "short"
    mock_settings.csrf_secret = "also-short"
    mock_settings.environment = "production"
    mock_settings.database_url = "postgresql://localhost/test"
    mock_settings.cors_origins = ["http://localhost"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = False
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = False
    mock_settings.ssl_enabled = True
    mock_settings.session_cookie_secure = True
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    with pytest.raises(ConfigValidationError) as exc_info:
        validator.validate_all()

    assert "SECRET_KEY debe tener al menos 32 caracteres" in str(exc_info.value)


def test_config_validator_dev_secret_in_production():
    """Test que dev-secret en producción causa error."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "dev-secret-key-change-in-production-123456789"
    mock_settings.csrf_secret = "csrf-secret-key-change-in-production-123456789"
    mock_settings.environment = "production"
    mock_settings.database_url = "postgresql://localhost/test"
    mock_settings.cors_origins = ["http://localhost"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = False
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = False
    mock_settings.ssl_enabled = True
    mock_settings.session_cookie_secure = True
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    with pytest.raises(ConfigValidationError) as exc_info:
        validator.validate_all()

    assert "dev-secret" in str(exc_info.value).lower()


def test_config_validator_cors_wildcard_in_production():
    """Test que CORS wildcard en producción causa error."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "a" * 32
    mock_settings.csrf_secret = "b" * 32
    mock_settings.environment = "production"
    mock_settings.database_url = "postgresql://localhost/test"
    mock_settings.cors_origins = ["*"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = False
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = False
    mock_settings.ssl_enabled = True
    mock_settings.session_cookie_secure = True
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    with pytest.raises(ConfigValidationError) as exc_info:
        validator.validate_all()

    assert "CORS_ORIGINS='*' en producción" in str(exc_info.value)


def test_config_validator_debug_in_production():
    """Test que DEBUG=True en producción causa error."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "a" * 32
    mock_settings.csrf_secret = "b" * 32
    mock_settings.environment = "production"
    mock_settings.database_url = "postgresql://localhost/test"
    mock_settings.cors_origins = ["https://example.com"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = False
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = True  # ERROR: Debug en producción
    mock_settings.ssl_enabled = True
    mock_settings.session_cookie_secure = True
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    with pytest.raises(ConfigValidationError) as exc_info:
        validator.validate_all()

    assert "DEBUG=True en producción" in str(exc_info.value)


def test_config_validator_valid_development_config():
    """Test que configuración de desarrollo válida pasa."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "dev-secret-key-change-in-production-123456789"
    mock_settings.csrf_secret = "csrf-secret-key-change-in-production-123456789"
    mock_settings.environment = "development"
    mock_settings.database_url = "postgresql://localhost/test"
    mock_settings.cors_origins = ["http://localhost:3000"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = False
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = True
    mock_settings.ssl_enabled = False
    mock_settings.session_cookie_secure = False
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    # No debe lanzar excepción
    assert validator.validate_all() is True
    # Pero debe tener warnings
    assert len(validator.warnings) > 0


def test_config_validator_redis_without_host():
    """Test que rate_limit_use_redis sin redis_host causa error."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "a" * 32
    mock_settings.csrf_secret = "b" * 32
    mock_settings.environment = "development"
    mock_settings.database_url = "postgresql://localhost/test"
    mock_settings.cors_origins = ["http://localhost"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = True  # Pero redis_host es None
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = True
    mock_settings.ssl_enabled = False
    mock_settings.session_cookie_secure = False
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    with pytest.raises(ConfigValidationError) as exc_info:
        validator.validate_all()

    assert "rate_limit_use_redis=True pero REDIS_HOST no está configurado" in str(exc_info.value)


def test_config_validator_invalid_database_url():
    """Test que DATABASE_URL con formato inválido causa error."""
    mock_settings = MagicMock()
    mock_settings.secret_key = "a" * 32
    mock_settings.csrf_secret = "b" * 32
    mock_settings.environment = "development"
    mock_settings.database_url = "mysql://localhost/test"  # MySQL no soportado
    mock_settings.cors_origins = ["http://localhost"]
    mock_settings.rate_limit_requests = 100
    mock_settings.rate_limit_window = 60
    mock_settings.scheduler_enabled = False
    mock_settings.alert_emails = []
    mock_settings.log_file = "logs/test.log"
    mock_settings.rate_limit_use_redis = False
    mock_settings.redis_host = None
    mock_settings.redis_health_check_enabled = False
    mock_settings.debug = True
    mock_settings.ssl_enabled = False
    mock_settings.session_cookie_secure = False
    mock_settings.access_token_expire_minutes = 30
    mock_settings.db_pool_size = 10

    validator = ConfigValidator(mock_settings)

    with pytest.raises(ConfigValidationError) as exc_info:
        validator.validate_all()

    assert "DATABASE_URL tiene formato inválido" in str(exc_info.value)
