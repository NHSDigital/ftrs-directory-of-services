
# FtRS Directory Of Services Ingestion API

This project provides testing for of the API that sends data into the FtRS Directory of Services, hosted on the NHS Digital API Management Platform (APIM).

## Table of Contents

- [Installation](#installation)
- [Linting](#linting)
- [Running Tests](#running-tests)
- [Environment Variables](#environment-variables)

## Installation

This project requires Python and Poetry as core dependencies.

```bash
poetry install
```

## Linting

Python code is linted and formatted using Ruff. The rules and arguments enabled can be found in the `pyproject.toml` file.

```bash
make lint # Runs ruff check and ruff format
```

To automatically format Python code and fix some linting issues, you can use:

```bash
poetry run ruff check --fix  # Runs linting with fix mode enabled
poetry run ruff format       # Runs the python code formatter
```

## Running Tests

Tests are run using Pytest. You can use the make target to conveniently run these tests, or run them directly using pytest.

```bash
make unit-test
# or
poetry run pytest
```

To run tests with coverage:

```bash
make coverage
```

## Environment Variables

The following environment variables are required for testing and running locally:

- `APIGEE_ENVIRONMENT` - The target APIM environment (e.g., internal-dev)
- `API_KEY` - Valid API key for authentication

Copy `.env.example` and rename to `.env` and fill in the required values. Do not update the `env.example` file with the values as this is committed to version control.

## API Documentation

- OpenAPI specification: `specification/`
- NHS Digital Developer Hub
