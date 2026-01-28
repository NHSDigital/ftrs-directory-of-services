# ETL ODS Service Makefile
# This service builds producer + consumer lambdas and a shared dependency layer

# ==============================================================================
# Service Configuration
# ==============================================================================

ENVIRONMENT ?= mgmt
SERVICE ?= etl-ods
PYTHON_VERSION ?= 3.12
PLATFORM ?= manylinux2014_x86_64

BUILD_DIR := ../../build/services/$(SERVICE)
DEPENDENCY_DIR := $(BUILD_DIR)/dependency-layer

ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket

DEPENDENCY_LAYER_NAME := ftrs-dos-$(SERVICE)-python-dependency-layer
PRODUCER_LAMBDA_NAME := ftrs-dos-$(SERVICE)-processor-lambda
CONSUMER_LAMBDA_NAME := ftrs-dos-$(SERVICE)-consumer-lambda

# ------------------------------------------------------------------------------
# Development artefact path (branch-aware)
# ------------------------------------------------------------------------------

BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

ifeq ($(BRANCH),main)
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/latest
else
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/$(WORKSPACE)
endif

# ==============================================================================
# Common targets (reuse shared quality & setup)
# ==============================================================================

include ../../scripts/services/python-service.mk

# ==============================================================================
# Overrides / Service-specific behaviour
# ==============================================================================

unit-test: ## Run unit testsßßß
	poetry run pytest tests/unit

# Override default build to produce producer + consumer artefacts
build: ensure-build-dir build-dependency-layer build-producer-lambda build-consumer-lambda ## Build all artefacts
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes

build-producer-lambda: ensure-build-dir ## Build producer lambda artefact
	mkdir -p $(BUILD_DIR)/producer-tmp
	cp -r producer $(BUILD_DIR)/producer-tmp/
	cp -r common $(BUILD_DIR)/producer-tmp/
	cd $(BUILD_DIR)/producer-tmp && zip -r -q ../$(PRODUCER_LAMBDA_NAME).zip . --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/producer-tmp

build-consumer-lambda: ensure-build-dir ## Build consumer lambda artefact
	mkdir -p $(BUILD_DIR)/consumer-tmp
	cp -r consumer $(BUILD_DIR)/consumer-tmp/
	cp -r common $(BUILD_DIR)/consumer-tmp/
	cd $(BUILD_DIR)/consumer-tmp && zip -r -q ../$(CONSUMER_LAMBDA_NAME).zip . --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/consumer-tmp

# ------------------------------------------------------------------------------
# Publish (service-specific S3 layout)
# ------------------------------------------------------------------------------

publish: ## Publish build artefacts to development path
	@echo "Publishing $(SERVICE) to $(ARTEFACT_DEVELOPMENT_PATH)..."
	aws s3 cp $(BUILD_DIR)/$(PRODUCER_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(PRODUCER_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(CONSUMER_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(CONSUMER_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	@echo "Published successfully"

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  ETL ODS Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
