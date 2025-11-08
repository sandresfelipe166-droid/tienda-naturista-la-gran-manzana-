#!/usr/bin/env python3
"""
Script simplificado para iniciar Redis en Windows
"""

import os
import subprocess
import time
from pathlib import Path


def start_redis_simple():
    """Iniciar Redis de forma simple"""
    print("🚀 Iniciando Redis...")

    # Buscar redis-server.exe
    redis_paths = [
        "redis-windows/redis-server.exe",
        "redis-windows/redis-server",
        "redis-server.exe",
    ]

    redis_server = None
    for path in redis_paths:
        if Path(path).exists():
            redis_server = path
            break

    if not redis_server:
        print("❌ No se encontró redis-server.exe")
        print("💡 Descarga Redis desde:")
        print("   https://github.com/microsoftarchive/redis/releases")
        return False

    print(f"✅ Encontrado: {redis_server}")

    try:
        # Iniciar Redis sin configuración compleja
        print("🔄 Iniciando Redis...")
        process = subprocess.Popen(
            [redis_server],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        # Esperar un momento
        time.sleep(3)

        # Verificar si sigue ejecutándose
        if process.poll() is None:
            print("✅ Redis iniciado exitosamente!")
            print(f"   - PID: {process.pid}")
            print("   - Puerto: 6379 (por defecto)")
            print("   - Comando: redis-server.exe")
            print("💡 Redis se está ejecutando en segundo plano")
            print("💡 Presiona Ctrl+C para detenerlo")
            return True
        else:
            print("❌ Redis se detuvo inmediatamente")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"   Error: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"❌ Error iniciando Redis: {e}")
        return False


def main():
    print("🔧 Iniciador Simple de Redis para Windows")
    print("=" * 50)

    if start_redis_simple():
        print("=" * 50)
        print("🎉 ¡Redis está funcionando!")
        print("💡 Ahora puedes probar tu aplicación:")
        print("   python scripts/test_fixed_configuration.py")
        print("💡 Para detener Redis manualmente:")
        print("   - Abre el Administrador de Tareas")
        print("   - Busca 'redis-server.exe'")
        print("   - Termínalo")
    else:
        print("=" * 50)
        print("❌ No se pudo iniciar Redis")
        print("💡 Soluciones alternativas:")
        print("   1. Descarga Redis desde GitHub")
        print("   2. Instálalo con Docker: docker run -p 6379:6379 redis")
        print("   3. Usa un servicio en la nube como Redis Labs")


if __name__ == "__main__":
    main()
