COMPOSE=docker compose -f config/compose/docker-compose.dev.yml
EXEC=$(COMPOSE) exec web

.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser test lint

help:
	@echo ""
	@echo "  make build            Build Docker images"
	@echo "  make up               Start all services (detached)"
	@echo "  make down             Stop all services"
	@echo "  make restart          Restart web container only"
	@echo "  make logs             Tail all service logs"
	@echo "  make shell            Django shell_plus inside web container"
	@echo "  make bash             Bash shell inside web container"
	@echo "  make migrate          Run migrate_schemas (shared + all tenants)"
	@echo "  make makemigrations   Make migrations for all apps"
	@echo "  make createsuperuser  Create a Django superuser"
	@echo "  make test             Run pytest"
	@echo "  make lint             Run ruff linter"
	@echo ""

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart web

logs:
	$(COMPOSE) logs -f

shell:
	$(EXEC) python manage.py shell

bash:
	$(EXEC) bash

migrate:
	$(EXEC) python manage.py migrate_schemas --shared
	$(EXEC) python manage.py migrate_schemas

makemigrations:
	$(EXEC) python manage.py makemigrations

createsuperuser:
	$(EXEC) python manage.py createsuperuser

test:
	$(EXEC) pytest

lint:
	$(EXEC) ruff check .

# Provision a demo hospital tenant for local testing
demo-tenant:
	$(EXEC) python manage.py shell -c "\
from apps.tenants.services import provision_hospital; \
from apps.tenants.models import Plan; \
Plan.objects.get_or_create(tier='basic', defaults={'name':'Basic','price_monthly':99,'max_users':10,'max_patients':500}); \
h = provision_hospital('Demo Hospital', 'demo@hospital.test', 'demo', base_domain='localhost'); \
print(f'Created: {h.name} → schema: {h.schema_name}')"
