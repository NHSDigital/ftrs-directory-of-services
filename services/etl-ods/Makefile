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

unit-test:
	poetry run pytest tests/unit

# Override default build to produce producer + consumer artefacts
build: ensure-build-dir build-dependency-layer build-producer-lambda build-consumer-lambda
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes

build-producer-lambda: ensure-build-dir
	mkdir -p $(BUILD_DIR)/producer-tmp
	cp -r producer $(BUILD_DIR)/producer-tmp/
	cp -r common $(BUILD_DIR)/producer-tmp/
	cd $(BUILD_DIR)/producer-tmp && zip -r -q ../$(PRODUCER_LAMBDA_NAME).zip . --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/producer-tmp

build-consumer-lambda: ensure-build-dir
	mkdir -p $(BUILD_DIR)/consumer-tmp
	cp -r consumer $(BUILD_DIR)/consumer-tmp/
	cp -r common $(BUILD_DIR)/consumer-tmp/
	cd $(BUILD_DIR)/consumer-tmp && zip -r -q ../$(CONSUMER_LAMBDA_NAME).zip . --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/consumer-tmp

# ------------------------------------------------------------------------------
# Publish (service-specific S3 layout)
# ------------------------------------------------------------------------------

publish:
	@echo "Publishing $(SERVICE) to $(ARTEFACT_DEVELOPMENT_PATH)..."
	aws s3 cp $(BUILD_DIR)/$(PRODUCER_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(PRODUCER_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(CONSUMER_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(CONSUMER_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	@echo "Published successfully"

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
