#!/bin/sh
set -e

echo "Waiting for database and running migrations..."
RETRIES=10
SLEEP=3
i=0
# Print masked DATABASE_URL info for debugging (do not log full credentials)
if [ -n "$DATABASE_URL" ]; then
  # Extract host and dbname roughly (handles format user:pass@host/db)
  MASKED_DBINFO=$(echo "$DATABASE_URL" | sed -E 's#(.*@)?([^:/]+)(:[0-9]+)?/([^?]+).*#host=\2 db=\4#')
  echo "DATABASE target: $MASKED_DBINFO"
else
  echo "DATABASE_URL not set"
fi

# Migraciones deshabilitadas temporalmente - arrancar sin migraciones
echo "Skipping migrations - starting application directly"
# Las tablas deben crearse manualmente o las migraciones deben arreglarse
# echo "Alembic current before upgrade:"
# alembic -c alembic.ini current || true

echo "Starting application"
# Use PORT from environment or default to 8000
APP_PORT="${PORT:-8000}"
echo "Starting on port: $APP_PORT"
exec uvicorn main:app --host 0.0.0.0 --port "$APP_PORT" --workers 2 --log-level info

# After startup we'll also print current alembic revision (best-effort)
# Note: this will only run if the container stays alive and python/alembic are available
echo "Alembic current after startup:"
alembic -c alembic.ini current || true
