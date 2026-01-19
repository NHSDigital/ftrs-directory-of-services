# Shared Makefile for Python-based services (Lambda functions)
# Include this in service Makefiles with: include ../../scripts/services/python-service.mk

# ==============================================================================
# Common Variables
# ==============================================================================

PYTHON_VERSION ?= 3.12
PLATFORM ?= manylinux2014_x86_64
POETRY_VERSION := $(shell poetry version -s)

BUILD_DIR := ../../build/services/$(SERVICE)
DEPENDENCY_DIR := $(BUILD_DIR)/dependency-layer

DEPENDENCY_LAYER_NAME := ftrs-dos-$(SERVICE)-python-dependency-layer
LAMBDA_NAME := ftrs-dos-$(SERVICE)-lambda

ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket
BUILD_TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),null)
BUILD_INFO_FILE := $(BUILD_DIR)/build-info.json

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
# Common Targets
# ==============================================================================

.PHONY: ensure-build-dir clean install install-dependencies lint lint-fix test \
		unit-test coverage generate-build-info build build-dependency-layer \
		publish stage-release promote-rc publish-release

# ------------------------------------------------------------------------------
# Setup & housekeeping
# ------------------------------------------------------------------------------

ensure-build-dir:
	@mkdir -p $(BUILD_DIR)

clean:
	@rm -rf .pytest_cache .ruff_cache .tmp .build .coverage coverage.xml
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DEPENDENCY_DIR)

install: install-dependencies

install-dependencies:
	asdf install
	poetry install --no-interaction

# ------------------------------------------------------------------------------
# Quality
# ------------------------------------------------------------------------------

lint:
	poetry run ruff check
	poetry run ruff format --check

lint-fix:
	poetry run ruff check --fix
	poetry run ruff format

test: unit-test

unit-test: coverage

coverage:
	poetry run pytest --cov-report xml:coverage-$(SERVICE).xml tests/unit

# ------------------------------------------------------------------------------
# Build
# ------------------------------------------------------------------------------

generate-build-info: ensure-build-dir
	@echo '{' > $(BUILD_INFO_FILE)
	@echo '  "git_commit": "$(COMMIT_HASH)",' >> $(BUILD_INFO_FILE)
	@echo '  "build_timestamp": "$(BUILD_TIMESTAMP)",' >> $(BUILD_INFO_FILE)
	@echo '  "release_version": "$(RELEASE_VERSION)"' >> $(BUILD_INFO_FILE)
	@echo '}' >> $(BUILD_INFO_FILE)

build-dependency-layer: clean
	@echo "Building dependency layer for $(SERVICE)..."
	@mkdir -p $(DEPENDENCY_DIR)/python
	poetry export --without dev --without-hashes > $(DEPENDENCY_DIR)/requirements.txt
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

build: ensure-build-dir build-dependency-layer generate-build-info
	@echo "Building $(SERVICE)..."
	poetry build -f wheel -o $(BUILD_DIR)
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	mv $(BUILD_DIR)/$(WHEEL_NAME) $(BUILD_DIR)/$(LAMBDA_NAME).zip
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes
	@echo "Build complete: $(LAMBDA_NAME).zip"

publish:
	@echo "Publishing $(SERVICE) to $(ARTEFACT_DEVELOPMENT_PATH)..."
	aws s3 cp $(BUILD_DIR)/$(LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_INFO_FILE) s3://$(ARTEFACT_DEVELOPMENT_PATH)/build-info.json --region $(AWS_REGION)
	@echo "Published successfully"

pre-commit: lint

# ==============================================================================
# Help Target
# ==============================================================================

help:
	@echo "Common Python Service Targets:"
	@echo "  install              - Install dependencies"
	@echo "  lint                 - Run linting checks"
	@echo "  lint-fix             - Fix linting issues"
	@echo "  test                 - Run tests"
	@echo "  build                - Build Lambda package and dependency layer"
	@echo "  publish              - Publish to development artefact bucket"
	@echo "  stage-release        - Stage release candidate"
	@echo "  promote-rc           - Promote to release candidate"
	@echo "  publish-release      - Publish final release"
	@echo "  clean                - Clean build artifacts"
