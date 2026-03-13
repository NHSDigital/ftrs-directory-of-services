# CRUD APIs Service Makefile
# This service provides REST APIs for healthcare services, locations, and organisations

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= crud-apis
PROJECT_VERSION := $(shell grep '^version' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
WHEEL_NAME := crud_apis-$(PROJECT_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Targets
# ==============================================================================

coverage: ## Run tests with coverage for all API modules
	uv run pytest --cov-report xml:coverage-$(SERVICE).xml \
		organisations/tests/unit \
		healthcare_service/tests/ \
		location/tests/

# Local development targets
start-organisations-api: ## Start organisations API
	uv run start-organisations-api

start-healthcare-api: ## Start healthcare service API
	uv run start-healthcare-api

start-location-api: ## Start location API
	uv run start-location-api

start-all-apis: ## Start all APIs
	uv run start-all-apis
