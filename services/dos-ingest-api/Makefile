SERVICE ?= apim-ingest-api

install-dependencies:
	poetry install --no-interaction

clean:
	rm -rf .pytest_cache .ruff_cache .tmp .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)
	rm -rf $(DEPENDENCY_DIR)

lint:
	poetry run ruff check
	poetry run ruff format --check

test: unit-test

unit-test: coverage

coverage:
	poetry run pytest --cov-report xml:coverage-${SERVICE}.xml tests

pre-commit: lint
