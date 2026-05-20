# ======================================================
# PROJECT
# ======================================================

PROJECT_NAME := talatrivia-api
MAIN_SERVICE := talatrivia-api-fastapi

COMPOSE := docker compose -p $(PROJECT_NAME)

# ======================================================
# HELP
# ======================================================

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ======================================================
# DOCKER
# ======================================================

build: ## Build containers
	$(COMPOSE) build

up: ## Start services
	$(COMPOSE) up -d

down: ## Stop services
	$(COMPOSE) down

logs: ## View logs
	$(COMPOSE) logs -f

restart: ## Restart services
	$(COMPOSE) restart

shell: ## Open shell in API container
	$(COMPOSE) exec $(MAIN_SERVICE) bash

# ======================================================
# DATABASE
# ======================================================

migrate: ## Run migrations
	$(COMPOSE) exec $(MAIN_SERVICE) alembic upgrade head

makemigrations: ## Create migration
	$(COMPOSE) exec $(MAIN_SERVICE) alembic revision --autogenerate -m "$(m)"

# ======================================================
# SEEDING
# ======================================================

seed-admin: ## Create initial admin user
	$(COMPOSE) exec $(MAIN_SERVICE) python -m app.scripts.seed_admin

# ======================================================
# QUALITY
# ======================================================

test: ## Run tests
	$(COMPOSE) exec $(MAIN_SERVICE) pytest

lint: ## Run linter
	$(COMPOSE) exec $(MAIN_SERVICE) ruff check .

format: ## Format code
	$(COMPOSE) exec $(MAIN_SERVICE) ruff format .

check: ## Run all quality checks
	$(COMPOSE) exec $(MAIN_SERVICE) sh -c "ruff check . && mypy app"

# ======================================================
# CLEANUP
# ======================================================

clean: ## Remove containers and volumes
	$(COMPOSE) down -v --remove-orphans
