# ETL ODS Service Makefile
# This service handles ETL processes for ODS data

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE := etl-ods
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := pipeline-$(POETRY_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Overrides
# ==============================================================================

# ETL-ODS doesn't need coverage report, just runs tests
unit-test:
	poetry run pytest tests/unit

# ==============================================================================
# Help Target
# ==============================================================================

help:
	@echo "ETL ODS Service Targets:"
	@echo ""
	@echo "Build & Test:"
	@echo "  make install              - Install dependencies"
	@echo "  make lint                 - Run linting checks"
	@echo "  make test                 - Run tests"
	@echo "  make build                - Build Lambda package"
	@echo ""
	@echo "Deployment:"
	@echo "  make publish              - Publish to development"
	@echo "  make stage-release        - Stage release"
	@echo "  make promote-rc           - Promote to RC"
	@echo "  make publish-release      - Publish release"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                - Clean build artifacts"
