"""
Tests de integración para Redis Cache Manager

Valida:
- Operaciones básicas (get/set/delete)
- Decoradores (@cache_result, @invalidate_cache)
- Invalidación de caché por patrones
- Serialización de modelos SQLAlchemy
- Performance y TTL

Ejecutar:
    pytest tests/test_cache_integration.py -v

Nota: Requiere Redis corriendo en localhost:6379
"""

import pytest
import time
from unittest.mock import MagicMock

from app.core.cache import cache_manager, CacheManager
from app.models.models import Producto


@pytest.fixture
def redis_cache():
    """
    Fixture para limpiar cache entre tests y asegurar que Redis está habilitado
    """
    # Marcar como test de integración si Redis no está disponible
    if not cache_manager.enabled:
        pytest.skip("Redis no está disponible para estos tests")
    
    # Verificar conexión con timeout
    try:
        if cache_manager.redis_client:
            cache_manager.redis_client.ping()
    except Exception as e:
        pytest.skip(f"Redis no responde: {e}")
    
    # Limpiar cache antes del test
    cache_manager.clear_all()
    yield cache_manager
    # Limpiar cache después del test
    cache_manager.clear_all()


@pytest.fixture
def mock_producto():
    """
    Fixture para crear un producto mock para testing
    """
    producto = MagicMock(spec=Producto)
    producto.id_producto = 1
    producto.nombre_producto = "Test Producto"
    producto.precio_venta = 100.0
    producto.stock_actual = 50
    producto.estado = "Activo"
    
    # Mock de __table__ para serialización
    producto.__table__ = MagicMock()
    producto.__table__.columns = [
        MagicMock(name="id_producto"),
        MagicMock(name="nombre_producto"),
        MagicMock(name="precio_venta"),
        MagicMock(name="stock_actual"),
        MagicMock(name="estado"),
    ]
    
    return producto


@pytest.mark.integration
class TestCacheBasicOperations:
    """Tests para operaciones básicas del cache"""
    
    def test_cache_set_and_get(self, redis_cache):
        """Test básico de set/get"""
        key = "test:producto:1"
        value = {"id": 1, "nombre": "Test Producto", "precio": 100.0}
        
        # Set cache
        result = redis_cache.set(key, value, ttl=60)
        assert result is True
        
        # Get cache
        cached = redis_cache.get(key)
        assert cached == value
        assert cached["id"] == 1
        assert cached["nombre"] == "Test Producto"
    
    def test_cache_get_nonexistent_key(self, redis_cache):
        """Test get de clave inexistente"""
        cached = redis_cache.get("nonexistent:key")
        assert cached is None
    
    def test_cache_delete(self, redis_cache):
        """Test de eliminación de cache"""
        key = "test:producto:2"
        value = {"id": 2, "nombre": "Producto a eliminar"}
        
        # Set y verificar
        redis_cache.set(key, value, ttl=60)
        assert redis_cache.get(key) == value
        
        # Eliminar
        result = redis_cache.delete(key)
        assert result is True
        
        # Verificar eliminación
        assert redis_cache.get(key) is None
    
    def test_cache_ttl_expiration(self, redis_cache):
        """Test de expiración de TTL"""
        key = "test:ttl:1"
        value = {"data": "temporal"}
        
        # Set con TTL de 1 segundo
        redis_cache.set(key, value, ttl=1)
        assert redis_cache.get(key) == value
        
        # Esperar expiración
        time.sleep(1.5)
        
        # Verificar que expiró
        assert redis_cache.get(key) is None


@pytest.mark.integration
class TestCachePatternOperations:
    """Tests para operaciones con patrones"""
    
    def test_delete_pattern_single_match(self, redis_cache):
        """Test de eliminación por patrón con una coincidencia"""
        redis_cache.set("productos:1", {"id": 1}, ttl=300)
        redis_cache.set("ventas:1", {"id": 1}, ttl=300)
        
        # Eliminar solo productos
        deleted = redis_cache.delete_pattern("productos:*")
        assert deleted == 1
        
        # Verificar que solo productos fue eliminado
        assert redis_cache.get("productos:1") is None
        assert redis_cache.get("ventas:1") is not None
    
    def test_delete_pattern_multiple_matches(self, redis_cache):
        """Test de eliminación por patrón con múltiples coincidencias"""
        # Crear múltiples claves con el mismo patrón
        redis_cache.set("productos:1", {"id": 1}, ttl=300)
        redis_cache.set("productos:2", {"id": 2}, ttl=300)
        redis_cache.set("productos:3", {"id": 3}, ttl=300)
        redis_cache.set("ventas:1", {"id": 1}, ttl=300)
        
        # Eliminar todos los productos
        deleted = redis_cache.delete_pattern("productos:*")
        assert deleted == 3
        
        # Verificar que productos fueron eliminados pero ventas permanece
        assert redis_cache.get("productos:1") is None
        assert redis_cache.get("productos:2") is None
        assert redis_cache.get("productos:3") is None
        assert redis_cache.get("ventas:1") is not None
    
    def test_delete_pattern_no_matches(self, redis_cache):
        """Test de eliminación por patrón sin coincidencias"""
        redis_cache.set("productos:1", {"id": 1}, ttl=300)
        
        # Intentar eliminar patrón inexistente
        deleted = redis_cache.delete_pattern("categorias:*")
        assert deleted == 0
        
        # Verificar que productos sigue existiendo
        assert redis_cache.get("productos:1") is not None


@pytest.mark.integration
class TestCacheDecorator:
    """Tests para decorador @cache_result"""
    
    def test_cache_result_decorator_sync(self, redis_cache):
        """Test del decorador @cache_result con función síncrona"""
        call_count = 0
        
        @redis_cache.cache_result(ttl=60, key_prefix="test_func")
        def expensive_operation(value: int):
            nonlocal call_count
            call_count += 1
            return {"result": value * 2}
        
        # Primera llamada - debe ejecutar función
        result1 = expensive_operation(5)
        assert result1 == {"result": 10}
        assert call_count == 1
        
        # Segunda llamada - debe usar cache
        result2 = expensive_operation(5)
        assert result2 == {"result": 10}
        assert call_count == 1  # No se incrementó
        
        # Llamada con argumento diferente - debe ejecutar función
        result3 = expensive_operation(10)
        assert result3 == {"result": 20}
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cache_result_decorator_async(self, redis_cache):
        """Test del decorador @cache_result con función asíncrona"""
        call_count = 0
        
        @redis_cache.cache_result(ttl=60, key_prefix="test_async")
        async def async_expensive_operation(value: int):
            nonlocal call_count
            call_count += 1
            return {"result": value * 3}
        
        # Primera llamada
        result1 = await async_expensive_operation(5)
        assert result1 == {"result": 15}
        assert call_count == 1
        
        # Segunda llamada - debe usar cache
        result2 = await async_expensive_operation(5)
        assert result2 == {"result": 15}
        assert call_count == 1


@pytest.mark.integration
class TestCacheInvalidation:
    """Tests para invalidación de cache"""
    
    def test_invalidate_cache_decorator_sync(self, redis_cache):
        """Test del decorador @invalidate_cache con función síncrona"""
        # Cachear datos
        redis_cache.set("productos:1", {"nombre": "Old"}, ttl=300)
        redis_cache.set("productos:2", {"nombre": "Old"}, ttl=300)
        redis_cache.set("dashboard:stats", {"total": 100}, ttl=300)
        
        # Verificar cache
        assert redis_cache.get("productos:1") is not None
        assert redis_cache.get("dashboard:stats") is not None
        
        @redis_cache.invalidate_cache(["productos:*", "dashboard:*"])
        def update_producto():
            return {"status": "updated"}
        
        # Ejecutar función que invalida cache
        result = update_producto()
        assert result == {"status": "updated"}
        
        # Verificar que cache fue invalidado
        assert redis_cache.get("productos:1") is None
        assert redis_cache.get("productos:2") is None
        assert redis_cache.get("dashboard:stats") is None
    
    @pytest.mark.asyncio
    async def test_invalidate_cache_decorator_async(self, redis_cache):
        """Test del decorador @invalidate_cache con función asíncrona"""
        # Cachear datos
        redis_cache.set("ventas:1", {"total": 500}, ttl=300)
        
        @redis_cache.invalidate_cache(["ventas:*"])
        async def create_venta():
            return {"id": 2, "total": 1000}
        
        # Verificar cache antes
        assert redis_cache.get("ventas:1") is not None
        
        # Ejecutar función
        result = await create_venta()
        assert result == {"id": 2, "total": 1000}
        
        # Verificar invalidación
        assert redis_cache.get("ventas:1") is None


@pytest.mark.integration
class TestCacheStats:
    """Tests para estadísticas del cache"""
    
    def test_get_stats(self, redis_cache):
        """Test de obtención de estadísticas"""
        # Realizar operaciones
        redis_cache.set("test:1", {"data": 1}, ttl=60)
        redis_cache.set("test:2", {"data": 2}, ttl=60)
        redis_cache.get("test:1")  # Hit
        redis_cache.get("test:nonexistent")  # Miss
        
        # Obtener stats
        stats = redis_cache.get_stats()
        
        assert stats["enabled"] is True
        assert stats["total_keys"] >= 2
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats


@pytest.mark.integration
class TestCacheSerialization:
    """Tests para serialización de modelos SQLAlchemy"""
    
    def test_serialize_sqlalchemy_model(self, redis_cache, mock_producto):
        """Test de serialización de modelo SQLAlchemy"""
        # Intentar cachear un "modelo" SQLAlchemy
        key = "producto:serialized:1"
        
        # El cache manager debe serializar automáticamente
        result = redis_cache.set(key, mock_producto, ttl=60)
        assert result is True
        
        # Recuperar debe devolver dict
        cached = redis_cache.get(key)
        # Como es un mock, el comportamiento puede variar
        # Lo importante es que no lance excepciones
        assert cached is not None
    
    def test_serialize_list_of_models(self, redis_cache):
        """Test de serialización de lista de modelos"""
        productos = [
            {"id": 1, "nombre": "Producto 1"},
            {"id": 2, "nombre": "Producto 2"},
            {"id": 3, "nombre": "Producto 3"},
        ]
        
        key = "productos:list"
        redis_cache.set(key, productos, ttl=60)
        
        cached = redis_cache.get(key)
        assert cached == productos
        assert len(cached) == 3


class TestCacheDisabled:
    """Tests para comportamiento cuando Redis está deshabilitado"""
    
    def test_operations_when_disabled(self):
        """Test de operaciones cuando cache está deshabilitado"""
        # Crear instancia sin Redis
        disabled_cache = CacheManager()
        disabled_cache.enabled = False
        disabled_cache.redis_client = None
        
        # Todas las operaciones deben fallar gracefully
        assert disabled_cache.get("any:key") is None
        assert disabled_cache.set("any:key", {"data": 1}) is False
        assert disabled_cache.delete("any:key") is False
        assert disabled_cache.delete_pattern("any:*") == 0
        
        stats = disabled_cache.get_stats()
        assert stats["enabled"] is False


@pytest.mark.integration
class TestCachePerformance:
    """Tests de performance del cache"""
    
    def test_cache_performance_improvement(self, redis_cache):
        """Verificar que el cache mejora la performance"""
        call_count = 0
        
        @redis_cache.cache_result(ttl=60, key_prefix="perf_test")
        def slow_operation():
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simular operación lenta
            return {"data": "heavy computation"}
        
        # Primera llamada - lenta
        start = time.time()
        result1 = slow_operation()
        duration1 = time.time() - start
        
        # Segunda llamada - debe ser mucho más rápida
        start = time.time()
        result2 = slow_operation()
        duration2 = time.time() - start
        
        assert result1 == result2
        assert call_count == 1  # Solo se ejecutó una vez
        assert duration2 < duration1 / 2  # Al menos 2x más rápido


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
