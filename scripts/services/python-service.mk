# Shared Makefile for Python-based services (Lambda functions)
# Include this in service Makefiles with: include ../../scripts/services/python-service.mk

# ==============================================================================
# Common Variables
# ==============================================================================

PYTHON_VERSION ?= 3.12
PLATFORM ?= manylinux2014_x86_64
BUILD_DIR := ../../build/services/$(SERVICE)
DEPENDENCY_DIR := $(BUILD_DIR)/dependency-layer
ARTEFACT_BUCKET := $(REPO_NAME)-$(ENVIRONMENT)-artefacts-bucket
POETRY_VERSION := $(shell poetry version -s)
DEPENDENCY_LAYER_NAME := ftrs-dos-$(SERVICE)-python-dependency-layer
LAMBDA_NAME := ftrs-dos-$(SERVICE)-lambda
BUILD_TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),$(if $(PRERELEASE_TAG),$(PRERELEASE_TAG),null))
BUILD_INFO_FILE := $(BUILD_DIR)/build-info.json

# Determine the correct artefact path based on branch
BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
ifeq ($(BRANCH),main)
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_PATH)/development/latest
else
ARTEFACT_DEVELOPMENT_PATH := $(ARTEFACT_PATH)/development/$(WORKSPACE)
endif

ARTEFACT_STAGING_PATH := $(ARTEFACT_PATH)/staging/$(PRERELEASE_TAG)
ARTEFACT_RELEASE_CANDIDATE_PATH := $(ARTEFACT_PATH)/release-candidates/$(RELEASE_TAG)

# ==============================================================================
# Common Targets
# ==============================================================================

.PHONY: ensure-build-dir clean install install-dependencies lint lint-fix test \
		unit-test coverage generate-build-info build build-dependency-layer \
		publish stage-release promote-rc publish-release

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

lint:
	poetry run ruff check
	poetry run ruff format --check

lint-fix:
	poetry run ruff check --fix
	poetry run ruff format

test: unit-test

unit-test: coverage

# Override this in service Makefile if different test paths needed
coverage:
	poetry run pytest --cov-report xml:coverage-$(SERVICE).xml tests/unit

generate-build-info: ensure-build-dir
	@echo '{' > $(BUILD_INFO_FILE)
	@echo '  "git_commit": "$(COMMIT_HASH)",' >> $(BUILD_INFO_FILE)
	@echo '  "build_timestamp": "$(BUILD_TIMESTAMP)",' >> $(BUILD_INFO_FILE)
	@echo '  "release_version": $(RELEASE_VERSION)' >> $(BUILD_INFO_FILE)
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

# Override WHEEL_NAME in service Makefile if package name differs from service name
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

set-prerelease-version:
	@if [ -z "$(PRERELEASE_TAG)" ]; then \
		echo "Finding latest prerelease version for $(SERVICE)..."; \
		$(eval PRERELEASE_TAG := $(shell aws s3 ls s3://$(ARTEFACT_BUCKET)/staging/ --region $(AWS_REGION) | awk '{print $$2}' | sed 's/\/$$//' | sort -V | tail -1)); \
		if [ -z "$(PRERELEASE_TAG)" ]; then echo "Error: No staging versions found"; exit 1; fi; \
	else \
		echo "Using provided prerelease version: $(PRERELEASE_TAG)"; \
	fi

stage-release: set-prerelease-version
	@echo "Staging release $(PRERELEASE_TAG) for $(SERVICE)..."
	aws s3 cp s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(LAMBDA_NAME).zip s3://$(ARTEFACT_STAGING_PATH)/$(LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_STAGING_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	aws s3 cp s3://$(ARTEFACT_DEVELOPMENT_PATH)/build-info.json s3://$(ARTEFACT_STAGING_PATH)/build-info.json --region $(AWS_REGION)
	@echo "Release staged successfully"

promote-rc: set-prerelease-version
	@echo "Promoting from staging/$(PRERELEASE_TAG) to release candidate for $(SERVICE)..."
	aws s3 cp s3://$(ARTEFACT_STAGING_PATH)/$(LAMBDA_NAME).zip s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/$(LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp s3://$(ARTEFACT_STAGING_PATH)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	aws s3 cp s3://$(ARTEFACT_STAGING_PATH)/build-info.json s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/build-info.json --region $(AWS_REGION)
	@echo "Promoted from staging/$(STAGING_VERSION) to release candidate"

promote-release:
	$(eval RELEASE_VERSION_CLEAN := $(shell echo "$(RELEASE_TAG)" | sed 's/-rc\.[0-9]*$$//'))
	$(eval ARTEFACT_RELEASE_PATH := $(ARTEFACT_PATH)/releases/$(RELEASE_VERSION_CLEAN))
	@echo "Promoting from release-candidates/$(RELEASE_TAG) to releases/$(RELEASE_VERSION_CLEAN)..."
	aws s3 cp s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/$(LAMBDA_NAME).zip s3://$(ARTEFACT_RELEASE_PATH)/$(LAMBDA_NAME).zip --region $(AWS_REGION)
	aws s3 cp s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/$(DEPENDENCY_LAYER_NAME).zip s3://$(ARTEFACT_RELEASE_PATH)/$(DEPENDENCY_LAYER_NAME).zip --region $(AWS_REGION)
	aws s3 cp s3://$(ARTEFACT_RELEASE_CANDIDATE_PATH)/build-info.json s3://$(ARTEFACT_RELEASE_PATH)/build-info.json --region $(AWS_REGION)
	@echo "Release published successfully to releases/$(RELEASE_VERSION_CLEAN)"

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
