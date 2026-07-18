#!/usr/bin/env bash
set -euo pipefail

echo ">>> Starting ASGI server (WebSocket + HTTP)..."
exec uvicorn config.asgi:application \
    --host 0.0.0.0 \
    --port 8001 \
    --workers "${UVICORN_WORKERS:-2}" \
    --proxy-headers \
    --forwarded-allow-ips="*"
