# Redis en Windows - Cómo obtener y configurar Redis

Este proyecto requiere Redis para funcionalidad completa (cache, rate limiting distribuido).

## Opción 1: Docker (Recomendado)
```powershell
# Desde inventario-backend/ o inventario-frontend/
docker-compose up -d redis
```

## Opción 2: Redis nativo en Windows
1. Descarga Redis for Windows desde:
   - https://github.com/microsoftarchive/redis/releases (versión 3.x)
   - O https://github.com/tporadowski/redis/releases (fork actualizado, recomendado)

2. Extrae el archivo ZIP a una carpeta local (por ejemplo `C:\redis-windows\`)

3. Inicia Redis desde PowerShell:
```powershell
cd C:\redis-windows
.\redis-server.exe
```

4. Verifica que funciona:
```powershell
.\redis-cli.exe ping
# Deberías ver: PONG
```

## Opción 3: WSL2 + Redis (para desarrolladores avanzados)
Si usas WSL2:
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
redis-cli ping  # Debes ver PONG
```

## Configurar en tu app
Añade `REDIS_URL` a tu archivo `.env`:
```
REDIS_URL=redis://localhost:6379
```

## Tests que requieren Redis
- `tests/test_redis_rate_limiter.py` — limiter distribuido con Redis
- Scripts con `cache` o `rate limiting` habilitado

Si no quieres ejecutar Redis localmente, los tests unitarios usan en-memory rate limiter por defecto y no fallarán.

---

**Nota**: Los ejecutables de Redis (`redis-windows/*.exe`) fueron eliminados del repo para mantenerlo limpio. Usa Docker Compose para desarrollo o descarga los binarios manualmente siguiendo los pasos anteriores.
