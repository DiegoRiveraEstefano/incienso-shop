#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Compressing static files..."
python manage.py compress

echo "==> Starting Gunicorn ASGI / Uvicorn server on 0.0.0.0:8000..."
exec gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers "${WEB_CONCURRENCY:-3}" \
    --access-logfile - \
    --error-logfile -
