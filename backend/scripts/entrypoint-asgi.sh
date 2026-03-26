#!/bin/bash

echo ">>> Starting ASGI server (WebSocket + HTTP)..."
uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --workers ${UVICORN_WORKERS:-2}
