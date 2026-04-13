#!/bin/sh
set -e

python manage.py migrate_schemas --shared
python manage.py runserver 0.0.0.0:8000
