ENVIRONMENT ?= mgmt
PACKAGE ?= python
BUILD_DIR := ../../../build/packages/$(PACKAGE)
ARTEFACT_BUCKET := ${REPO_NAME}-$(ENVIRONMENT)-artefacts-bucket
PACKAGE_VERSION := $(shell poetry version -s)
WHEEL_NAME := ftrs_python_packages-$(PACKAGE_VERSION)-py3-none-any.whl
PYTHON_VERSION ?= 3.12
PLATFORM ?= manylinux2014_x86_64
PACKAGES_LAYER_NAME := ftrs-dos-python-packages-layer
BUILD_TIMESTAMP := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
RELEASE_VERSION := $(if $(RELEASE_TAG),$(RELEASE_TAG),null)
BUILD_INFO_FILE := $(BUILD_DIR)/build-info.json
RETAIN_VERSIONS ?= 5

# Determine the correct artefact path based on branch
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

ARTEFACT_STAGING_PATH := $(ARTEFACT_BUCKET)/staging/$(RELEASE_TAG)

ensure-build-dir:
	@mkdir -p $(BUILD_DIR)

clean:
	@rm -rf .poetry .pytest_cache .ruff_cache .tmp .venv .build .coverage coverage.xml
	@rm -rf $(BUILD_DIR)

install:
	asdf install
	poetry install

generate-build-info: ensure-build-dir
	@echo '{' > $(BUILD_INFO_FILE)
	@echo '  "git_commit": "$(COMMIT_HASH)",' >> $(BUILD_INFO_FILE)
	@echo '  "build_timestamp": "$(BUILD_TIMESTAMP)",' >> $(BUILD_INFO_FILE)
	@echo '  "release_version": "$(RELEASE_VERSION)"' >> $(BUILD_INFO_FILE)
	@echo '}' >> $(BUILD_INFO_FILE)

build: ensure-build-dir build-package build-layer generate-build-info

build-package:
	@echo "Building Python packages wheel..."
	poetry build -o $(BUILD_DIR) -f wheel

build-layer:
	@echo "Building Lambda layer from wheel..."
	mkdir -p $(BUILD_DIR)/layer/python
	pip install \
		--target $(BUILD_DIR)/layer/python \
		--platform $(PLATFORM) \
		--implementation cp \
		--python-version $(PYTHON_VERSION) \
		--only-binary=:all: \
		--upgrade \
		$(BUILD_DIR)/$(WHEEL_NAME)
	cd $(BUILD_DIR)/layer && zip -r -q ../$(PACKAGES_LAYER_NAME).zip * --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/layer/
	@echo "Layer built: $(PACKAGES_LAYER_NAME).zip"

lint:
	poetry run ruff check
	poetry run ruff format --check

lint-fix:
	poetry run ruff check --fix
	poetry run ruff format

unit-test:
	poetry run pytest --cov-report xml:coverage-$(PACKAGE).xml

coverage: unit-test

publish:
	@echo "Publishing Python packages layer to $(ARTEFACT_DEVELOPMENT_PATH)..."
	aws s3 cp $(BUILD_DIR)/$(PACKAGES_LAYER_NAME).zip s3://$(ARTEFACT_DEVELOPMENT_PATH)/$(PACKAGES_LAYER_NAME).zip --checksum-algorithm SHA256 --region $(AWS_REGION)
	aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$(ARTEFACT_DEVELOPMENT_PREFIX)/$(PACKAGES_LAYER_NAME).zip" --tagging "TagSet=[{Key=retention,Value=$(RETENTION_VALUE)}]" --region $(AWS_REGION)
	aws s3 cp $(BUILD_INFO_FILE) s3://$(ARTEFACT_DEVELOPMENT_PATH)/build-info.json --region $(AWS_REGION)
	aws s3api put-object-tagging --bucket $(ARTEFACT_BUCKET) --key "$(ARTEFACT_DEVELOPMENT_PREFIX)/build-info.json" --tagging "TagSet=[{Key=retention,Value=$(RETENTION_VALUE)}]" --region $(AWS_REGION)
	@echo "Published successfully"

help:
	@echo "Python Packages Makefile Targets:"
	@echo ""
	@echo "Build & Test:"
	@echo "  make install              - Install dependencies"
	@echo "  make lint                 - Run linting checks"
	@echo "  make lint-fix             - Fix linting issues"
	@echo "  make unit-test            - Run tests"
	@echo "  make build                - Build wheel and Lambda layer"
	@echo ""
	@echo "Deployment:"
	@echo "  make publish              - Publish to development"
	@echo "  make stage-release        - Stage release (RELEASE_TAG required)"
	@echo "  make promote-rc           - Promote to RC"
	@echo "  make publish-release      - Publish release"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                - Clean build artifacts"
