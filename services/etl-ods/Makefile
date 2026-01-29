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
EXTRACTOR_LAMBDA_NAME := ftrs-dos-$(SERVICE)-extractor-lambda
TRANSFORMER_LAMBDA_NAME := ftrs-dos-$(SERVICE)-transformer-lambda
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

unit-test: ## Run unit tests
	poetry run pytest tests/unit

# Override default build to produce extractor + transformer + consumer artefacts
build: ensure-build-dir build-dependency-layer build-extractor-lambda build-transformer-lambda build-consumer-lambda
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes

build-extractor-lambda: ensure-build-dir ## Build extractor lamdba artefact
	mkdir -p $(BUILD_DIR)/extractor-tmp
	cp -r extractor $(BUILD_DIR)/extractor-tmp/
	cp -r common $(BUILD_DIR)/extractor-tmp/
	cd $(BUILD_DIR)/extractor-tmp && zip -r -q ../$(EXTRACTOR_LAMBDA_NAME).zip . --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/extractor-tmp

build-transformer-lambda: ensure-build-dir
	mkdir -p $(BUILD_DIR)/transformer-tmp
	cp -r transformer $(BUILD_DIR)/transformer-tmp/
	cp -r common $(BUILD_DIR)/transformer-tmp/
	cd $(BUILD_DIR)/transformer-tmp && zip -r -q ../$(TRANSFORMER_LAMBDA_NAME).zip . --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/transformer-tmp

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
	aws s3 cp $(BUILD_DIR)/$(EXTRACTOR_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(EXTRACTOR_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(TRANSFORMER_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(TRANSFORMER_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(CONSUMER_LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(CONSUMER_LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	@echo "Published successfully"
