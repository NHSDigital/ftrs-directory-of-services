.PHONY: help venv install jwt-token clean

PYTHON_CMD := $(shell command -v python3 || command -v python)
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
REQUIREMENTS := PyJWT[crypto] boto3 requests

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

$(VENV)/bin/activate:
	@if [ -z "$(PYTHON_CMD)" ]; then \
		echo "No Python installation found. Please install Python."; \
		exit 1; \
	fi
	$(PYTHON_CMD) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install $(REQUIREMENTS)

venv: $(VENV)/bin/activate

install: venv

jwt-token:
ifndef env
	$(error env parameter is required. Usage: make jwt-token env=local api=dos-ingest)
endif
ifndef api
	$(error api parameter is required. Usage: make jwt-token env=local api=dos-ingest)
endif
	@if [ ! -d "$(VENV)" ]; then $(MAKE) venv; fi
	$(PYTHON) generate_jwt.py $(env) $(api)

clean:
	rm -rf $(VENV)

.DEFAULT_GOAL := help
