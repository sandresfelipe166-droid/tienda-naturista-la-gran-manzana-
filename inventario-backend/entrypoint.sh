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

echo "Alembic current before upgrade:"
alembic -c alembic.ini current || true
while [ "$i" -lt "$RETRIES" ]; do
  # Use 'heads' to apply all heads when multiple branches exist
  if alembic -c alembic.ini upgrade heads; then
    echo "Migrations applied successfully"
    # Seed default roles to ensure application has expected roles
    echo "Seeding default roles (idempotent)..."
    if python -m app.scripts.seed_roles; then
      echo "Seed script completed"
    else
      echo "Seed script failed (continuing startup)" >&2
    fi
    break
  else
    echo "Migration attempt $((i+1)) failed, retrying in $SLEEP seconds..."
    i=$((i+1))
    sleep $SLEEP
  fi
done

if [ "$i" -ge "$RETRIES" ]; then
  echo "Migrations failed after $RETRIES attempts" >&2
  exit 1
fi

echo "Starting application"
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2 --log-level info

# After startup we'll also print current alembic revision (best-effort)
# Note: this will only run if the container stays alive and python/alembic are available
echo "Alembic current after startup:"
alembic -c alembic.ini current || true
