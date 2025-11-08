#!/usr/bin/env python3
"""
Script para configurar Redis en Windows automáticamente
"""

import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path


def download_redis():
    """Descargar Redis para Windows"""
    print("⬇️ Descargando Redis para Windows...")

    redis_url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
    zip_path = "redis-windows.zip"

    try:
        print(f"   Descargando desde: {redis_url}")
        urllib.request.urlretrieve(redis_url, zip_path)
        print("✅ Redis descargado exitosamente")
        return zip_path
    except Exception as e:
        print(f"❌ Error descargando Redis: {e}")
        return None


def extract_redis(zip_path):
    """Extraer Redis del archivo ZIP"""
    print("📦 Extrayendo Redis...")

    extract_path = Path("redis-windows")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
        print(f"✅ Redis extraído en: {extract_path}")
        return extract_path
    except Exception as e:
        print(f"❌ Error extrayendo Redis: {e}")
        return None


def create_redis_config(redis_path):
    """Crear archivo de configuración de Redis"""
    print("⚙️ Creando configuración de Redis...")

    config_content = """# Redis configuration file
port 6379
bind 127.0.0.1
timeout 0
tcp-keepalive 300
daemonize no
supervised no
loglevel notice
logfile "redis.log"
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
replica-priority 100
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
aof-rewrite-incremental-fsync yes
"""

    config_path = redis_path / "redis.conf"
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        print(f"✅ Configuración creada: {config_path}")
        return config_path
    except Exception as e:
        print(f"❌ Error creando configuración: {e}")
        return None


def test_redis_connection(redis_path):
    """Probar conexión a Redis"""
    print("🔍 Probando conexión a Redis...")

    redis_server = redis_path / "redis-server.exe"
    if not redis_server.exists():
        print(f"❌ No se encontró redis-server.exe en {redis_server}")
        return False

    try:
        # Iniciar Redis en background
        config_file = redis_path / "redis.conf"
        process = subprocess.Popen(
            [str(redis_server), str(config_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )

        # Esperar un momento para que inicie
        import time

        time.sleep(2)

        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("✅ Redis iniciado exitosamente")
            print(f"   - PID: {process.pid}")
            print("   - Puerto: 6379")
            # Terminar el proceso de prueba
            process.terminate()
            process.wait()
            return True
        else:
            print("❌ Redis no pudo iniciarse")
            return False

    except Exception as e:
        print(f"❌ Error probando Redis: {e}")
        return False


def create_startup_script(redis_path):
    """Crear script para iniciar Redis fácilmente"""
    print("📝 Creando script de inicio...")

    script_content = f'''@echo off
echo Iniciando Redis...
cd /d "{redis_path}"
redis-server.exe redis.conf
'''

    script_path = redis_path / "start-redis.bat"
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        print(f"✅ Script de inicio creado: {script_path}")
        print("💡 Para iniciar Redis: doble clic en start-redis.bat")
        return script_path
    except Exception as e:
        print(f"❌ Error creando script: {e}")
        return None


def main():
    print("🚀 Configurando Redis para Windows...")
    print("=" * 50)

    # Verificar si ya existe Redis
    redis_path = Path("redis-windows")
    if redis_path.exists():
        print("ℹ️ Redis ya está configurado")
        if test_redis_connection(redis_path):
            print("✅ Redis está funcionando correctamente")
            return
        else:
            print("⚠️ Redis existe pero no funciona. Reconfigurando...")

    # Descargar Redis
    zip_path = download_redis()
    if not zip_path:
        print("❌ No se pudo descargar Redis")
        print("💡 Descárgalo manualmente desde:")
        print("   https://github.com/microsoftarchive/redis/releases")
        return

    # Extraer Redis
    extract_path = extract_redis(zip_path)
    if not extract_path:
        print("❌ No se pudo extraer Redis")
        return

    # Crear configuración
    config_path = create_redis_config(extract_path)
    if not config_path:
        print("❌ No se pudo crear configuración")
        return

    # Probar Redis
    if test_redis_connection(extract_path):
        print("✅ Redis configurado exitosamente")
    else:
        print("❌ Redis no funciona correctamente")
        return

    # Crear script de inicio
    create_startup_script(extract_path)

    # Limpiar archivo ZIP
    try:
        os.remove(zip_path)
        print("🧹 Archivo temporal eliminado")
    except Exception:
        pass

    print("=" * 50)
    print("🎉 ¡Redis configurado exitosamente!")
    print("💡 Para iniciar Redis:")
    print(f"   1. Ve a la carpeta: {extract_path}")
    print("   2. Ejecuta: start-redis.bat")
    print("   3. O manualmente: redis-server.exe redis.conf")
    print("💡 Para verificar:")
    print("   python scripts/test_fixed_configuration.py")


if __name__ == "__main__":
    main()
