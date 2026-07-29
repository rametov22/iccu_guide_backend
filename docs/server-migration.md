# Перенос ICCU iPad Tour

## 1. Старый сервер

Остановить входящий трафик, оставив backend и PostgreSQL запущенными:

```bash
docker compose -f docker-compose.prod.yml stop nginx
make prod dump media
```

Команда создаст `dumps/<timestamp>/database.sql.gz` и `media.tar.gz`.
Скопировать каталог на новый сервер через `rsync`.

## 2. Новый сервер

Клонировать тот же commit, создать `.env`, каталог `secrets` и положить Firebase
service-account JSON:

```bash
mkdir -p secrets
chmod 700 secrets
```

В `.env` указать точный SHA image:

```dotenv
ENVIRONMENT=prod
BACKEND_IMAGE=ghcr.io/rametov22/iccu-guide-backend:sha-<full-commit-sha>
FIREBASE_CREDENTIALS_PATH=/app/secrets/firebase-service-account.json
DEEP_HEALTH_API_KEY=<output of openssl rand -hex 32>
```

Авторизоваться и запустить пустой стек:

```bash
docker login ghcr.io
make prod deploy
```

Остановить внешний доступ и ASGI, восстановить архив:

```bash
docker compose -f docker-compose.prod.yml stop nginx backend-asgi
make prod restore dumps/<timestamp>
docker compose -f docker-compose.prod.yml up -d
```

## 3. Проверка

```bash
docker compose -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:${APP_PORT}/healthcheck/
KEY='<same value as DEEP_HEALTH_API_KEY in .env>'
curl -sS -H "X-API-Key: ${KEY}" https://api.guide.iccu.uz/deep-health/
unset KEY
docker compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
```

Проверить admin, REST API, media и WebSocket `/ws/lobby/`.

Старый сервер и его volumes не удалять до окончания периода наблюдения.
