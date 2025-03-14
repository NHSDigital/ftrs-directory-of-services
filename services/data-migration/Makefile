SERVICE ?= data-migration
PYTHON_VERSION ?= 3.12
BUILD_DIR := ../../build/services/${SERVICE}
DEPENDENCY_DIR := ${BUILD_DIR}/dependency-layer
PLATFORM ?= manylinux2014_x86_64
DEPENDENCY_LAYER_NAME := ftrs-dos-${SERVICE}-python-dependency-layer

.PHONY: install lint test build

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .poetry .pytest_cache .ruff_cache .tmp .venv .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)
	rm -rf $(DEPENDENCY_DIR)

install: install-dependencies

install-dependencies:
	asdf install
	poetry install

lint:
	poetry run ruff check
	poetry run ruff format --check

test: unit-test

unit-test:
	poetry run pytest tests/unit

build: ensure-build-dir build-dependency-layer
	poetry build -f wheel -o $(BUILD_DIR)
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
	cd $(DEPENDENCY_DIR) && zip -r -q ../$(DEPENDENCY_LAYER_NAME)-$(COMMIT_HASH).zip * --exclude "*__pycache__/*"
