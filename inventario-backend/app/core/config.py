import os
from typing import Any
import json

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base configuration
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Server
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", "8000"))

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://admin:admin123@localhost:5432/inventario",
    )
    db_host: str | None = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "inventario")
    db_user: str = os.getenv("DB_USER", "admin")
    db_password: str = os.getenv("DB_PASSWORD", "admin123")

    # Database - Advanced Pool Configuration
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "30"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    db_connect_args: dict[str, Any] = {}

    # Schema creation on startup (for development only; prefer Alembic migrations)
    create_schema_on_startup: bool = (
        os.getenv("CREATE_SCHEMA_ON_STARTUP", "false").lower() == "true"
    )

    # Security - JWT
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-123456789")
    algorithm: str = os.getenv("JWT_ALG", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Security - Password Policy
    min_password_length: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
    require_special_chars: bool = os.getenv("REQUIRE_SPECIAL_CHARS", "true").lower() == "true"
    require_uppercase: bool = os.getenv("REQUIRE_UPPERCASE", "true").lower() == "true"
    require_numbers: bool = os.getenv("REQUIRE_NUMBERS", "true").lower() == "true"

    # Security - Session
    session_cookie_secure: bool = os.getenv("SESSION_COOKIE_SECURE", "true").lower() == "true"
    session_cookie_httponly: bool = os.getenv("SESSION_COOKIE_HTTPONLY", "true").lower() == "true"
    session_cookie_samesite: str = os.getenv("SESSION_COOKIE_SAMESITE", "strict")

    # Security - CSRF
    csrf_secret: str = os.getenv("CSRF_SECRET", "csrf-secret-key-change-in-production")
    csrf_token_expire_minutes: int = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", "60"))

    # Security - API Key
    api_key_enabled: bool = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    api_key_secret: str = os.getenv("API_KEY_SECRET", "api-key-secret")

    # Security - Headers
    send_x_powered_by: bool = os.getenv("SEND_X_POWERED_BY", "false").lower() == "true"
    powered_by_header: str = os.getenv("POWERED_BY_HEADER", "Inventario-Backend")
    security_headers: dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    }

    # Content Security Policy (optional)
    csp_enabled: bool = os.getenv("CSP_ENABLED", "false").lower() == "true"
    csp_default: str = os.getenv(
        "CSP_DEFAULT", "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    )

    # CORS
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = [
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "X-API-Key",
        "X-CSRF-Token",
        "X-Request-Id",
    ]
    cors_expose_headers: list[str] = [
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Window",
        "X-RateLimit-Reset",
        "X-Request-Id",
    ]
    cors_max_age: int = 600
    # Allow regex origins (useful for custom schemes like capacitor://localhost)
    cors_allow_origin_regex: str | None = os.getenv("CORS_ALLOW_ORIGIN_REGEX")

    # CORS & Hosts - Environment Specific
    cors_origins_development: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        # Vite (React) default dev server
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    cors_origins_production: list[str] = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://api.yourdomain.com",
    ]
    # Trusted hosts - usar wildcard por defecto para evitar bloqueos`n    trusted_hosts: list[str] = ["*"]

    # Rate limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    endpoint_rate_limits: dict[str, dict[str, int]] = {}
    # Optional Redis backend for rate limiting
    rate_limit_use_redis: bool = os.getenv("RATE_LIMIT_USE_REDIS", "false").lower() == "true"
    rate_limit_redis_prefix: str = os.getenv("RATE_LIMIT_REDIS_PREFIX", "ratelimit")

    # Logging
    log_file: str = os.getenv("LOG_FILE", "logs/inventario.log")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_json_format: bool = os.getenv("LOG_JSON_FORMAT", "true").lower() == "true"
    log_max_file_size: int = int(os.getenv("LOG_MAX_FILE_SIZE", str(10 * 1024 * 1024)))
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    log_levels: dict[str, str] = {
        "app.core.database": "INFO",
        "sqlalchemy.engine": "WARNING",
        "sqlalchemy.pool": "WARNING",
        "uvicorn": "WARNING",
    }

    # Redis and caching
    redis_host: str | None = os.getenv("REDIS_HOST")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: str | None = os.getenv("REDIS_PASSWORD")
    redis_socket_timeout: float = float(os.getenv("REDIS_SOCKET_TIMEOUT", "1.0"))
    # Health check socket timeout for Redis (used in /health/detailed)
    redis_health_timeout: float = float(os.getenv("REDIS_HEALTH_TIMEOUT", "1.0"))

    # SMTP / Email
    smtp_host: str | None = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    alert_emails: list[str] = []

    # Scheduler
    scheduler_enabled: bool = os.getenv("SCHEDULER_ENABLED", "false").lower() == "true"
    scheduler_interval_hours: int = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "24"))
    scheduler_timezone: str = os.getenv("SCHEDULER_TIMEZONE", "UTC")

    # Password reset
    password_reset_expire_minutes: int = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "15"))

    # Health/Monitoring toggles
    health_check_enabled: bool = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
    db_health_check_enabled: bool = os.getenv("DB_HEALTH_CHECK_ENABLED", "true").lower() == "true"
    redis_health_check_enabled: bool = (
        os.getenv("REDIS_HEALTH_CHECK_ENABLED", "false").lower() == "true"
    )
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"
    metrics_enabled: bool = os.getenv("METRICS_ENABLED", "false").lower() == "true"
    backup_enabled: bool = os.getenv("BACKUP_ENABLED", "false").lower() == "true"
    ssl_enabled: bool = os.getenv("SSL_ENABLED", "false").lower() == "true"
    # External services health checks configuration placeholder
    external_services_health: list[dict[str, Any]] = []

    # Pydantic settings model config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def model_post_init(self, __context: Any) -> None:
        # Normalize to sync driver always (avoid async/sync conflicts in runtime)
        if self.database_url.startswith("postgresql+asyncpg://"):
            self.database_url = self.database_url.replace(
                "postgresql+asyncpg://", "postgresql+psycopg2://", 1
            )

        # For tests, also convert plain postgresql to psycopg2
        if os.getenv("TESTING") == "true":
            if self.database_url.startswith("postgresql://"):
                self.database_url = self.database_url.replace(
                    "postgresql://", "postgresql+psycopg2://", 1
                )
            # Add testserver to trusted hosts for testing
            if "testserver" not in self.trusted_hosts:
                self.trusted_hosts.append("testserver")

        # Set connect_args based on database type
        if self.database_url.startswith("sqlite"):
            self.db_connect_args = {"check_same_thread": False}
        else:
            self.db_connect_args = {
                "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
                "application_name": os.getenv("DB_APP_NAME", "InventarioBackend"),
                "options": os.getenv("DB_PG_OPTIONS", "-c statement_timeout=30s"),
            }

        # Parse env-driven overrides for lists (comma-separated)
        cors_env = os.getenv("CORS_ORIGINS")
        hosts_env = os.getenv("TRUSTED_HOSTS")
        if cors_env:
            parsed = [o.strip() for o in cors_env.split(",") if o.strip()]
            if parsed:
                self.cors_origins = parsed
        if hosts_env:
            # Accept either JSON array or comma-separated list
            parsed: list[str] = []
            try:
                maybe = json.loads(hosts_env)
                if isinstance(maybe, list):
                    parsed = [str(h).strip() for h in maybe if str(h).strip()]
            except Exception:
                parsed = [h.strip() for h in hosts_env.split(",") if h.strip()]

            if parsed:
                self.trusted_hosts = parsed

        # Parse alert emails for notifications (comma-separated)
        emails_env = os.getenv("ALERT_EMAILS")
        if emails_env:
            parsed_emails = [e.strip() for e in emails_env.split(",") if e.strip()]
            if parsed_emails:
                self.alert_emails = parsed_emails

        # Dynamic CORS origins based on environment
        if self.environment.lower() == "production":
            self._cors_origins = self.cors_origins_production
        else:
            self._cors_origins = self.cors_origins_development

        # Optionally add LAN origin for mobile testing
        # Example: set LOCAL_DEV_IP=192.168.1.50 and (optional) DEV_CLIENT_PORT=5173
        local_ip = os.getenv("LOCAL_DEV_IP")
        dev_client_port = os.getenv("DEV_CLIENT_PORT", "5173")
        if local_ip:
            lan_origin = f"http://{local_ip}:{dev_client_port}"
            if lan_origin not in self._cors_origins:
                self._cors_origins.append(lan_origin)

        # Trusted hosts (Host header) for local/mobile testing
        if self.environment.lower() != "production":
            # Allow all hosts in development unless explicitly overridden
            if os.getenv("ALLOW_ALL_HOSTS_DEV", "true").lower() == "true":
                self.trusted_hosts = ["*"]
            else:
                # Optionally add a specific LAN IP or hostname
                backend_host = os.getenv("LOCAL_BACKEND_HOST")
                if backend_host and backend_host not in self.trusted_hosts:
                    self.trusted_hosts.append(backend_host)

        # In development, optionally allow mobile app schemes via regex
        if self.environment.lower() != "production":
            if os.getenv("ALLOW_MOBILE_SCHEMES_DEV", "true").lower() == "true":
                # Accept http/https plus capacitor/ionic local origins
                default_regex = r"^(https?://.*|capacitor://localhost|ionic://localhost)$"
                # Only set if not explicitly provided by env
                if not self.cors_allow_origin_regex:
                    self.cors_allow_origin_regex = default_regex

        # Validate critical security settings
        if self.environment.lower() == "production" and len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long in production")

        if self.environment.lower() == "production" and not self.ssl_enabled:
            # Only a warning in production if SSL disabled
            import warnings
            warnings.warn("SSL is not enabled in production environment")

        # Conditionally apply HSTS only when SSL is enabled
        if not self.ssl_enabled and "Strict-Transport-Security" in self.security_headers:
            self.security_headers.pop("Strict-Transport-Security", None)
        elif self.ssl_enabled:
            self.security_headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Apply Content-Security-Policy header if enabled
        if getattr(self, "csp_enabled", False):
            self.security_headers["Content-Security-Policy"] = getattr(
                self, "csp_default", "default-src 'self'; frame-ancestors 'none'; base-uri 'self'"
            )
        else:
            self.security_headers.pop("Content-Security-Policy", None)

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS origins based on environment"""
        return getattr(self, "_cors_origins", self.cors_origins_development)

    @cors_origins.setter
    def cors_origins(self, value: list[str]):
        """Set CORS origins (explicit override)"""
        self._cors_origins = value

    def get_redis_url(self) -> str:
        """Build Redis URL from components"""
        auth = ""
        if self.redis_password:
            auth = f":{self.redis_password}@"
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_log_level(self, module_name: str) -> str:
        """Get log level for specific module"""
        return self.log_levels.get(module_name, self.log_level)


settings = Settings()

