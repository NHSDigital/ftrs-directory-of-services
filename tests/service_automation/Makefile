SERVICE ?= service-automation
PYTHON_VERSION ?= 3.12
BUILD_DIR := build
ALLURE_RESULTS := allure-results
ALLURE_REPORTS := allure-reports
MARKERS ?= ui is-api is-infra
TEST_TYPE ?= non-ui
LINT_HINT := Hint: Run 'make lint-fix' to fix any fixable linting errors and to format all files in the project

# ==============================================================================

.PHONY: clean install config lint lint-staged lint-fix pre-commit test report _install-dependency _install-dependencies

clean:
	rm -rf .pytest_cache .ruff_cache .tmp .build
	rm -rf $(BUILD_DIR)
	rm -rf $(ALLURE_RESULTS)
	rm -rf $(ALLURE_REPORTS)
	rm -rf venv
	rm -rf downloads
	find . -name "*.log" -type f -delete

install: config

config:
	make _install-dependencies
	poetry install --no-root --no-interaction --with shared
	poetry run playwright install chromium

lint:
	poetry run ruff check || { echo "$(LINT_HINT)"; exit 1; }
	poetry run ruff format --check || { echo "$(LINT_HINT)"; exit 1; }

lint-staged:
	files=$$(git diff --relative --name-only --cached -- '*.py'); \
	if [ -z "$$files" ]; then \
		echo "No files staged"; \
	else \
		echo "$$files" | xargs poetry run ruff check || { echo "$(LINT_HINT)"; exit 1; }; \
		echo "$$files" | xargs poetry run ruff format --check || { echo "$(LINT_HINT)"; exit 1; }; \
	fi

lint-fix:
	poetry run ruff check --fix
	poetry run ruff format

pre-commit: lint-staged

test:
	@for marker in $(MARKERS); do \
		echo "Running tests for marker: $$marker"; \
		echo "Running tests for env: $$ENVIRONMENT"; \
		if [ "$$marker" = "ui" ] || [ "$(TEST_TYPE)" = "ui" ]; then \
			poetry run pytest -m "$$marker" -p allure_pytest --alluredir=$(ALLURE_RESULTS); \
		else \
			poetry run pytest -m "$$marker" -p allure_pytest_bdd --alluredir=$(ALLURE_RESULTS); \
		fi; \
	done

# Run tests against LocalStack (no AWS credentials required)
# This now includes Lambda tests via local HTTP servers
test-local:
	@echo "Running tests against LocalStack (testcontainers)..."
	@echo "Docker must be running for this to work."
	@echo "Lambda tests run via local FastAPI servers."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
		poetry run python -m pytest -m "is-infra" --ignore=tests/step_definitions/ui_steps -v

# Run data migration tests locally with local SQL files
test-local-data-migration:
	@echo "Running data migration tests against LocalStack (testcontainers)..."
	@echo "Docker must be running for this to work."
	@echo "Uses local SQL files from tests/sql_files/"
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
		poetry run python -m pytest tests/step_definitions/data_migration_steps/ -v

# Run a quick smoke test locally to verify testcontainers setup (S3 and DynamoDB)
test-local-smoke:
	@echo "Running smoke test against LocalStack..."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
		poetry run python -m pytest -m "is-infra" -k "s3 or data" --tb=short -v

# Run Lambda tests locally (DOS Search via local FastAPI server)
test-local-lambda:
	@echo "Running Lambda tests against local servers..."
	@echo "This starts DOS Search as a local FastAPI server."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
		poetry run python -m pytest tests/step_definitions/infra_steps/test_lambda.py -v

# Run ETL ODS local tests (Extractor only - Transformer requires JWT auth setup)
test-local-etl-ods:
	@echo "Running ETL ODS local tests against LocalStack + Mock ODS API..."
	@echo "This tests the ETL ODS extractor with a mock ODS Terminology API."
	@echo "Note: Full pipeline tests are excluded (require JWT auth configuration)."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
		poetry run python -m pytest tests/step_definitions/etl_ods_steps/test_etl_ods_local.py \
		-m "not slow" -v

# Run CRUD APIs mock server tests (for ETL ODS integration)
# Note: For full CRUD APIs integration tests, use services/crud-apis/tests/
test-local-crud-apis:
	@echo "Running CRUD APIs mock server tests..."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	PROJECT_NAME=ftrs-dos \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
		poetry run python -m pytest tests/step_definitions/local_steps/test_crud_apis_mock.py -v

# Run CRUD APIs local integration tests (real CRUD APIs code against LocalStack)
# This uses FastAPI TestClient to test the actual CRUD APIs handlers
test-local-crud-apis-integration:
	@echo "Running CRUD APIs local integration tests..."
	@echo "This runs the real CRUD APIs code against LocalStack DynamoDB."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	PROJECT_NAME=ftrs-dos \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
	PYTHONPATH="$(shell pwd)/../../services/crud-apis:$$PYTHONPATH" \
		poetry run python -m pytest tests/step_definitions/local_steps/test_crud_apis_local_integration.py -v

# Run comprehensive CRUD APIs Organization tests locally (100+ tests)
# This is the full business logic test suite - validation, sanitization, roles, telecom, etc.
# The AWS feature file now only contains smoke tests for infrastructure verification.
test-local-crud-apis-comprehensive:
	@echo "Running comprehensive CRUD APIs Organization tests against LocalStack..."
	@echo "This runs 100+ business logic tests without requiring AWS deployment."
	@echo "Docker must be running for this to work."
	USE_LOCALSTACK=true ENVIRONMENT=local WORKSPACE=test COMMIT_HASH=local-test \
	PROJECT_NAME=ftrs-dos \
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 \
	PYTHONPATH="$(shell pwd)/../../services/crud-apis:$$PYTHONPATH" \
		poetry run python -m pytest tests/step_definitions/local_steps/test_crud_apis_organization_comprehensive.py -v

# Run ALL local tests (comprehensive suite for CI without AWS)
test-local-all:
	@echo "Running ALL local tests against LocalStack..."
	@echo "This includes: infra, data-migration, CRUD APIs, ETL ODS"
	@echo "Docker must be running for this to work."
	$(MAKE) test-local
	$(MAKE) test-local-data-migration
	$(MAKE) test-local-crud-apis-comprehensive
	$(MAKE) test-local-etl-ods

# Run data migration tests (requires AWS credentials for S3 test data)
# These tests use LocalStack for DynamoDB but need real S3 for SQL setup scripts
test-data-migration:
	@echo "Running data migration tests (requires AWS credentials for S3 test data)..."
	poetry run python -m pytest -m "data-migration" -v

report:
	allure generate --single-file -c -o $(ALLURE_REPORTS) $(ALLURE_RESULTS)

# ==============================================================================

_install-dependency: # Install asdf dependency - mandatory: name=[listed in the '.tool-versions' file]; optional: version=[if not listed]
	echo ${name}
	asdf plugin add ${name} ||:
	asdf plugin update ${name} ||:
	asdf install ${name} $(or ${version},)

_install-dependencies: # Install all the dependencies listed in .tool-versions
	for plugin in $$(grep ^[a-z] .tool-versions | sed 's/[[:space:]].*//'); do \
		make _install-dependency name="$${plugin}"; \
	done

# ==============================================================================

${VERBOSE}.SILENT: \
	clean \
	config \
	_install-dependency \
	_install-dependencies \
	install \
	lint \
	lint-staged \
	lint-fix \
