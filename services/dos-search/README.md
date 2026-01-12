# GP Search Service

This service provides FHIR-compliant API endpoints for healthcare system integrations, specifically designed to search for GP (General Practitioner) endpoints by ODS code.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Lambda-per-endpoint patterns](#lambda-per-endpoint-patterns)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Initial Setup](#initial-setup)
  - [Environment Configuration](#environment-configuration)
- [Development](#development)
  - [Code Structure](#code-structure)
  - [Testing](#testing)
  - [Linting and Formatting](#linting-and-formatting)
  - [Pre-commit Hooks](#pre-commit-hooks)
- [Deployment](#deployment)
- [Usage](#usage)
  - [Lambda Function Invocation](#lambda-function-invocation)
  - [Local Testing](#local-testing)
- [Contributing](#contributing)

## Overview

The GP Search service retrieves healthcare organization endpoints from a DynamoDB database based on ODS (Organization Data Service) codes and returns them in a FHIR-compliant Bundle format. This allows healthcare systems to discover electronic communication endpoints for specific organizations.

Key capabilities:

- Retrieval of organization and endpoint data by ODS code
- Mapping of DynamoDB records to FHIR resources (Organization, Endpoint)
- Combining related resources into a FHIR Bundle
- Error handling with FHIR OperationOutcome responses

## Architecture

The service uses:

- **AWS Lambda** for serverless execution
- **DynamoDB** for data storage
- **FHIR R4 resources** for healthcare data representation
- **Pydantic** for data validation and serialization
- **AWS Lambda Powertools** for logging and utilities

## Lambda-per-endpoint patterns

We support two related patterns:

1. **One Lambda per endpoint (default):** API Gateway integrates directly to a single Lambda.
2. **Set of Lambdas per endpoint (optional):** API Gateway integrates to a *router* Lambda which can delegate to one or more *worker* Lambdas.

The router/worker approach is useful when an endpoint grows in complexity, needs different scaling,
or needs internal separation without changing the public API.

For `dos-search`:

- `GET /_status` uses one Lambda (`lambdas/status_get/handler.py`).

- `GET /Organization` **uses one Lambda by default** (handler `functions/dos_search_ods_code_function.lambda_handler`).
- If you enable internal workers, `GET /Organization` switches to a router + workers (`lambdas/organization_get_router/handler.py` and `lambdas/organization_get_worker/handler.py`).

The router can run inline or delegate, controlled by environment variables:

- `DOS_SEARCH_ORCHESTRATION_MODE=inline|lambda` (default: `inline`)
- `DOS_SEARCH_ORG_WORKER_LAMBDA_NAMES=<comma-separated lambda names>` (preferred)
- `DOS_SEARCH_ORG_WORKER_LAMBDA_NAME=<lambda name>` (backwards compatible)

## Prerequisites

- [asdf](https://asdf-vm.com/) for runtime version management
- Access to appropriate AWS services
- You have read and followed the root `README.md` for first steps

## Getting Started

### Initial Setup

1. Clone the repository

   ```shell
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install all dependencies

   ```shell
   # From root directory
   make config

   # Then in the service directory
   cd services/dos-search
   make config
   ```

### Environment Configuration

1. Create an environment file by copying the template

   ```shell
   cp .env.sample .env
   ```

2. Fill in required values in the `.env` file

3. Activate environment variables

   ```shell
   export $(cat .env | xargs)
   ```

## Development

### Code Structure

```plain
├── functions/                           # Shared business logic
│   ├── dos_search_ods_code_function.py  # Original /Organization handler (reused by worker)
│   ├── organization_handler.py          # Shared /Organization handler used by router
│   └── lambda_invoker.py                # Utility for router -> worker invokes
├── health_check/                        # Shared health check routes
├── lambdas/                             # Per-endpoint Lambda entrypoints
│   ├── organization_get_router/handler.py
│   ├── organization_get_worker/handler.py
│   └── status_get/handler.py
├── scripts/
│   └── package_endpoint_lambdas.py      # Builds per-endpoint/per-role zips
└── ...                                 # Configuration files
```

### Testing

Run unit tests:

```shell
# Run all tests
poetry run pytest tests/unit

# Run with coverage report
poetry run pytest --cov=functions tests/unit

# Run specific test file
poetry run pytest tests/unit/functions/test_dos_search_ods_code_function.py
```

Run the lambda function locally for manual testing:

```shell
PYTHONPATH=$(git rev-parse --show-toplevel)/services/dos-search/functions poetry run python tests/manual_test.py
```

### Linting and Formatting

The project uses [ruff](https://github.com/charliermarsh/ruff) for linting and formatting.

```shell
# Check for linting and formatting issues
make lint

# Attempt to fix linting and formatting issues
make lint-fix
```

IDE Integration: Configure your IDE to use ruff for linting and formatting. See [ruff documentation](https://docs.astral.sh/ruff/editors/setup/) for details.

### Pre-commit Hooks

Pre-commit hooks are set up to automatically run linting and formatting checks before each commit.

```shell
# Pre-commit hooks will run automatically on commit
git commit

# To manually run pre-commit hooks
pre-commit run --all-files -c $(git rev-parse --show-toplevel)/scripts/config/pre-commit.yaml
```

## Deployment

Push your latest changes to the repository.
The GitHub Actions workflow will automatically build the Lambda function package and dependency layers, perform tests, and deploy onto the development environment.

## Usage

### Lambda Function Invocation

The Lambda function accepts an event with an `odsCode` parameter:

```json
{
  "odsCode": "O123"
}
```

### Local Testing

Use the `manual_test.py` script to test the Lambda function locally:

```shell
PYTHONPATH=$(git rev-parse --show-toplevel)/services/dos-search/functions poetry run python tests/manual_test.py
```

This will use the ODS_CODE from your environment variables to make a test request.

## Contributing

1. Set up development environment as described in [Getting Started](#getting-started)
2. Make code changes
3. Add tests for new functionality
4. Ensure all tests pass with `make test`
5. Check for linting/formatting issues with `make lint`
6. Create a pull request with your changes
7. Ensure GitHub Actions pass

## Dependency Management

Update dependencies:

```shell
# Update lock file with changes from pyproject.toml
poetry lock --no-update

# Update all dependencies to latest versions
poetry lock

# Update poetry environment with lock file changes
poetry install

# Update poetry environment with lock file changes, removing unused dependencies
poetry sync
```

## Troubleshooting

### Common Issues

1. **Missing environment variables**
   - Ensure all required environment variables are set in `.env` and exported

2. **AWS connectivity issues**
   - Verify AWS credentials are properly configured
   - Re-assume the correct AWS profile if necessary

     ```shell
     assume <role-name>
     ```

## Choosing between router+workers vs Step Functions

When an endpoint grows beyond a single Lambda, there are two common serverless patterns:

### Router + internal worker Lambdas (what we use for `/Organization` when enabled)

**Shape:** API Gateway r router Lambda r N internal worker lambdas (sync invokes)

Use this when:
- You need a **synchronous HTTP response** (request/response).
- The flow is mostly **linear** (A r B r C).
- Each step is fast and you remain within API Gateway + Lambda timeouts.
- You mainly want **deployment separation** (change one step without touching others).

Trade-offs:
- Orchestration logic (retries, branching) lives in code.
- More lambdas usually means more latency (multiple sync invokes).

### Step Functions (recommended once it becomes a real workflow)

**Shape:** API Gateway r Lambda r Step Function execution r N tasks (Lambdas)

Use this when:
- You need **retries/backoff**, **branches**, **compensation**, or **fan-out/fan-in**.
- You need better **operational visibility** (one execution view of all steps).
- Steps may be long-running or you want async patterns.

Trade-offs:
- Extra infrastructure and state-machine definitions to maintain.
- For a strictly synchronous endpoint, Step Functions can add complexity.

### Recommendation for `dos-search`

- Keep `GET /_status` as **one Lambda per endpoint**.
- Keep `GET /Organization` as **one Lambda by default**.
- Enable router + worker lambdas for `GET /Organization` only when separation is needed.
- If `GET /Organization` becomes a branching/long-running workflow, migrate orchestration to Step Functions.
