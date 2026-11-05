#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "==> Starting Celery worker for incienso_shop..."
exec celery -A config.celery_app worker \
    --loglevel="${CELERY_LOGLEVEL:-INFO}" \
    --concurrency="${CELERY_WORKER_CONCURRENCY:-2}"
