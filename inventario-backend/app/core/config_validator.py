"""
Validador de configuración en tiempo de inicio.

Este módulo verifica la consistencia de la configuración antes de que la aplicación inicie,
previniendo errores en producción causados por configuraciones incorrectas.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Excepción lanzada cuando la configuración es inválida."""

    pass


class ConfigValidator:
    """Validador de configuración de aplicación."""

    def __init__(self, settings: Any):
        """
        Inicializar validador con settings.

        Args:
            settings: Objeto Settings de la aplicación
        """
        self.settings = settings
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_all(self, strict: bool = False) -> bool:
        """
        Ejecutar todas las validaciones.

        Args:
            strict: Si es True, los warnings también causan fallo

        Returns:
            bool: True si la configuración es válida

        Raises:
            ConfigValidationError: Si hay errores de configuración
        """
        self.errors = []
        self.warnings = []

        # Validaciones críticas
        self._validate_secret_keys()
        self._validate_database_config()
        self._validate_cors_config()
        self._validate_rate_limiting()
        self._validate_email_config()
        self._validate_paths()
        self._validate_redis_config()

        # Warnings de producción
        if self.settings.environment.lower() == "production":
            self._validate_production_settings()

        # Reportar resultados
        if self.errors:
            error_msg = "\n".join([f"  - {err}" for err in self.errors])
            raise ConfigValidationError(
                f"Errores de configuración encontrados:\n{error_msg}\n\n"
                "La aplicación no puede iniciar con estos errores."
            )

        if self.warnings:
            warning_msg = "\n".join([f"  - {warn}" for warn in self.warnings])
            logger.warning(f"Advertencias de configuración:\n{warning_msg}")
            if strict:
                raise ConfigValidationError(
                    f"Modo estricto: Advertencias tratadas como errores:\n{warning_msg}"
                )

        return True

    def _validate_secret_keys(self) -> None:
        """Validar que las secret keys sean seguras."""
        # SECRET_KEY
        if not self.settings.secret_key or len(self.settings.secret_key) < 32:
            self.errors.append(
                "SECRET_KEY debe tener al menos 32 caracteres. "
                "Genera una clave segura con: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        if "dev-secret" in self.settings.secret_key.lower():
            if self.settings.environment.lower() == "production":
                self.errors.append(
                    "SECRET_KEY contiene 'dev-secret' en producción. "
                    "Esto es altamente inseguro. Genera una nueva clave."
                )
            else:
                self.warnings.append("SECRET_KEY parece ser una clave de desarrollo")

        # CSRF Secret
        if not self.settings.csrf_secret or len(self.settings.csrf_secret) < 32:
            self.errors.append("CSRF_SECRET debe tener al menos 32 caracteres")

        if self.settings.secret_key == self.settings.csrf_secret:
            self.warnings.append(
                "SECRET_KEY y CSRF_SECRET son idénticos. "
                "Se recomienda usar claves diferentes para cada propósito."
            )

    def _validate_database_config(self) -> None:
        """Validar configuración de base de datos."""
        if not self.settings.database_url:
            self.errors.append("DATABASE_URL no está configurado")
            return

        # Validar formato
        if not any(
            self.settings.database_url.startswith(prefix)
            for prefix in ["postgresql://", "postgresql+psycopg2://", "sqlite://"]
        ):
            self.errors.append(
                f"DATABASE_URL tiene formato inválido: {self.settings.database_url[:20]}... "
                "Debe iniciar con postgresql://, postgresql+psycopg2://, o sqlite://"
            )

        # Warning si usa SQLite en producción
        if (
            self.settings.database_url.startswith("sqlite")
            and self.settings.environment.lower() == "production"
        ):
            self.warnings.append(
                "Usando SQLite en producción. Se recomienda PostgreSQL para producción."
            )

        # Validar pool settings
        if self.settings.db_pool_size < 5:
            self.warnings.append(
                f"DB_POOL_SIZE={self.settings.db_pool_size} es muy bajo. "
                "Recomendado: 10-20 para producción"
            )

        if self.settings.db_pool_size > 100:
            self.warnings.append(
                f"DB_POOL_SIZE={self.settings.db_pool_size} es muy alto. "
                "Podría causar sobrecarga en la base de datos."
            )

    def _validate_cors_config(self) -> None:
        """Validar configuración de CORS."""
        cors_origins = self.settings.cors_origins

        if not cors_origins:
            self.warnings.append(
                "CORS_ORIGINS está vacío. La API no será accesible desde navegadores."
            )

        # Warning si CORS permite todo
        if "*" in cors_origins:
            if self.settings.environment.lower() == "production":
                self.errors.append(
                    "CORS_ORIGINS='*' en producción es un riesgo de seguridad. "
                    "Especifica dominios explícitos."
                )
            else:
                self.warnings.append("CORS permite todos los orígenes (*). Esto es inseguro.")

        # Validar que los orígenes tengan protocolo
        for origin in cors_origins:
            if origin != "*" and not origin.startswith(("http://", "https://")):
                self.errors.append(
                    f"Origen CORS inválido: '{origin}'. Debe incluir protocolo (http:// o https://)"
                )

    def _validate_rate_limiting(self) -> None:
        """Validar configuración de rate limiting."""
        if self.settings.rate_limit_requests <= 0:
            self.errors.append("RATE_LIMIT_REQUESTS debe ser mayor a 0")

        if self.settings.rate_limit_window <= 0:
            self.errors.append("RATE_LIMIT_WINDOW debe ser mayor a 0")

        if self.settings.rate_limit_requests > 10000:
            self.warnings.append(
                f"RATE_LIMIT_REQUESTS={self.settings.rate_limit_requests} es muy alto. "
                "¿Estás seguro?"
            )

    def _validate_email_config(self) -> None:
        """Validar configuración de email."""
        if self.settings.scheduler_enabled and self.settings.alert_emails:
            # Si scheduler está habilitado y hay emails, validar SMTP
            if not self.settings.smtp_host:
                self.warnings.append(
                    "scheduler_enabled=True y alert_emails configurados, "
                    "pero SMTP_HOST no está configurado. Las alertas por email no funcionarán."
                )

            if not self.settings.smtp_user or not self.settings.smtp_password:
                self.warnings.append("SMTP_USER o SMTP_PASSWORD no configurados")

    def _validate_paths(self) -> None:
        """Validar que los directorios necesarios existan."""
        # Directorio de logs
        log_dir = Path(self.settings.log_file).parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"Directorio de logs creado: {log_dir}")
            except Exception as e:
                self.errors.append(f"No se puede crear directorio de logs {log_dir}: {e}")

    def _validate_redis_config(self) -> None:
        """Validar configuración de Redis."""
        if self.settings.rate_limit_use_redis and not self.settings.redis_host:
            self.errors.append(
                "rate_limit_use_redis=True pero REDIS_HOST no está configurado. "
                "Configura Redis o desactiva rate_limit_use_redis."
            )

        if self.settings.redis_health_check_enabled and not self.settings.redis_host:
            self.warnings.append(
                "redis_health_check_enabled=True pero REDIS_HOST no configurado. "
                "El health check de Redis fallará."
            )

    def _validate_production_settings(self) -> None:
        """Validaciones específicas para producción."""
        if self.settings.debug:
            self.errors.append(
                "DEBUG=True en producción es un riesgo de seguridad. "
                "Desactiva DEBUG en producción."
            )

        if not self.settings.ssl_enabled:
            self.warnings.append(
                "SSL_ENABLED=False en producción. HTTPS es altamente recomendado."
            )

        if self.settings.session_cookie_secure and not self.settings.ssl_enabled:
            self.warnings.append(
                "session_cookie_secure=True pero ssl_enabled=False. "
                "Las cookies seguras requieren HTTPS."
            )

        # Validar que access token no expire demasiado rápido ni lento
        if self.settings.access_token_expire_minutes < 5:
            self.warnings.append(
                f"access_token_expire_minutes={self.settings.access_token_expire_minutes} "
                "es muy corto. Los usuarios tendrán que re-autenticarse frecuentemente."
            )

        if self.settings.access_token_expire_minutes > 120:
            self.warnings.append(
                f"access_token_expire_minutes={self.settings.access_token_expire_minutes} "
                "es muy largo. Considera reducirlo por seguridad."
            )


def validate_config_on_startup(settings: Any, strict: bool = False) -> None:
    """
    Validar configuración al iniciar la aplicación.

    Args:
        settings: Objeto Settings
        strict: Si es True, warnings causan fallo

    Raises:
        ConfigValidationError: Si la configuración es inválida
    """
    validator = ConfigValidator(settings)

    try:
        validator.validate_all(strict=strict)
        logger.info("✓ Validación de configuración exitosa")
    except ConfigValidationError as e:
        logger.error(f"✗ Error en validación de configuración:\n{e}")
        if os.getenv("TESTING") != "true":
            # En tests no queremos que falle por config
            sys.exit(1)
        raise


if __name__ == "__main__":
    # Para testing manual
    from app.core.config import settings

    validate_config_on_startup(settings, strict=False)
    print("✓ Configuración válida")
