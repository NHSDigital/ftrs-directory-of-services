# CRUD APIs Service Makefile
# This service provides REST APIs for healthcare services, locations, and organisations

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= crud-apis
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := crud_apis-$(POETRY_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Targets
# ==============================================================================

coverage: ## Run tests with coverage for all API modules
	poetry run pytest --cov-report xml:coverage-$(SERVICE).xml \
		organisations/tests/unit \
		healthcare_service/tests/ \
		location/tests/

# Local development targets
start-organisations-api: ## Start organisations API
	poetry run poe start-organisations-api

start-healthcare-api: ## Start healthcare service API
	poetry run poe start-healthcare-api

start-location-api: ## Start location API
	poetry run poe start-location-api

start-all-apis: ## Start all APIs
	poetry run poe start-all-apis

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  CRUD APIs Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
