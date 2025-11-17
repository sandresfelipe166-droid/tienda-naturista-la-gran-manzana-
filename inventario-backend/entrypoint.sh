#!/bin/sh
set -e

echo "Waiting for database and running migrations..."
RETRIES=10
SLEEP=3
i=0
while [ "$i" -lt "$RETRIES" ]; do
  # Use 'heads' to apply all heads when multiple branches exist
  if alembic -c alembic.ini upgrade heads; then
    echo "Migrations applied successfully"
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
