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

# Override coverage target to test all three API modules
coverage:
	poetry run pytest --cov-report xml:coverage-$(SERVICE).xml \
		organisations/tests/unit \
		healthcare_service/tests/ \
		location/tests/

# Local development targets
start-organisations-api:
	poetry run poe start-organisations-api

start-healthcare-api:
	poetry run poe start-healthcare-api

start-location-api:
	poetry run poe start-location-api

start-all-apis:
	poetry run poe start-all-apis

# ==============================================================================
# Help Target
# ==============================================================================

help:
	@echo "CRUD APIs Service Targets:"
	@echo ""
	@echo "Build & Test:"
	@echo "  make install              - Install dependencies"
	@echo "  make lint                 - Run linting checks"
	@echo "  make lint-fix             - Fix linting issues"
	@echo "  make test                 - Run tests"
	@echo "  make build                - Build Lambda package"
	@echo ""
	@echo "Local Development:"
	@echo "  make start-all-apis       - Start all APIs locally"
	@echo "  make start-organisations-api"
	@echo "  make start-healthcare-api"
	@echo "  make start-location-api"
	@echo ""
	@echo "Deployment:"
	@echo "  make publish              - Publish to development"
	@echo "  make stage-release        - Stage release (RELEASE_TAG required)"
	@echo "  make promote-rc           - Promote to RC"
	@echo "  make publish-release      - Publish release"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                - Clean build artifacts"
