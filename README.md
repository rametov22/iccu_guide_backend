# ICCU iPad Tour

Django/DRF/Channels backend on the production-oriented structure from
[`igorkhaylov/django-template`](https://github.com/igorkhaylov/django-template).
The existing custom user, models, migrations, REST API, WebSocket consumers,
Firebase integration and local media storage are preserved.

## Services

- `backend`: Gunicorn/WSGI on port 8000.
- `backend-asgi`: Uvicorn/Channels on port 8001.
- `db`: PostgreSQL 17.4.
- `redis`: cache and Channels layer.
- `nginx`: REST, WebSocket, static and media entrypoint.

Media files remain in the `django-media` Docker volume. Firebase credentials are
read from `./secrets/firebase-service-account.json`; the directory is excluded
from Git and Docker build context.

## Development

```bash
cp .env.example .env
# Fill every CHANGE_ME.
make dev up
make dev run
```

The REST/admin service is available at `http://localhost:${APP_PORT}`.
WebSocket requests under `/ws/` are proxied to the ASGI container.

## Health checks

`/healthcheck/` is the shallow Docker healthcheck. `/deep-health/` is the
protected monitoring endpoint and checks `backend`, `backend-asgi`, `db` and
`redis` concurrently. Configure a separate random key in `.env`:

```dotenv
DEEP_HEALTH_API_KEY=<output of openssl rand -hex 32>
```

Call it through HTTPS in production:

```bash
KEY='<same value as DEEP_HEALTH_API_KEY in .env>'
curl -sS -H "X-API-Key: ${KEY}" https://api.guide.iccu.uz/deep-health/
unset KEY
```

Missing or invalid credentials return HTTP 401. An authorized request always
returns HTTP 200; inspect the JSON `status` and individual `services` values.

## Commands

```bash
make dev test
make dev lint
make dev migrate
make dev createsuperuser

make up
make prod deploy
make prod logs backend
make prod dump media
make prod restore dumps/<timestamp>
```

Never run `docker compose down -v` on a server containing production data.

## Image deployment

GitHub Actions publishes:

```text
ghcr.io/rametov22/iccu-guide-backend:sha-<full-commit-sha>
```

Set that value as `BACKEND_IMAGE` on the server, authenticate with GHCR, then:

```bash
make prod deploy
```

See [docs/server-migration.md](docs/server-migration.md) for database, media and
Firebase migration.
