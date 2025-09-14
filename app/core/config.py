from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://admin:admin123@localhost:5432/inventario"
    db_host: Optional[str] = None
    db_port: int = 5432
    db_name: str = "inventario"
    db_user: str = "admin"
    db_password: str = "admin123"

    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Server
    debug: bool = True
    port: int = 8000
    host: str = "127.0.0.1"

    # CORS & Hosts
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    trusted_hosts: List[str] = ["localhost", "127.0.0.1"]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # Cache
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl: int = 300

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

settings = Settings()
