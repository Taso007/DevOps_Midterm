# ===========================================================================
# Convenience entrypoints for the DevOps Final project.
# Works wherever `make` is available; Windows users can use scripts/bootstrap.ps1
# or call the same commands directly.
# ===========================================================================
.DEFAULT_GOAL := help
PY ?= python

.PHONY: help setup validate up down restart ps logs test lint audit \
        smoke deploy rollback monitor security clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## One-command bootstrap: validate, build, start, verify
	bash scripts/bootstrap.sh

validate: ## Validate tools, files, ports and compose definition
	$(PY) validate_env.py

up: ## Build and start the full stack
	docker compose up -d --build

down: ## Stop the stack (keep volumes)
	docker compose down

restart: ## Restart the stack
	docker compose restart

ps: ## Show container status
	docker compose ps

logs: ## Tail logs for all services
	docker compose logs -f

test: ## Run unit tests
	npm test

lint: ## Run the linter
	npm run lint

audit: ## Production dependency vulnerability scan
	npm audit --omit=dev --audit-level=high

smoke: ## Deployment verification against the proxy
	$(PY) smoke_test.py --url http://127.0.0.1:8000

deploy: ## Blue-green deploy + post-deploy verification
	$(PY) deploy.py

rollback: ## Roll traffic back to the previous slot
	$(PY) rollback.py

monitor: ## Continuous health monitor
	$(PY) monitor.py

security: ## Full local security scan (audit + Trivy + gitleaks via Docker)
	bash scripts/security_scan.sh

clean: ## Stop stack and remove volumes + local images
	docker compose down -v --rmi local
