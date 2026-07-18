ifneq ($(filter dev,$(MAKECMDGOALS)),)
  COMPOSE := docker compose -f docker-compose.dev.yml
  EXEC := --workdir /app/backend
else ifneq ($(filter prod,$(MAKECMDGOALS)),)
  COMPOSE := docker compose -f docker-compose.prod.yml
  EXEC :=
else
  COMPOSE := docker compose
  EXEC :=
endif

ARGS = $(filter-out dev prod $@,$(MAKECMDGOALS))

.PHONY: help dev prod up run run-asgi down down-v build pull deploy logs shell \
        dbshell migrate makemigrations makemessages compilemessages \
        collectstatic createsuperuser test lint format dump restore flush-redis \
        bash bash-asgi bash-db bash-nginx

help:
	@echo "make dev up / make dev run   - development"
	@echo "make up                     - local production-like stack"
	@echo "make prod deploy            - pull image and start on a server"
	@echo "make dump media / restore   - PostgreSQL and media migration"

dev:
	@:

prod:
	@:

up:
	$(COMPOSE) up -d --build

run:
	$(COMPOSE) exec $(EXEC) backend python manage.py runserver 0.0.0.0:8000

run-asgi:
	$(COMPOSE) exec $(EXEC) backend uvicorn config.asgi:application --host 0.0.0.0 --port 8001 --reload

down:
	$(COMPOSE) down

down-v:
	$(COMPOSE) down -v

build:
	$(COMPOSE) build

pull:
	$(COMPOSE) pull

deploy:
	$(COMPOSE) pull
	$(COMPOSE) up -d

logs:
	$(COMPOSE) logs -f $(ARGS)

shell:
	$(COMPOSE) exec $(EXEC) backend python manage.py shell

dbshell:
	$(COMPOSE) exec db sh -c 'exec psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

migrate:
	$(COMPOSE) exec $(EXEC) backend python manage.py migrate

makemigrations:
	$(COMPOSE) exec $(EXEC) backend python manage.py makemigrations

makemessages:
	$(COMPOSE) exec $(EXEC) backend python manage.py makemessages -l ru -l en -l uz --ignore .venv

compilemessages:
	$(COMPOSE) exec $(EXEC) backend python manage.py compilemessages

collectstatic:
	$(COMPOSE) exec $(EXEC) backend python manage.py collectstatic --no-input

createsuperuser:
	$(COMPOSE) exec $(EXEC) backend python manage.py createsuperuser

test:
	$(COMPOSE) exec $(EXEC) backend pytest

lint:
	$(COMPOSE) exec $(EXEC) backend ruff check .

format:
	$(COMPOSE) exec $(EXEC) backend ruff format .

dump:
	COMPOSE="$(COMPOSE)" EXEC="$(EXEC)" ./scripts/dump_all.sh $(ARGS)

restore:
	COMPOSE="$(COMPOSE)" EXEC="$(EXEC)" ./scripts/restore_all.sh $(ARGS)

flush-redis:
	$(COMPOSE) exec redis redis-cli FLUSHALL

bash:
	$(COMPOSE) exec -it $(EXEC) backend bash

bash-asgi:
	$(COMPOSE) exec -it $(EXEC) backend-asgi bash

bash-db:
	$(COMPOSE) exec -it db bash

bash-nginx:
	$(COMPOSE) exec -it nginx sh

%:
	@:
