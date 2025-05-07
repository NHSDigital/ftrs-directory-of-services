ENVIRONMENT ?= mgmt
PACKAGE ?= python
BUILD_DIR := ../../../build/packages/$(PACKAGE)
ARTEFACT_BUCKET := ${REPO_NAME}-$(ENVIRONMENT)-artefacts-bucket
PACKAGE_VERSION := $(shell poetry version -s)
WHEEL_NAME := ftrs_python_packages-$(PACKAGE_VERSION)-py3-none-any.whl
PACKAGES_LAYER_NAME := ftrs-dos-python-packages-layer

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .poetry .pytest_cache .ruff_cache .tmp .venv .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)

install:
	poetry install

build:
	poetry build -o $(BUILD_DIR) -f wheel
	mkdir -p $(BUILD_DIR)/python
	poetry run pip install --no-deps --target=$(BUILD_DIR)/python $(BUILD_DIR)/$(WHEEL_NAME)
	cd $(BUILD_DIR) && zip -r $(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip python --exclude "*__pycache__/*"

lint:
	poetry run ruff check
	poetry run ruff format --check

unit-test:
	poetry run pytest

publish:
	aws s3 cp $(BUILD_DIR)/$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION)

