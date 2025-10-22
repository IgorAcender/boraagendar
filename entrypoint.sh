#!/bin/sh
set -e

if [ "${SKIP_COLLECTSTATIC:-0}" = "1" ]; then
  echo "[entrypoint] Skipping collectstatic (SKIP_COLLECTSTATIC=1)."
else
  echo "[entrypoint] Running collectstatic..."
  python manage.py collectstatic --noinput
  echo "[entrypoint] collectstatic complete."
fi

exec "$@"
