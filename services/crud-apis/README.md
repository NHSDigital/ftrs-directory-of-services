# CRUD APIs (DoS Ingest)

FastAPI service for CRUD-style ingest endpoints used to update DoS data.

## Structure

- `dos_ingest/app.py` - FastAPI app setup, middleware, exception handlers, and routers
- `dos_ingest/router/` - endpoint routers (`Organization`, `Location`, `HealthcareService`)
- `dos_ingest/handler.py` - AWS Lambda entrypoint (via Mangum)
- `tests/unit` and `tests/integration` - service test suites

## Local setup

From this directory (`services/crud-apis`):

1. Install dependencies:
	- `make install-dependencies`
	- or `poetry install`
2. Create local env values from `.env.sample`.

## Run locally

Start the API with Uvicorn:

- `poetry run uvicorn dos_ingest.app:app --host 0.0.0.0 --port 4000 --reload`

## Developer workflow

- Lint: `make lint`
- Auto-fix lint/formatting: `make lint-fix`
- Unit tests: `poetry run pytest -m "not integration"`
- Integration tests: `poetry run pytest -m integration tests/integration`
- Full test run: `poetry run pytest`

## Build and packaging

- Build Lambda artefacts and dependency layer: `make build`
- Build dependency layer only: `make build-dependency-layer`

Build output is written to `../../build/services/crud-apis`.
