SERVICE ?= gp-search
PYTHON_VERSION ?= 3.12
BUILD_DIR := ../../build/services/${SERVICE}
DEPENDENCY_DIR := ${BUILD_DIR}/dependency-layer
PLATFORM ?= manylinux2014_x86_64
S3_BUCKET := ${REPO_NAME}-$(ENVIRONMENT)-artefacts-bucket
POETRY_VERSION := $(shell poetry version -s)
WHEEL_NAME := functions-$(POETRY_VERSION)-py3-none-any.whl
DEPENDENCY_LAYER_NAME := ftrs-dos-${SERVICE}-python-dependency-layer
LAMBDA_NAME := ftrs-dos-${SERVICE}-lambda


# ==============================================================================

# Example CI/CD targets are: dependencies, build, publish, deploy, clean, etc.
clean:
	rm -rf .pytest_cache .ruff_cache .tmp .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)
	rm -rf $(DEPENDENCY_DIR)

install: config

config:
	make _install-dependencies
	poetry install --no-interaction

lint:
	poetry run ruff check
	poetry run ruff format --check

lint-fix:
	poetry run ruff check --fix
	poetry run ruff format

test: unit-test

unit-test:
	poetry run pytest tests/unit

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

dependencies: # Install dependencies needed to build and test the project @Pipeline
	# TODO: Implement installation of your project dependencies

build: ensure-build-dir build-dependency-layer
	poetry build -f wheel -o $(BUILD_DIR)
	echo "$(COMMIT_HASH)" > $(BUILD_DIR)/metadata.txt
	mv $(BUILD_DIR)/$(WHEEL_NAME) $(BUILD_DIR)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip

build-dependency-layer: clean
	mkdir -p $(DEPENDENCY_DIR)/python
	poetry export --without dev --without test --without-hashes > $(DEPENDENCY_DIR)/requirements.txt
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
	aws s3 cp $(BUILD_DIR)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip s3://$(S3_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(LAMBDA_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION)
	aws s3 cp $(BUILD_DIR)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip s3://$(S3_BUCKET)/$(WORKSPACE)/$(COMMIT_HASH)/$(DEPENDENCY_LAYER_NAME)-$(APPLICATION_TAG).zip --region $(AWS_REGION)

# ==============================================================================

_install-dependency: # Install asdf dependency - mandatory: name=[listed in the '.tool-versions' file]; optional: version=[if not listed]
	echo ${name}
	asdf plugin add ${name} ||:
	asdf install ${name} $(or ${version},)

_install-dependencies: # Install all the dependencies listed in .tool-versions
	for plugin in $$(grep ^[a-z] .tool-versions | sed 's/[[:space:]].*//'); do \
		make _install-dependency name="$${plugin}"; \
	done

pre-commit: lint

# ==============================================================================

${VERBOSE}.SILENT: \
	build \
	clean \
	config \
	dependencies \
	deploy \
