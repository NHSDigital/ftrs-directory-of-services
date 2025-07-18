ENVIRONMENT ?= mgmt
SERVICE ?= crud-apis
PYTHON_VERSION ?= 3.12
BUILD_DIR := ../../build/services/${SERVICE}
DEPENDENCY_DIR := ${BUILD_DIR}/dependency-layer
PLATFORM ?= manylinux2014_x86_64
ARTEFACT_BUCKET := ${REPO_NAME}-${ENVIRONMENT}-artefacts-bucket
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := crud_apis-$(POETRY_VERSION)-py3-none-any.whl
DEPENDENCY_LAYER_NAME := ftrs-dos-${SERVICE}-python-dependency-layer
LAMBDA_NAME := ftrs-dos-${SERVICE}-lambda

.PHONY: install lint test build

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .pytest_cache .ruff_cache .tmp .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)
	rm -rf $(DEPENDENCY_DIR)

install: install-dependencies

install-dependencies:
	asdf install
	poetry install --no-interaction

lint:
	poetry run ruff check
	poetry run ruff format --check

test: unit-test

unit-test: coverage

coverage:
	poetry run pytest --cov-report xml:coverage-${SERVICE}.xml organisations/tests/unit healthcare_service/tests/ location/tests/ utils/tests/

start-organisations-api:
	poetry run poe start-organisations-api

start-healthcare-api:
	poetry run poe start-healthcare-api

start-location-api:
	poetry run poe start-location-api

start-all-apis:
	poetry run poe start-all-apis

build: ensure-build-dir build-dependency-layer
	poetry build -f wheel -o $(BUILD_DIR)
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	mv $(BUILD_DIR)/$(WHEEL_NAME) $(BUILD_DIR)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes

build-dependency-layer: clean
	mkdir -p $(DEPENDENCY_DIR)/python
	poetry export --without dev --without-hashes > $(DEPENDENCY_DIR)/requirements.txt
	pip install \
	--platform $(PLATFORM) \
	--target $(DEPENDENCY_DIR)/python \
	--implementation cp \
	--python-version $(PYTHON_VERSION) \
	--no-deps \
	--upgrade \
	-r $(DEPENDENCY_DIR)/requirements.txt
	cd $(DEPENDENCY_DIR) && zip -r -q ../$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip * --exclude "*__pycache__/*"

publish:
	aws s3 cp $(BUILD_DIR)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION)
