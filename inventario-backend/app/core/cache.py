"""
Sistema de caché con Redis para mejorar performance
"""

import hashlib
import inspect
import json
from collections.abc import Callable
from functools import wraps
from typing import Any, cast

import redis

from app.core.config import settings
from app.core.logging_config import inventario_logger

logger = inventario_logger


class CacheManager:
    """Gestor de caché con Redis"""

    def __init__(self):
        self.redis_client: redis.Redis | None = None
        self.enabled = False
        self._initialize_redis()

    def _initialize_redis(self):
        """Inicializar conexión a Redis"""
        if not settings.redis_host:
            logger.log_warning("Redis host not configured, cache disabled")
            return

        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_timeout,
                decode_responses=True,
                retry_on_timeout=True,
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.log_info("Redis cache initialized successfully")
        except Exception as e:
            logger.log_warning(f"Failed to connect to Redis: {e}. Cache disabled.")
            self.redis_client = None
            self.enabled = False

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generar clave de caché única basada en argumentos"""
        # Crear string único con los argumentos
        key_parts = [prefix]

        # Agregar args
        for arg in args:
            if hasattr(arg, '__dict__'):
                # Para objetos, usar su representación
                key_parts.append(str(arg.__class__.__name__))
            else:
                key_parts.append(str(arg))

        # Agregar kwargs ordenados
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        # Crear hash para claves muy largas
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"

        return key_string

    def get(self, key: str) -> Any | None:
        """Obtener valor del caché"""
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = cast(str | None, self.redis_client.get(key))
            if value is not None and value != "":
                logger.log_info(f"Cache HIT: {key}")
                try:
                    return json.loads(value)
                except Exception:
                    # Si no es JSON válido, retorna como string
                    return value
            logger.log_info(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.log_error(e, {"context": "cache_get", "key": key})
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Guardar valor en caché con TTL opcional (en segundos)"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            serialized = json.dumps(value, default=str)
            if ttl:
                self.redis_client.setex(key, ttl, serialized)
            else:
                self.redis_client.set(key, serialized)
            logger.log_info(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.log_error(e, {"context": "cache_set", "key": key})
            return False

    def delete(self, key: str) -> bool:
        """Eliminar clave del caché"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            logger.log_info(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.log_error(e, {"context": "cache_delete", "key": key})
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Eliminar todas las claves que coincidan con el patrón"""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = cast(list[str], self.redis_client.keys(pattern))
            if keys:
                deleted_raw = self.redis_client.delete(*keys)
                deleted = deleted_raw if isinstance(deleted_raw, int) else 0
                logger.log_info(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.log_error(e, {"context": "cache_delete_pattern", "pattern": pattern})
            return 0

    def clear_all(self) -> bool:
        """Limpiar todo el caché (usar con precaución)"""
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            logger.log_warning("Cache CLEARED: All keys deleted")
            return True
        except Exception as e:
            logger.log_error(e, {"context": "cache_clear_all"})
            return False

    def get_stats(self) -> dict:
        """Obtener estadísticas del caché"""
        if not self.enabled or not self.redis_client:
            return {"enabled": False, "message": "Redis not available"}

        try:
            info = cast(dict, self.redis_client.info("stats"))
            size_raw = self.redis_client.dbsize()
            total_keys = size_raw if isinstance(size_raw, int) else 0
            hits_raw = info.get("keyspace_hits", 0)
            misses_raw = info.get("keyspace_misses", 0)
            hits = hits_raw if isinstance(hits_raw, int) else int(hits_raw or 0)
            misses = misses_raw if isinstance(misses_raw, int) else int(misses_raw or 0)
            denom = hits + misses if (hits + misses) > 0 else 1
            hit_rate = (hits / denom) * 100.0
            return {
                "enabled": True,
                "total_keys": total_keys,
                "hits": hits,
                "misses": misses,
                "hit_rate": hit_rate,
            }
        except Exception as e:
            logger.log_error(e, {"context": "cache_stats"})
            return {"enabled": False, "error": str(e)}

    def _to_sa_dict(self, obj: Any) -> Any:
        """Convierte un objeto SQLAlchemy a dict de forma segura si aplica."""
        try:
            if hasattr(obj, "__table__"):
                return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        except Exception:
            return obj
        return obj

    def _serialize_result(self, result: Any) -> Any:
        """Serializa resultados potencialmente con modelos SQLAlchemy a tipos JSON-serializables."""
        try:
            # Lista o iterable de modelos
            if isinstance(result, list):
                return [self._to_sa_dict(x) for x in result]
            # Un único modelo
            if hasattr(result, "__table__"):
                return {c.name: getattr(result, c.name) for c in result.__table__.columns}
            # Dict/str/num/etc.
            return result
        except Exception:
            return result

    def cache_result(self, ttl: int = 300, key_prefix: str | None = None):
        """
        Decorador para cachear resultados de funciones (sincronas o asíncronas)

        Args:
            ttl: Tiempo de vida en segundos (default: 5 minutos)
            key_prefix: Prefijo personalizado para la clave de caché

        Usage:
            @cache_manager.cache_result(ttl=600, key_prefix="productos")
            def get_productos_list(db, skip, limit):
                return db.query(Producto).offset(skip).limit(limit).all()
        """

        def decorator(func: Callable) -> Callable:
            # Soporte para funciones asíncronas
            if inspect.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    if not self.enabled:
                        return await func(*args, **kwargs)

                    prefix = key_prefix or func.__name__
                    cache_key = self._generate_cache_key(prefix, *args, **kwargs)

                    cached_value = self.get(cache_key)
                    if cached_value is not None:
                        return cached_value

                    result = await func(*args, **kwargs)
                    serializable_result = self._serialize_result(result)
                    self.set(cache_key, serializable_result, ttl)
                    return result

                return async_wrapper  # type: ignore[return-value]
            else:

                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    if not self.enabled:
                        return func(*args, **kwargs)

                    prefix = key_prefix or func.__name__
                    cache_key = self._generate_cache_key(prefix, *args, **kwargs)

                    cached_value = self.get(cache_key)
                    if cached_value is not None:
                        return cached_value

                    result = func(*args, **kwargs)
                    serializable_result = self._serialize_result(result)
                    self.set(cache_key, serializable_result, ttl)
                    return result

                return sync_wrapper  # type: ignore[return-value]

        return decorator

    def invalidate_cache(self, patterns: list[str]):
        """
        Decorador para invalidar caché después de operaciones de escritura (sync/async)

        Usage:
            @cache_manager.invalidate_cache(["productos:*", "dashboard:*"])
            def create_producto(db, producto_data):
                ...
        """

        def decorator(func: Callable) -> Callable:
            if inspect.iscoroutinefunction(func):

                @wraps(func)
                async def async_wrapper(*args, **kwargs):
                    result = await func(*args, **kwargs)
                    if self.enabled:
                        for pattern in patterns:
                            self.delete_pattern(pattern)
                    return result

                return async_wrapper  # type: ignore[return-value]
            else:

                @wraps(func)
                def sync_wrapper(*args, **kwargs):
                    result = func(*args, **kwargs)
                    if self.enabled:
                        for pattern in patterns:
                            self.delete_pattern(pattern)
                    return result

                return sync_wrapper  # type: ignore[return-value]

        return decorator


# Instancia global del gestor de caché
cache_manager = CacheManager()


# Funciones de utilidad para uso directo
def get_cache(key: str) -> Any | None:
    """Obtener valor del caché"""
    return cache_manager.get(key)


def set_cache(key: str, value: Any, ttl: int | None = None) -> bool:
    """Guardar valor en caché"""
    return cache_manager.set(key, value, ttl)


def delete_cache(key: str) -> bool:
    """Eliminar clave del caché"""
    return cache_manager.delete(key)


def clear_cache_pattern(pattern: str) -> int:
    """Eliminar claves por patrón"""
    return cache_manager.delete_pattern(pattern)


# Exported symbols for static analyzers
__all__ = [
    "CacheManager",
    "cache_manager",
    "get_cache",
    "set_cache",
    "delete_cache",
    "clear_cache_pattern",
]
