#!/usr/bin/env bash
# Start TARS v2: ASGI backend (daphne) + engine + dashboard.
# Works on macOS and Linux. Requires the virtualenv at ./.venv to already exist
# and the dashboard's node_modules to be installed.

set -euo pipefail
cd "$(dirname "$0")"

# Load optional .env
if [[ -f .env ]]; then
  set -a; source .env; set +a
fi

# Activate virtualenv
if [[ -d .venv ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python manage.py migrate --noinput

BACKEND_PORT="${TARS_BACKEND_PORT:-8000}"
DASHBOARD_PORT="${TARS_DASHBOARD_PORT:-3000}"

echo "── Starting Django ASGI (daphne) on :${BACKEND_PORT} ──"
daphne -b 0.0.0.0 -p "${BACKEND_PORT}" backend.asgi:application &
BACKEND_PID=$!

echo "── Starting Next.js dashboard on :${DASHBOARD_PORT} ──"
(cd dashboard && npm run dev -- -p "${DASHBOARD_PORT}") &
DASHBOARD_PID=$!

cleanup() {
  kill "${BACKEND_PID}" "${DASHBOARD_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "── Starting TARS engine ──"
python -m engine.main
