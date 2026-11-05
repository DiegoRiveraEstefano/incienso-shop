#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# Ensure required directories exist
mkdir -p /app/data /app/data/cache/diskcache /app/staticfiles /app/incienso_shop/media

if [ -n "${DATABASE_URL:-}" ] && [[ "${DATABASE_URL}" == postgres* ]]; then
  postgres_ready() {
python << END
import sys
import psycopg

try:
    psycopg.connect(
        conninfo="${DATABASE_URL}",
        connect_timeout=3,
    )
except psycopg.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
  }

  echo "==> Waiting for PostgreSQL to be ready..."
  until postgres_ready; do
    >&2 echo "PostgreSQL is unavailable (sleeping)..."
    sleep 1
  done
  echo "==> PostgreSQL is ready!"
fi

exec "$@"
