"""
Integración de Sentry para Error Tracking

Este módulo configura Sentry para monitoreo de errores en producción.
Solo se activa en ambiente de producción.

Variables de entorno requeridas:
    SENTRY_DSN: DSN de Sentry (obtener de https://sentry.io)
    ENVIRONMENT: 'production', 'staging', o 'development'
    SENTRY_TRACES_SAMPLE_RATE: Tasa de muestreo (default: 0.1 = 10%)

Uso:
    from app.core.sentry import init_sentry
    
    # En main.py
    init_sentry()
"""

import os

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings
from app.core.logging_config import inventario_logger as logger


def init_sentry() -> None:
    """
    Inicializar Sentry para monitoreo de errores
    
    Solo se activa en producción si SENTRY_DSN está configurado.
    """
    sentry_dsn = os.getenv("SENTRY_DSN")
    
    # No inicializar en desarrollo o si no hay DSN
    if not sentry_dsn:
        logger.log_info("Sentry no configurado (SENTRY_DSN no encontrado)")
        return
    
    if settings.environment.lower() == "development":
        logger.log_info("Sentry deshabilitado en desarrollo")
        return
    
    try:
        # Configuración de Sentry
        traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
        
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=settings.environment,
            # Integraciones
            integrations=[
                FastApiIntegration(
                    transaction_style="url",  # Agrupar por URL
                ),
                SqlalchemyIntegration(),
            ],
            # Performance Monitoring
            traces_sample_rate=traces_sample_rate,
            # Profiles (opcional, requiere plan pago)
            profiles_sample_rate=0.0,  # Deshabilitado por defecto
            # Configuración adicional
            send_default_pii=False,  # No enviar PII por defecto
            attach_stacktrace=True,
            # Release tracking (opcional)
            release=os.getenv("SENTRY_RELEASE", "1.0.0"),
            # Ignorar errores comunes
            ignore_errors=[
                KeyboardInterrupt,
                SystemExit,
            ],
            # Before send hook para filtrar eventos
            before_send=before_send_hook,
        )
        
        logger.log_info(
            f"Sentry inicializado exitosamente (env: {settings.environment}, "
            f"traces_sample_rate: {traces_sample_rate})"
        )
        
    except Exception as e:
        logger.log_error(e, {"context": "sentry_init"})


def before_send_hook(event, hint):
    """
    Hook para filtrar/modificar eventos antes de enviar a Sentry
    
    Casos de uso:
    - Remover información sensible
    - Filtrar errores no importantes
    - Enriquecer eventos con contexto adicional
    """
    # Ejemplo: Filtrar errores de health checks
    if "exception" in event:
        for exception in event["exception"].get("values", []):
            if "health" in str(exception.get("value", "")).lower():
                return None  # No enviar a Sentry
    
    # Ejemplo: Remover datos sensibles de los breadcrumbs
    if "breadcrumbs" in event:
        for breadcrumb in event["breadcrumbs"]:
            if "data" in breadcrumb:
                # Redactar campos sensibles
                sensitive_keys = ["password", "token", "secret", "authorization"]
                for key in sensitive_keys:
                    if key in breadcrumb["data"]:
                        breadcrumb["data"][key] = "[REDACTED]"
    
    return event


def capture_exception(exception: Exception, context: dict = None) -> None:
    """
    Capturar excepción manualmente en Sentry
    
    Args:
        exception: La excepción a capturar
        context: Contexto adicional (dict)
    
    Ejemplo:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e, {"user_id": 123, "operation": "risky"})
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(exception)
    else:
        sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", context: dict = None) -> None:
    """
    Capturar mensaje manualmente en Sentry
    
    Args:
        message: Mensaje a enviar
        level: 'debug', 'info', 'warning', 'error', 'fatal'
        context: Contexto adicional
    
    Ejemplo:
        capture_message("Payment processed successfully", "info", {"amount": 100})
    """
    if context:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level)
    else:
        sentry_sdk.capture_message(message, level)


def set_user_context(user_id: int = None, username: str = None, email: str = None) -> None:
    """
    Establecer contexto de usuario para eventos de Sentry
    
    Args:
        user_id: ID del usuario
        username: Nombre de usuario
        email: Email del usuario
    
    Ejemplo:
        set_user_context(user_id=123, username="john_doe")
    """
    user_data = {}
    if user_id:
        user_data["id"] = user_id
    if username:
        user_data["username"] = username
    if email:
        user_data["email"] = email
    
    if user_data:
        sentry_sdk.set_user(user_data)


def clear_user_context() -> None:
    """Limpiar contexto de usuario (ej: al hacer logout)"""
    sentry_sdk.set_user(None)


# Exportar funciones principales
__all__ = [
    "init_sentry",
    "capture_exception",
    "capture_message",
    "set_user_context",
    "clear_user_context",
]
