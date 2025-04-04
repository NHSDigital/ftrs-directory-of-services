PACKAGE ?= python
BUILD_DIR := ../../../build/packages/$(PACKAGE)
S3_BUCKET := ${REPO_NAME}-$(ENVIRNOMENT)-artefacts-bucket
PACKAGE_VERSION := $(shell poetry version -s)
WHEEL_NAME := ftrs_python_packages-$(PACKAGE_VERSION)-py3-none-any.whl

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .poetry .pytest_cache .ruff_cache .tmp .venv .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)

install:
	poetry install

build:
	poetry build -o $(BUILD_DIR) -f wheel

lint:
	poetry run ruff check
	poetry run ruff format --check

unit-test:
	poetry run pytest

publish:
	aws s3 cp $(BUILD_DIR)/$(WHEEL_NAME) s3://$(S3_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(WHEEL_NAME) --region $(AWS_REGION)

