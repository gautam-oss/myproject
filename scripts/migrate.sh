#!/bin/sh
# Runs shared-schema migrations first, then all tenant schemas.
set -e
echo "Running shared (public) schema migrations..."
python manage.py migrate_schemas --shared

echo "Running tenant schema migrations..."
python manage.py migrate_schemas

echo "All migrations complete."
