# Variables de entorno requeridas

Este proyecto usa variables para backend (FastAPI) y frontend (Vite/React). A continuación tienes el mínimo necesario para producir y desarrollo, con opcionales marcados.

## Backend (FastAPI)

Recomendadas para producción (Render – servicio Docker):

- ENVIRONMENT=production
- DEBUG=false
- HOST=0.0.0.0
- PORT (Render lo inyecta; no lo cambies manualmente)
- DATABASE_URL=postgresql+psycopg2://<USER>:<PASS>@<HOST>:<PORT>/<DB>?sslmode=require
- SECRET_KEY=una cadena aleatoria segura (>= 64 caracteres)
- JWT_ALG=HS256
- ACCESS_TOKEN_EXPIRE_MINUTES=30
- REFRESH_TOKEN_EXPIRE_DAYS=7

Opcionales útiles:

- DB_POOL_SIZE=20
- DB_MAX_OVERFLOW=30
- DB_POOL_TIMEOUT=30
- DB_POOL_RECYCLE=3600
- LOG_LEVEL=INFO
- LOG_FILE=logs/inventario.log
- CORS_ORIGINS=lista separada por comas si quieres forzar orígenes (por defecto en producción permite *.onrender.com)
- TRUSTED_HOSTS=lista separada por comas si quieres forzar hosts (por defecto en producción permite *.onrender.com)
- PROMETHEUS_ENABLED=false (o true si expones /metrics)
- METRICS_ENABLED=false

Redis (solo si lo usas):

- REDIS_HOST=<host>
- REDIS_PORT=6379
- REDIS_DB=0
- REDIS_PASSWORD=<password>
- REDIS_HEALTH_CHECK_ENABLED=false

Email/SMTP (solo si habilitas notificaciones):

- SMTP_HOST
- SMTP_PORT=587
- SMTP_USER
- SMTP_PASSWORD
- SMTP_USE_TLS=true

Reset de contraseña:

- PASSWORD_RESET_EXPIRE_MINUTES=15

Health/seguridad:

- HEALTH_CHECK_ENABLED=true
- DB_HEALTH_CHECK_ENABLED=true
- SSL_ENABLED=false (Render termina TLS en el LB)

Notas importantes:

- En producción, el backend exige SECRET_KEY de al menos 32 caracteres. Usa 64+.
- Si tu DATABASE_URL viene de Render Postgres, usa el host/URL interno y añade `sslmode=require`.
- El endpoint de salud está en `/health`.

Ejemplo .env (local):

```
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql+psycopg2://admin:admin123@localhost:5432/inventario
SECRET_KEY=dev-secret-key-change-in-production-123456789
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=INFO
LOG_FILE=logs/inventario.log
```

Ejemplo .env (producción Render – Docker):

```
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
# PORT lo inyecta Render
DATABASE_URL=postgresql+psycopg2://<USER>:<PASS>@<HOST>:5432/<DB>?sslmode=require
SECRET_KEY=<cadena-aleatoria-64+>
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
PROMETHEUS_ENABLED=false
HEALTH_CHECK_ENABLED=true
DB_HEALTH_CHECK_ENABLED=true
```

## Frontend (Vite/React)

Requeridas:

- VITE_API_URL=https://<tu-backend>.onrender.com
- VITE_API_V1=/api/v1
- VITE_WS_URL=wss://<tu-backend>.onrender.com
- VITE_ENV=production (o development en local)

Opcionales:

- VITE_ENABLE_NOTIFICATIONS=true
- VITE_ENABLE_ANALYTICS=false

Ejemplos:

Local
```
VITE_API_URL=http://localhost:8000
VITE_API_V1=/api/v1
VITE_WS_URL=ws://localhost:8000
VITE_ENV=development
```

Producción (Render Static Site)
```
VITE_API_URL=https://<tu-backend>.onrender.com
VITE_API_V1=/api/v1
VITE_WS_URL=wss://<tu-backend>.onrender.com
VITE_ENV=production
```