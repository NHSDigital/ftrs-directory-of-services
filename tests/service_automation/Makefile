SERVICE ?= service-automation
PYTHON_VERSION ?= 3.12
BUILD_DIR := build
ALLURE_RESULTS := allure-results
ALLURE_REPORTS := allure-reports
MARKERS ?=
TEST_TYPE ?= bdd
LINT_HINT := Hint: Run 'make lint-fix' to fix any fixable linting errors and to format all files in the project

# ==============================================================================

.PHONY: clean install config lint lint-staged lint-fix pre-commit test report _install-dependency _install-dependencies

# import dotenv file if exists
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

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
	files=$$(git diff --relative --name-only --cached --diff-filter=d -- '*.py'); \
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
	@if [ "$(TEST_TYPE)" = "apim" ]; then \
		if [ -n "$(WORKSPACE)" ]; then \
			PROXY_NAME="$(API_NAME)--$(APIM_ENV)--$(API_NAME)-$(WORKSPACE)_FHIR_R4"; \
		else \
			PROXY_NAME="$(API_NAME)--$(APIM_ENV)_FHIR_R4"; \
		fi; \
	fi; \
	for marker in $(MARKERS); do \
		echo "Running tests for marker: $$marker"; \
		echo "Running tests for test type: $$TEST_TYPE"; \
		echo "Running tests for env: $$ENVIRONMENT"; \
		if [ "$$marker" = "ui" ] || [ "$(TEST_TYPE)" = "ui" ]; then \
			poetry run pytest -m "$$marker" -p allure_pytest --alluredir=$(ALLURE_RESULTS); \
		elif [ "$(TEST_TYPE)" = "apim" ]; then \
			echo "Running tests for API name: $(API_NAME)"; \
			echo "Running tests for proxy name: $$PROXY_NAME"; \
			poetry run pytest -m "$$marker" --api-name=$(API_NAME) --proxy-name=$$PROXY_NAME -p allure_pytest_bdd --alluredir=$(ALLURE_RESULTS); \
		else \
			poetry run pytest -m "$$marker" -p allure_pytest_bdd --alluredir=$(ALLURE_RESULTS); \
		fi; \
	done

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
