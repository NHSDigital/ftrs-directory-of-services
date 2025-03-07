BUILD_DIR := ../../build/services/data-migration


.PHONY: install lint test build

ensure-build-dir:
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf .poetry .pytest_cache .ruff_cache .tmp .venv .build .coverage coverage.xml
	rm -rf $(BUILD_DIR)

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

build: ensure-build-dir
	poetry build -f wheel -o $(BUILD_DIR)
	poetry export -f requirements.txt --output $(BUILD_DIR)/requirements.txt --without-hashes
