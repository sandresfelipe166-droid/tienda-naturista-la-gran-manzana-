"""
Configuración de logging para el sistema de inventario
"""

import json
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Any

from app.core.config import settings
from app.core.log_context import RequestIdFilter


class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs estructurados"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Agregar request_id si viene en el registro (inyectado por RequestIdFilter)
        req_id: str | None = getattr(record, "request_id", None)
        if req_id:
            log_entry["request_id"] = req_id

        # Agregar información extra si existe (evitar errores de tipado con getattr)
        extra_data: Any | None = getattr(record, "extra_data", None)
        if extra_data is not None:
            try:
                if isinstance(extra_data, dict):
                    clean = sanitize_for_log(extra_data)
                    log_entry.update(clean)
                else:
                    log_entry["extra_data"] = str(extra_data)
            except Exception:
                log_entry["extra_data"] = "unserializable-extra-data"

        # Agregar información de excepción si existe
        if record.exc_info:
            try:
                log_entry["exception"] = self.formatException(record.exc_info)
            except Exception:
                # fallback seguro si formatException falla
                log_entry["exception"] = "unserializable-exception"

        return json.dumps(log_entry, ensure_ascii=False)


class InventarioLogger:
    """Logger personalizado para el sistema de inventario"""

    def __init__(self):
        self.logger = logging.getLogger("inventario")
        self._configured = False
        self.setup_logging()

    def _build_formatter(self) -> logging.Formatter:
        if settings.log_json_format:
            return JSONFormatter()
        return logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    def setup_logging(self):
        """Configurar el sistema de logging"""
        if self._configured:
            return

        # Crear directorio de logs si no existe
        log_file = settings.log_file
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Configurar nivel de logging
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        self.logger.propagate = False  # evitar duplicados al root logger

        # Limpiar handlers existentes
        self.logger.handlers.clear()

        formatter = self._build_formatter()

        # Filtro para inyectar request_id en todos los registros
        request_id_filter = RequestIdFilter()

        # Handler para archivo principal
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=int(settings.log_max_file_size),
            backupCount=int(settings.log_backup_count),
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        file_handler.addFilter(request_id_filter)
        self.logger.addHandler(file_handler)

        # Handler para errores (archivo separado)
        error_file = log_file.replace(".log", "_errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=int(settings.log_max_file_size),
            backupCount=int(settings.log_backup_count),
            encoding="utf-8",
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        error_handler.addFilter(request_id_filter)
        self.logger.addHandler(error_handler)

        # Console handler en modo debug
        if settings.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(level)
            console_handler.addFilter(request_id_filter)
            self.logger.addHandler(console_handler)

        # Niveles por módulo específicos
        for module_name, module_level in settings.log_levels.items():
            try:
                logging.getLogger(module_name).setLevel(
                    getattr(logging, module_level.upper(), level)
                )
            except Exception:
                # Ignorar módulos inválidos
                pass

        self._configured = True

    # Métodos de logging estructurado
    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration: float | None = None,
        query: str | None = None,
    ):
        extra_data: dict[str, Any] = {
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
        }
        if duration is not None:
            extra_data["duration"] = duration
        if query is not None:
            extra_data["query"] = query
        self.logger.info(
            f"DB {operation} on {table}", extra={"extra_data": sanitize_for_log(extra_data)}
        )

    def log_business_event(self, event: str, details: dict[str, Any] | None = None):
        extra_data: dict[str, Any] = {
            "event_type": "business_event",
            "event": event,
            "details": details or {},
        }
        self.logger.info(
            f"Business event: {event}", extra={"extra_data": sanitize_for_log(extra_data)}
        )

    def log_security_event(
        self,
        event: str,
        user_id: int | None = None,
        ip_address: str | None = None,
        **kwargs: Any,
    ):
        extra_data: dict[str, Any] = {
            "event_type": "security_event",
            "event": event,
            "user_id": user_id,
            "ip_address": ip_address,
        }
        extra_data.update(kwargs or {})
        self.logger.warning(
            f"Security event: {event}", extra={"extra_data": sanitize_for_log(extra_data)}
        )

    def log_error(self, error: Exception, context: dict[str, Any] | None = None):
        extra_data: dict[str, Any] = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "context": context or {},
        }
        self.logger.error(
            f"Error: {str(error)}",
            extra={"extra_data": sanitize_for_log(extra_data)},
            exc_info=True,
        )

    # Métodos de compatibilidad y conveniencia
    def log_info(self, message: str, extra_data: dict[str, Any] | None = None):
        self.logger.info(message, extra={"extra_data": sanitize_for_log(extra_data or {})})

    def log_warning(self, message: str, extra_data: dict[str, Any] | None = None):
        self.logger.warning(message, extra={"extra_data": sanitize_for_log(extra_data or {})})

    def log_request(
        self,
        method: str,
        path: str,
        user_id: int | None = None,
        ip_address: str | None = None,
        user_agent: str = "",
        request_id: str | None = None,
        **kwargs: Any,
    ):
        extra_data: dict[str, Any] = {
            "event_type": "http_request",
            "method": method,
            "path": path,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }
        if request_id:
            extra_data["request_id"] = request_id
        if kwargs:
            try:
                for k, v in kwargs.items():
                    if k not in extra_data:
                        extra_data[k] = v
            except Exception:
                pass
        self.logger.info(f"{method} {path}", extra={"extra_data": sanitize_for_log(extra_data)})


def sanitize_for_log(obj: Any) -> Any:
    """Sanitiza objetos para logging JSON: convierte objetos no serializables a str
    y redacta campos sensibles.

    Rules:
    - Si es dict, procesar recursivamente.
    - Si es lista/tuple, procesar elementos.
    - Redactar keys que contengan palabras sensibles.
    - Para objetos desconocidos, devolver str(obj).
    """
    SENSITIVE_KEYS = {
        "password",
        "secret",
        "token",
        "authorization",
        "api_key",
        "api-key",
        "secret_key",
    }

    def _is_sensitive_key(k: str) -> bool:
        kl = k.lower()
        return any(s in kl for s in SENSITIVE_KEYS)

    try:
        if obj is None:
            return obj
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                try:
                    if isinstance(k, str) and _is_sensitive_key(k):
                        out[k] = "[REDACTED]"
                    else:
                        out[k] = sanitize_for_log(v)
                except Exception:
                    out[str(k)] = "[UNSERIALIZABLE_KEY]"
            return out
        if isinstance(obj, (list, tuple)):  # noqa: UP038 - tuple required by isinstance
            return [sanitize_for_log(v) for v in obj]
        # JSON serializable primitives
        if isinstance(obj, (str, int, float, bool)):  # noqa: UP038 - tuple required by isinstance
            return obj
        # Fallback: convertir a str
        return str(obj)
    except Exception:
        return "[UNSERIALIZABLE]"


# Instancia global del logger
inventario_logger = InventarioLogger()


def get_logger():
    """Obtener instancia del logger base"""
    return inventario_logger.logger


def setup_uvicorn_logging():
    """Configurar logging para Uvicorn y su access logger"""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")

    uvicorn_logger.setLevel(level)
    # Reducir verbosidad de access log si no estamos en debug
    uvicorn_access_logger.setLevel(logging.WARNING if not settings.debug else level)

    # Adjuntar RequestIdFilter para propagar request_id cuando el formateador lo soporte
    try:
        req_filter = RequestIdFilter()
        uvicorn_logger.addFilter(req_filter)
        uvicorn_access_logger.addFilter(req_filter)
    except Exception:
        # No romper si no puede agregar filtros
        pass
