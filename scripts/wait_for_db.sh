#!/bin/sh
# Usage: ./scripts/wait_for_db.sh
set -e
HOST="${DB_HOST:-db}"
PORT="${DB_PORT:-5432}"

echo "Waiting for PostgreSQL at $HOST:$PORT..."
while ! nc -z "$HOST" "$PORT"; do
  sleep 0.5
done
echo "PostgreSQL is up."
