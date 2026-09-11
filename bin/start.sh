#!/bin/sh
set -e

python manage.py collectstatic --noinput
exec gunicorn settings.wsgi:application \
  --bind "0.0.0.0:${PORT:-4000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 60
