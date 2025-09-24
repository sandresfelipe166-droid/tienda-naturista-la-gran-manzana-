"""
Configuración de logging para el sistema de inventario
"""
import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any
import json

from app.core.config import settings


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
            "line": record.lineno
        }
        
        # Agregar información extra si existe
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class InventarioLogger:
    """Logger personalizado para el sistema de inventario"""
    
    def __init__(self):
        self.logger = logging.getLogger("inventario")
        self.setup_logging()
    
    def setup_logging(self):
        """Configurar el sistema de logging"""
        
        # Crear directorio de logs si no existe
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar nivel de logging
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Limpiar handlers existentes
        self.logger.handlers.clear()
        
        # Handler para archivo principal
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(JSONFormatter())
        file_handler.setLevel(level)
        
        # Handler para errores (archivo separado)
        error_file = settings.log_file.replace('.log', '_errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setFormatter(JSONFormatter())
        error_handler.setLevel(logging.ERROR)
        
        # Handler para consola (desarrollo)
        if settings.debug:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(level)
            self.logger.addHandler(console_handler)
        
        # Agregar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        
        # Evitar propagación a root logger
        self.logger.propagate = False
    
    def log_request(self, method: str, path: str, user_id: int = None, **kwargs):
        """Log de solicitudes HTTP"""
        extra_data = {
            "event_type": "http_request",
            "method": method,
            "path": path,
            "user_id": user_id,
            **kwargs
        }
        self.logger.info(f"{method} {path}", extra={"extra_data": extra_data})

    def log_database_operation(self, operation: str, table: str, record_id: int = None, **kwargs):
        """Log de operaciones de base de datos"""
        extra_data = {
            "event_type": "database_operation",
            "operation": operation,
            "table": table,
            "record_id": record_id,
            **kwargs
        }
        self.logger.info(f"DB {operation} on {table}", extra={"extra_data": extra_data})

    def log_business_event(self, event: str, details: Dict[str, Any] = None):
        """Log de eventos de negocio"""
        extra_data = {
            "event_type": "business_event",
            "event": event,
            "details": details or {}
        }
        self.logger.info(f"Business event: {event}", extra={"extra_data": extra_data})

    def log_security_event(self, event: str, user_id: int = None, ip_address: str = None, **kwargs):
        """Log de eventos de seguridad"""
        extra_data = {
            "event_type": "security_event",
            "event": event,
            "user_id": user_id,
            "ip_address": ip_address,
            **kwargs
        }
        self.logger.warning(f"Security event: {event}", extra={"extra_data": extra_data})

    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log de errores con contexto"""
        extra_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "context": context or {}
        }
        self.logger.error(f"Error: {str(error)}", extra={"extra_data": extra_data}, exc_info=True)

    # Métodos de compatibilidad para el script de prueba
    def log_info(self, message: str, extra_data: Dict[str, Any] = None):
        """Log de información (compatibilidad)"""
        self.logger.info(message, extra={"extra_data": extra_data or {}})

    def log_warning(self, message: str, extra_data: Dict[str, Any] = None):
        """Log de advertencia (compatibilidad)"""
        self.logger.warning(message, extra={"extra_data": extra_data or {}})


# Instancia global del logger
inventario_logger = InventarioLogger()


def get_logger():
    """Obtener instancia del logger"""
    return inventario_logger.logger


def setup_uvicorn_logging():
    """Configurar logging para Uvicorn"""
    
    # Configurar uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # Usar el mismo nivel que nuestro logger
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    uvicorn_logger.setLevel(level)
    uvicorn_access_logger.setLevel(level)
    
    # Si no estamos en debug, reducir verbosidad de uvicorn
    if not settings.debug:
        uvicorn_access_logger.setLevel(logging.WARNING)
