ENVIRONMENT ?= mgmt
PACKAGE ?= python
BUILD_DIR := ../../../build/packages/$(PACKAGE)
ARTEFACT_BUCKET := ${REPO_NAME}-$(ENVIRONMENT)-artefacts-bucket
PACKAGE_VERSION := $(shell poetry version -s)
WHEEL_NAME := ftrs_python_packages-$(PACKAGE_VERSION)-py3-none-any.whl
PYTHON_VERSION ?= 3.12
PLATFORM ?= manylinux2014_x86_64
PACKAGES_LAYER_NAME := ftrs-dos-python-packages-layer
RELEASE_BUILD ?= false
RELEASE_DIR ?= releases

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .poetry .pytest_cache .ruff_cache .tmp .venv .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)

install:
	poetry install

build: build-package build-layer

build-package: ensure-build-dir
	poetry build -o $(BUILD_DIR) -f wheel

build-layer:
	mkdir -p $(BUILD_DIR)/layer/python
	pip install \
		--target $(BUILD_DIR)/layer/python \
		--platform $(PLATFORM) \
		--implementation cp \
		--python-version $(PYTHON_VERSION) \
		--only-binary=:all: \
		--upgrade \
		$(BUILD_DIR)/$(WHEEL_NAME)
	cd $(BUILD_DIR)/layer && zip -r -q ../$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip * --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/layer/

lint:
	poetry run ruff check
	poetry run ruff format --check

lint-fix:
	poetry run ruff check --fix
	poetry run ruff format

unit-test:
	poetry run pytest

publish:
	if [ "$(RELEASE_BUILD)" = "false" ] ; then \
		aws s3 cp $(BUILD_DIR)/$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
	else \
		aws s3 cp $(BUILD_DIR)/$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(RELEASE_DIR)/$(APPLICATION_TAG)/$(PACKAGES_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
	fi
