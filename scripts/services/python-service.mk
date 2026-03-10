# Shared Makefile for Python-based services (Lambda functions)
# Include this in service Makefiles with: include ../../scripts/services/python-service.mk

# ==============================================================================
# Common Variables
# ==============================================================================

PYTHON_VERSION ?= 3.12
PLATFORM ?= manylinux2014_x86_64
POETRY_VERSION := $(shell poetry version -s)

LINT_HINT := Hint: Run 'make lint-fix' to fix any fixable linting errors and to format all files in the project

BUILD_DIR := ../../build/services/$(SERVICE)
DEPENDENCY_DIR := $(BUILD_DIR)/dependency-layer

DEPENDENCY_LAYER_NAME := ftrs-dos-$(SERVICE)-python-dependency-layer
LAMBDA_NAME := ftrs-dos-$(SERVICE)-lambda

# Multi-lambda support: Set LAMBDA_SUBDIRS in service Makefile to build multiple lambdas
# Example: LAMBDA_SUBDIRS := extractor transformer consumer health_check
# Each lambda will be built from its subdirectory with common/ included
LAMBDA_SUBDIRS ?=

# Optional; subdirectory containing the lambda directories
# Example: LAMBDA_SOURCES_SUBDIR := src
LAMBDA_SOURCES_SUBDIR ?= .

ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket
BUILD_TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),null)
BUILD_INFO_FILE := $(BUILD_DIR)/build-info.json

COLOR_ORANGE := \033[0;33m
COLOR_GREEN := \033[0;32m
COLOR_RESET := \033[0m

define log_start
	@echo "$(COLOR_ORANGE)$(1)...$(COLOR_RESET)"
endef

define log_success
	@echo "$(COLOR_GREEN)✓ $(1)$(COLOR_RESET)"
endef


# ------------------------------------------------------------------------------
# Development artefact path (branch-aware)
# ------------------------------------------------------------------------------

BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)

ifeq ($(BRANCH),main)
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/latest
RETENTION_TAG := retention=retain
else
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_BUCKET)/development/$(WORKSPACE)
RETENTION_TAG := retention=ephemeral
endif
ARTEFACT_DEVELOPMENT_PREFIX := $(patsubst $(ARTEFACT_BUCKET)/%,%,$(ARTEFACT_DEVELOPMENT_PATH))
RETENTION_VALUE := $(patsubst retention=%,%,$(RETENTION_TAG))

# ==============================================================================
# Common Targets
# ==============================================================================

.PHONY: ensure-build-dir clean install install-dependencies lint lint-fix lint-staged \
		test unit-test coverage generate-build-info build build-dependency-layer \
		publish stage release-candidate release

# ------------------------------------------------------------------------------
# Setup & housekeeping
# ------------------------------------------------------------------------------

ensure-build-dir:
	@mkdir -p $(BUILD_DIR)

clean:
	@rm -rf .pytest_cache .ruff_cache .tmp .build .coverage coverage.xml coverage-*.xml
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DEPENDENCY_DIR)

install: install-dependencies

install-dependencies: ## Install project dependencies
	asdf install
	poetry install --no-interaction

# ------------------------------------------------------------------------------
# Quality
# ------------------------------------------------------------------------------

lint: ## Run linting checks
	poetry run ruff check || { echo "$(LINT_HINT)"; exit 1; }
	poetry run ruff format --check || { echo "$(LINT_HINT)"; exit 1; }

lint-staged: ## Run linting checks only on stages files
	files=$$(git diff --relative --name-only --cached --diff-filter=d -- '*.py'); \
	if [ -z "$$files" ]; then \
		echo "No files staged"; \
	else \
		echo "$$files" | xargs poetry run ruff check || { echo "$(LINT_HINT)"; exit 1; }; \
		echo "$$files" | xargs poetry run ruff format --check || { echo "$(LINT_HINT)"; exit 1; }; \
	fi

lint-fix: ## Run linting checks and fix auto-fixable issues
	poetry run ruff check --fix
	poetry run ruff format

pre-commit: lint-staged

test: unit-test ## Run all tests

unit-test: coverage ## Run unit tests

coverage: ## Run unit tests with coverage
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

build-dependency-layer: clean ### Build the dependency layer
	$(call log_start,Building dependency layer for $(SERVICE))
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
	$(call log_success,Dependency layer built: $(DEPENDENCY_LAYER_NAME).zip)

# Multi-lambda build helper (called for each lambda in LAMBDA_SUBDIRS)
define build_lambda
$(eval ZIP_NAME := ftrs-dos-$(SERVICE)-$(shell echo $(1) | tr '_' '-')-lambda.zip)
@mkdir -p $(BUILD_DIR)/$(1)-tmp
cp -r $(LAMBDA_SOURCES_SUBDIR)/$(1) $(BUILD_DIR)/$(1)-tmp/
[ ! -d $(LAMBDA_SOURCES_SUBDIR)/common ] || cp -r $(LAMBDA_SOURCES_SUBDIR)/common $(BUILD_DIR)/$(1)-tmp/
cd $(BUILD_DIR)/$(1)-tmp && zip -r -q ../$(ZIP_NAME) . --exclude "*__pycache__/*"
@rm -rf $(BUILD_DIR)/$(1)-tmp
$(call log_success,Lambda built: $(ZIP_NAME))
endef

build: ensure-build-dir build-dependency-layer generate-build-info ### Build the service
ifdef LAMBDA_SUBDIRS
	$(call log_start,Building $(SERVICE) with multiple lambdas: $(LAMBDA_SUBDIRS))
	$(foreach lambda,$(LAMBDA_SUBDIRS),$(call build_lambda,$(lambda)))
else
	$(call log_start,Building $(SERVICE))
	poetry build -f wheel -o $(BUILD_DIR)
	mv $(BUILD_DIR)/$(WHEEL_NAME) $(BUILD_DIR)/$(LAMBDA_NAME).zip
	$(call log_success,Lambda built: $(LAMBDA_NAME).zip)
endif
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes
	$(call log_success,Build complete)

# Multi-lambda publish helper (called for each lambda in LAMBDA_SUBDIRS)
define publish_lambda
$(eval ZIP_NAME := ftrs-dos-$(SERVICE)-$(shell echo $(1) | tr '_' '-')-lambda.zip)
aws s3 cp $(BUILD_DIR)/$(ZIP_NAME) s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(ZIP_NAME) --checksum-algorithm SHA256 --region $(AWS_REGION)
aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$(ARTEFACT_DEVELOPMENT_PREFIX)/$(ZIP_NAME)" --tagging "TagSet=[{Key=retention,Value=$(RETENTION_VALUE)}]" --region $(AWS_REGION)
$(call log_success,Lambda published: $(ZIP_NAME))
endef

publish: ## Publish artifacts to S3 development path
	$(call log_start,Publishing $(SERVICE) to $(ARTEFACT_DEVELOPMENT_PATH))
ifdef LAMBDA_SUBDIRS
	$(foreach lambda,$(LAMBDA_SUBDIRS),$(call publish_lambda,$(lambda)))
else
	aws s3 cp $(BUILD_DIR)/$(LAMBDA_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(LAMBDA_NAME).zip --checksum-algorithm SHA256 --region $(AWS_REGION)
	aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$(ARTEFACT_DEVELOPMENT_PREFIX)/$(LAMBDA_NAME).zip" --tagging "TagSet=[{Key=retention,Value=$(RETENTION_VALUE)}]" --region $(AWS_REGION)
	$(call log_success,Lambda published: $(LAMBDA_NAME).zip)
endif
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(DEPENDENCY_LAYER_NAME).zip --checksum-algorithm SHA256 --region $(AWS_REGION)
	aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$(ARTEFACT_DEVELOPMENT_PREFIX)/$(DEPENDENCY_LAYER_NAME).zip" --tagging "TagSet=[{Key=retention,Value=$(RETENTION_VALUE)}]" --region $(AWS_REGION)
	aws s3 cp $(BUILD_INFO_FILE) s3://$(ARTEFACT_DEVELOPMENT_PATH)/build-info.json --checksum-algorithm SHA256 --region $(AWS_REGION)
	aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$(ARTEFACT_DEVELOPMENT_PREFIX)/build-info.json" --tagging "TagSet=[{Key=retention,Value=$(RETENTION_VALUE)}]" --region $(AWS_REGION)
	$(call log_success,Published successfully)

# ==============================================================================
# Help Target
# ==============================================================================

help: ## Show this help message
	@echo ""
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)  $(SERVICE) Service - Available Commands$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)═══════════════════════════════════════════════════════$(COLOR_RESET)"
	@echo ""
	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_ORANGE)%-30s$(COLOR_RESET) %s\n", $$1, $$2}' | \
		sort
	@echo ""
