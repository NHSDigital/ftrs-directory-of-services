# Slack Notifier Service Makefile
# This service provides Slack notification functionality for CloudWatch alarms

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= slack-notifier
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := slack_notifier-$(POETRY_VERSION)-py3-none-any.whl

# ==============================================================================
# Include Shared Python Service Targets
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Service-Specific Overrides
# ==============================================================================

# Override dependency layer export to exclude additional groups
build-dependency-layer: ## Build Python dependency layer artefact
	@echo "Building dependency layer for $(SERVICE)..."
	@mkdir -p $(DEPENDENCY_DIR)/python
	poetry export --without dev --without test --without-hashes > $(DEPENDENCY_DIR)/requirements.txt
	pip install \
		--platform $(PLATFORM) \
		--target $(DEPENDENCY_DIR)/python \
		--implementation cp \
		--python-version $(PYTHON_VERSION) \
		--no-deps \
		--upgrade \
		-r $(DEPENDENCY_DIR)/requirements.txt
	cd $(DEPENDENCY_DIR) && zip -r -q ../$(DEPENDENCY_LAYER_NAME).zip * --exclude "*__pycache__/*"
	@echo "Dependency layer built: $(DEPENDENCY_LAYER_NAME).zip"