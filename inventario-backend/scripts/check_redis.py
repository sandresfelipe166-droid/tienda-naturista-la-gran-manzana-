#!/usr/bin/env python3
"""
Script para verificar y configurar Redis
"""

import os
import socket
import subprocess
import sys
from pathlib import Path


def check_redis_running():
    """Verificar si Redis está ejecutándose"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 6379))
        sock.close()
        return result == 0
    except:
        return False


def check_redis_installed():
    """Verificar si Redis está instalado"""
    try:
        result = subprocess.run(['redis-cli', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def start_redis_service():
    """Intentar iniciar el servicio de Redis"""
    try:
        print("🔄 Intentando iniciar Redis...")
        if os.name == 'nt':  # Windows
            # Para Windows, intentar iniciar Redis desde servicios
            result = subprocess.run(['net', 'start', 'Redis'], capture_output=True, text=True)
            return result.returncode == 0
        else:  # Linux/Mac
            result = subprocess.run(
                ['sudo', 'service', 'redis-server', 'start'], capture_output=True, text=True
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ['redis-server', '--daemonize', 'yes'], capture_output=True, text=True
                )
            return result.returncode == 0
    except Exception as e:
        print(f"❌ Error iniciando Redis: {e}")
        return False


def install_redis():
    """Instalar Redis (solo para Linux/Mac)"""
    print("📦 Instalando Redis...")
    try:
        if os.name == 'nt':
            print(
                "⚠️  En Windows, descarga Redis desde: https://github.com/microsoftarchive/redis/releases"
            )
            print("   Luego ejecuta: redis-server.exe")
            return False

        # Para Linux
        if sys.platform == 'linux':
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', 'redis-server', '-y'], check=True)
            subprocess.run(['sudo', 'service', 'redis-server', 'start'], check=True)
            return True

        # Para macOS
        elif sys.platform == 'darwin':
            subprocess.run(['brew', 'install', 'redis'], check=True)
            subprocess.run(['brew', 'services', 'start', 'redis'], check=True)
            return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando Redis: {e}")
        return False


def main():
    print("🔍 Verificando Redis...")
    print("=" * 50)

    # Verificar si Redis está instalado
    if not check_redis_installed():
        print("❌ Redis no está instalado")
        if input("¿Deseas instalar Redis? (y/n): ").lower() == 'y':
            if install_redis():
                print("✅ Redis instalado exitosamente")
            else:
                print("❌ No se pudo instalar Redis automáticamente")
                print("💡 Instálalo manualmente y ejecuta este script nuevamente")
                return
        else:
            print("💡 Instala Redis manualmente y ejecuta este script nuevamente")
            return

    # Verificar si Redis está ejecutándose
    if not check_redis_running():
        print("❌ Redis no está ejecutándose")
        if start_redis_service():
            print("✅ Redis iniciado exitosamente")
        else:
            print("❌ No se pudo iniciar Redis")
            print("💡 Inicia Redis manualmente:")
            print("   - Linux/Mac: sudo service redis-server start")
            print("   - Windows: Ejecuta redis-server.exe")
            return

    # Verificar conexión
    if check_redis_running():
        print("✅ Redis está funcionando correctamente")
        print("   - Host: localhost")
        print("   - Puerto: 6379")
        print("   - Estado: Conectado")

        # Probar conexión con redis-cli
        try:
            result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
            if result.returncode == 0 and 'PONG' in result.stdout:
                print("✅ Conexión Redis verificada: PONG")
            else:
                print("⚠️  Redis ejecutándose pero sin respuesta")
        except:
            print("⚠️  No se pudo verificar con redis-cli")
    else:
        print("❌ Redis no responde")

    print("=" * 50)
    print("🎉 ¡Redis está listo para usar!")
    print("💡 Para verificar desde tu aplicación:")
    print("   python scripts/test_configuration.py")


if __name__ == "__main__":
    main()
