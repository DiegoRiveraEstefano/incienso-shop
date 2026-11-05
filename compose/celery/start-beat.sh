#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "==> Starting Celery beat scheduler for incienso_shop..."
rm -f '/app/celerybeat.pid'
exec celery -A config.celery_app beat \
    --loglevel="${CELERY_LOGLEVEL:-INFO}" \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
