SERVICE ?= service-automation
PYTHON_VERSION ?= 3.12
BUILD_DIR := build
ALLURE_RESULTS := allure-results
ALLURE_REPORTS := allure-reports
MARKERS ?= ui is-api is-infra
TEST_TYPE ?= non-ui

# ==============================================================================

.PHONY: clean install config test report

clean:
	rm -rf .pytest_cache .ruff_cache .tmp .build
	rm -rf $(BUILD_DIR)
	rm -rf $(ALLURE_RESULTS)
	rm -rf $(ALLURE_REPORTS)
	rm -rf venv

install: config

config:
	make _install-dependencies
	poetry install --no-root --no-interaction
	poetry run playwright install chromium

test:
	@for marker in $(MARKERS); do \
		echo "Running tests for marker: $$marker"; \
		if [ "$$marker" = "ui" ] || [ "$(TEST_TYPE)" = "ui" ]; then \
			poetry run pytest -m "$$marker" -p allure_pytest --alluredir=$(ALLURE_RESULTS); \
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
