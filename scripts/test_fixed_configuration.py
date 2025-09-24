#!/usr/bin/env python3
"""
Script de prueba para verificar las configuraciones corregidas
"""
import sys
import os
import asyncio
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging_config import inventario_logger
import redis

logger = inventario_logger

def test_configuration():
    """Probar configuración avanzada"""
    print("🔧 Probando configuración avanzada...")

    # Test 1: Configuración de seguridad
    print("✅ Configuración de seguridad:")
    print(f"   - Environment: {settings.environment}")
    print(f"   - Debug: {settings.debug}")
    print(f"   - Secret Key Length: {len(settings.secret_key)}")
    print(f"   - SSL Enabled: {settings.ssl_enabled}")
    print(f"   - CORS Origins: {len(settings.cors_origins)}")

    # Test 2: Configuración de base de datos
    print("✅ Configuración de base de datos:")
    print(f"   - Pool Size: {settings.db_pool_size}")
    print(f"   - Max Overflow: {settings.db_max_overflow}")
    print(f"   - Pool Timeout: {settings.db_pool_timeout}")
    print(f"   - Pool Recycle: {settings.db_pool_recycle}")

    # Test 3: Configuración de rate limiting
    print("✅ Configuración de rate limiting:")
    print(f"   - Default Limit: {settings.rate_limit_requests}")
    print(f"   - Default Window: {settings.rate_limit_window}")
    print(f"   - Endpoint Limits: {len(settings.endpoint_rate_limits)}")

    # Test 4: Configuración de logging
    print("✅ Configuración de logging:")
    print(f"   - Log Level: {settings.log_level}")
    print(f"   - Log JSON Format: {settings.log_json_format}")
    print(f"   - Log Max File Size: {settings.log_max_file_size}")
    print(f"   - Log Backup Count: {settings.log_backup_count}")

    # Test 5: Configuración de caché
    print("✅ Configuración de caché:")
    print(f"   - Redis Host: {settings.redis_host}")
    print(f"   - Redis Port: {settings.redis_port}")
    print(f"   - Cache TTL Short: {settings.cache_ttl_short}")
    print(f"   - Cache TTL Medium: {settings.cache_ttl_medium}")

    # Test 6: Health checks
    print("✅ Configuración de health checks:")
    print(f"   - Health Check Enabled: {settings.health_check_enabled}")
    print(f"   - DB Health Check: {settings.db_health_check_enabled}")
    print(f"   - Redis Health Check: {settings.redis_health_check_enabled}")

    print("✅ Todas las configuraciones se cargaron correctamente!")

def test_database_connection():
    """Probar conexión a la base de datos (CORREGIDO)"""
    print("🗄️ Probando conexión a base de datos...")
    try:
        health = db_manager.health_check()
        if health["status"] == "healthy":
            print("✅ Conexión a base de datos exitosa")
            conn_info = db_manager.get_connection_info()
            print(f"   - Pool Size: {conn_info['pool_size']}")
            print(f"   - Checked In: {conn_info['checked_in']}")
            print(f"   - Checked Out: {conn_info['checked_out']}")
        else:
            print(f"❌ Error en base de datos: {health['message']}")
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")

def test_redis_connection():
    """Probar conexión a Redis"""
    print("⚡ Probando conexión a Redis...")
    try:
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            socket_timeout=settings.redis_socket_timeout
        )
        redis_client.ping()
        print("✅ Conexión a Redis exitosa")
        info = redis_client.info()
        print(f"   - Redis Version: {info.get('redis_version', 'unknown')}")
        print(f"   - Connected Clients: {info.get('connected_clients', 'unknown')}")
    except redis.ConnectionError as e:
        print(f"❌ Error conectando a Redis: {e}")
        print("💡 Solución: Ejecuta 'python scripts/check_redis.py' para configurar Redis")
    except Exception as e:
        print(f"❌ Error inesperado con Redis: {e}")

def test_logging():
    """Probar sistema de logging"""
    print("📊 Probando sistema de logging...")
    try:
        logger.log_info("Test info message", {"test": True})
        logger.log_warning("Test warning message", {"test": True})
        logger.log_error("Test error message", {"test": True})
        logger.log_security_event("test_event", "127.0.0.1", "/test")
        logger.log_business_event("test_business", {"operation": "test"})
        print("✅ Sistema de logging funcionando correctamente")
    except Exception as e:
        print(f"❌ Error en sistema de logging: {e}")

async def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas de configuración corregida...")
    print("=" * 60)

    # Probar configuración
    test_configuration()
    print()

    # Probar base de datos
    test_database_connection()
    print()

    # Probar Redis
    test_redis_connection()
    print()

    # Probar logging
    test_logging()
    print()

    print("=" * 60)
    print("🎉 ¡Pruebas completadas!")
    print("💡 Para ejecutar el servidor:")
    print("   python main.py")
    print("💡 Para ver los health checks:")
    print("   curl http://localhost:8000/api/v1/health")
    print("   curl http://localhost:8000/api/v1/health/detailed")

if __name__ == "__main__":
    asyncio.run(main())
