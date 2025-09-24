from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Dict, Any
import os

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+psycopg2://admin:admin123@localhost:5432/inventario"
    db_host: Optional[str] = None
    db_port: int = 5432
    db_name: str = "inventario"
    db_user: str = "admin"
    db_password: str = "admin123"

    # Database - Advanced Pool Configuration
    db_pool_size: int = 20
    db_max_overflow: int = 30
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600
    db_connect_args: Dict[str, Any] = {
        "connect_timeout": 10,
        "application_name": "InventarioBackend",
        "options": "-c statement_timeout=30s"
    }

    # Security - JWT
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-123456789")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Security - Password Policy
    min_password_length: int = 8
    require_special_chars: bool = True
    require_uppercase: bool = True
    require_numbers: bool = True

    # Security - Session
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "strict"

    # Security - CSRF
    csrf_secret: str = os.getenv("CSRF_SECRET", "csrf-secret-key-change-in-production")
    csrf_token_expire_minutes: int = 60

    # Security - API Key
    api_key_enabled: bool = False
    api_key_secret: str = os.getenv("API_KEY_SECRET", "api-key-secret")

    # Security - Headers
    security_headers: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "no-referrer-when-downgrade",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }

    # Server
    port: int = 8000
    host: str = "127.0.0.1"

    # CORS & Hosts - Environment Specific
    cors_origins_development: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000"
    ]

    cors_origins_production: List[str] = [
        "https://yourdomain.com",
        "https://www.yourdomain.com",
        "https://api.yourdomain.com"
    ]

    trusted_hosts: List[str] = ["localhost", "127.0.0.1", "testserver"]

    # CORS Advanced Configuration
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]
    cors_expose_headers: List[str] = ["X-RateLimit-Limit", "X-RateLimit-Remaining"]
    cors_max_age: int = 86400  # 24 horas

    # Rate Limiting - Advanced
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Rate Limiting - Per Endpoint
    endpoint_rate_limits: Dict[str, Dict[str, Dict[str, int]]] = {
        "/api/v1/auth/login": {
            "GET": {"limit": 10, "window": 300},
            "POST": {"limit": 5, "window": 300}
        },
        "/api/v1/productos": {
            "GET": {"limit": 200, "window": 60},
            "POST": {"limit": 50, "window": 60},
            "PUT": {"limit": 30, "window": 60},
            "DELETE": {"limit": 10, "window": 60}
        },
        "/api/v1/users": {
            "GET": {"limit": 100, "window": 60},
            "POST": {"limit": 20, "window": 60},
            "PUT": {"limit": 20, "window": 60},
            "DELETE": {"limit": 5, "window": 60}
        }
    }

    # Logging - Advanced
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_file_size: str = "10MB"
    log_backup_count: int = 10
    log_json_format: bool = True
    log_include_extra: bool = True

    # Logging - External Services
    sentry_dsn: Optional[str] = None
    rollbar_token: Optional[str] = None

    # Logging - Module Levels
    log_levels: Dict[str, str] = {
        "app.core.security": "WARNING",
        "app.core.database": "INFO",
        "uvicorn": "WARNING"
    }

    # Cache - Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    redis_retry_on_timeout: bool = True
    redis_health_check_interval: int = 30

    # Cache - TTL Settings
    cache_ttl_short: int = 300      # 5 minutos
    cache_ttl_medium: int = 1800    # 30 minutos
    cache_ttl_long: int = 7200      # 2 horas
    cache_ttl_products: int = 600   # 10 minutos
    cache_ttl_users: int = 900      # 15 minutos

    # Health Checks
    health_check_enabled: bool = True
    health_check_path: str = "/health"
    health_check_timeout: int = 30

    # Database Health
    db_health_check_enabled: bool = True
    db_health_query_timeout: int = 5

    # Redis Health
    redis_health_check_enabled: bool = True
    redis_health_timeout: int = 3

    # External Services Health
    external_services_health: List[Dict[str, Any]] = []

    # Backup Configuration
    backup_enabled: bool = True
    backup_path: str = "./backups"
    backup_frequency_hours: int = 24
    backup_retention_days: int = 7

    # Cloud Backup
    cloud_backup_enabled: bool = False
    aws_s3_bucket: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    metrics_enabled: bool = True
    metrics_collection_interval: int = 60

    # Alert Configuration
    alerts_enabled: bool = True
    alert_thresholds: Dict[str, Any] = {
        "error_rate": 0.05,      # 5% error rate
        "response_time": 2.0,    # 2 segundos
        "db_connection_errors": 5,
        "memory_usage": 80       # 80% memory
    }

    # Deployment
    docker_enabled: bool = False
    docker_registry: Optional[str] = None
    docker_image_tag: str = "latest"

    # SSL/TLS
    ssl_enabled: bool = False
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Environment-specific configurations
        if self.environment == "production":
            self.debug = False
            self.log_level = "WARNING"
            self.cors_allow_credentials = True
            self.ssl_enabled = True
        elif self.environment == "testing":
            self.debug = True
            self.log_level = "DEBUG"
            self.trusted_hosts.append("testserver")

        # Normalize to sync driver always (avoid async/sync conflicts in runtime)
        if self.database_url.startswith("postgresql+asyncpg://"):
            self.database_url = self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        # For tests, also convert plain postgresql to psycopg2
        if os.getenv("TESTING") == "true":
            if self.database_url.startswith("postgresql://"):
                self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            # Add testserver to trusted hosts for testing
            self.trusted_hosts.append("testserver")

        # Parse env-driven overrides for lists (comma-separated)
        cors_env = os.getenv("CORS_ORIGINS")
        hosts_env = os.getenv("TRUSTED_HOSTS")
        if cors_env:
            self.cors_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
        if hosts_env:
            self.trusted_hosts = [h.strip() for h in hosts_env.split(",") if h.strip()]

        # Dynamic CORS origins based on environment
        if self.environment == "production":
            self.cors_origins = self.cors_origins_production
        else:
            self.cors_origins = self.cors_origins_development

        # Validate critical security settings
        if self.environment == "production" and len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long in production")

        if self.environment == "production" and not self.ssl_enabled:
            print("WARNING: SSL is not enabled in production environment")

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins based on environment"""
        if self.environment == "production":
            return self.cors_origins_production
        return self.cors_origins_development

    @cors_origins.setter
    def cors_origins(self, value: List[str]):
        """Set CORS origins"""
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
