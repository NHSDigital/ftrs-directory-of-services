ENVIRONMENT ?= mgmt
SERVICE ?= etl-ods
PYTHON_VERSION ?= 3.12
BUILD_DIR := ../../build/services/${SERVICE}
DEPENDENCY_DIR := ${BUILD_DIR}/dependency-layer
PLATFORM ?= manylinux2014_x86_64
ARTEFACT_BUCKET := ${REPO_NAME}-${ENVIRONMENT}-artefacts-bucket
DEPENDENCY_LAYER_NAME := ftrs-dos-${SERVICE}-python-dependency-layer
PRODUCER_LAMBDA_NAME := ftrs-dos-${SERVICE}-processor-lambda
CONSUMER_LAMBDA_NAME := ftrs-dos-${SERVICE}-consumer-lambda
LAMBDA_NAME := ftrs-dos-${SERVICE}-lambda
RELEASE_BUILD ?= false
RELEASE_DIR ?= releases

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

unit-test:
	poetry run pytest tests/unit

build: ensure-build-dir build-dependency-layer
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes

build-producer-lambda:
	mkdir -p $(BUILD_DIR)/producer-tmp
	cp -r producer $(BUILD_DIR)/producer-tmp/
	cp utilities.py $(BUILD_DIR)/producer-tmp/
	cd $(BUILD_DIR)/producer-tmp && zip -r -q ../$(PRODUCER_LAMBDA_NAME)-$(APPLICATION_TAG).zip * --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/producer-tmp

build-consumer-lambda:
	mkdir -p $(BUILD_DIR)/consumer-tmp
	cp -r consumer $(BUILD_DIR)/consumer-tmp/
	cp utilities.py $(BUILD_DIR)/consumer-tmp/
	cd $(BUILD_DIR)/consumer-tmp && zip -r -q ../$(CONSUMER_LAMBDA_NAME)-$(APPLICATION_TAG).zip * --exclude "*__pycache__/*"
	rm -rf $(BUILD_DIR)/consumer-tmp

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
	if [ "$(RELEASE_BUILD)" = "false" ] ; then \
		aws s3 cp $(BUILD_DIR)/$(PRODUCER_LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(PRODUCER_LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
		aws s3 cp $(BUILD_DIR)/$(CONSUMER_LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(CONSUMER_LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
		aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
	else \
		aws s3 cp $(BUILD_DIR)/$(PRODUCER_LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(RELEASE_DIR)/$(APPLICATION_TAG)/$(PRODUCER_LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
		aws s3 cp $(BUILD_DIR)/$(CONSUMER_LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(RELEASE_DIR)/$(APPLICATION_TAG)/$(CONSUMER_LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
		aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(ARTEFACT_BUCKET)/$(RELEASE_DIR)/$(APPLICATION_TAG)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION);\
	fi

pre-commit: lint
