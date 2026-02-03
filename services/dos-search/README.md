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

We intend to standardise on **one Lambda per endpoint**.

For `dos-search` use the following layout:

- `GET /_status` will use one Lambda (`health_check/handler.py`).
  The handler delegates to the implementation in
  `health_check/health_check_function.py` (the Lambda entrypoint is
  `health_check/handler.py`, which exposes the `/_status` route). The handler
  resolves the `health_check` app and returns a 200/500 status depending on
  repository health.
- `GET /Organization` will use one Lambda (`endpoints/organisation/handler.py`).
  The handler delegates to the implementation in
  `endpoints/organisation/dos_search_ods_code_function.py`.

  Implementation note: the active Organization endpoint logic lives in
  `endpoints/organisation/dos_search_ods_code_function.py` (it exposes the
  `/Organization` route and a `lambda_handler`). The per-endpoint wrapper
  `endpoints/organisation/handler.py` wires the runtime and delegates to the
  implementation.

### Naming conventions

We will use **two names** for the same Lambda:

- **Python folder/module name (snake_case):** used in handler paths inside the ZIP
  - Example: `endpoints/triage_code/handler.lambda_handler`
- **Artefact + Terraform `lambda_name` (kebab-case):** used for ZIP and
  S3 object naming
  - Example: `triage-code`

The packaging script will convert snake_case folder names into kebab-case
artefact names.

## Build artefacts (proposal)

The packaging script will produce endpoint ZIPs. The script
should live at:

- `scripts/package_endpoint_lambdas.py`

Script will build one ZIP per endpoint and
include shared code from `common/` inside each endpoint ZIP so handlers
can import it at runtime.

### Status (proposal)

- Packaging: Update `scripts/package_endpoint_lambdas.py` so it
  discovers endpoint folders under `endpoints/` and includes the `common/`
  package inside each endpoint ZIP. Artefacts will use the pattern
  `ftrs-dos-dos-search-<lambda>-lambda-<tag>.zip`.
- Terraform: Update stacks to reference handlers at `endpoints/<name>/handler.lambda_handler` for organisation and triage lambdas. The `_status` route lives in `health_check`; add `health_check/handler.py` as the Lambda entrypoint and ensure packaging includes `health_check`.
- Compatibility: The canonical implementation of `OrganizationQueryParams` lives in
  `common.organization_query_params`. Update any legacy imports that reference
  `endpoints.organisation.organization_query_params` to import from the `common`
  module. Prefer updating callers to import `common.organization_query_params` so
  the canonical location is used consistently across the codebase.
- Cleanup: Update any legacy imports/references.
- Prefer referencing the packaged handler path used by Terraform:
  `endpoints/organisation/handler.lambda_handler` (this file wires the
  runtime and delegates to `dos_search_ods_code_function`).
Removing old references prevents confusion and ensures CI/packaging pick up
the correct, single implementation.

### Next steps

- When migrating callers, update imports to reference
   `common.organization_query_params` and removing the old path.
- Confirm CI/publish uploads the per-endpoint zip artefacts to the S3
  object keys Terraform expects. The publish target uploads
  `*-lambda-$(APPLICATION_TAG).zip` artefacts and matches the new names.

### Quick build & publish

From `services/dos-search`:

```shell
# Build per-endpoint artefacts into the build dir
make build-endpoint-lambdas APPLICATION_TAG=test-tag

# Or run the script directly
poetry run python scripts/package_endpoint_lambdas.py \
  --out build \
  --application-tag test-tag

# Publish (example; CI normally does this)
make publish APPLICATION_TAG=test-tag
```

### Guidance for reviewers

- Verify CI uploads create endpoint ZIPs named like `ftrs-dos-dos-search-<lambda>-lambda-<tag>.zip` and that S3 keys in Terraform match those artefacts
- Confirm Terraform handler settings reference per-endpoint handlers (e.g. `endpoints/organisation/handler.lambda_handler`)
- Update any infra or automation that relied on `functions/` to use `endpoints/` or imports from `common/`
- Ensure packaging includes `health_check` when the `_status` route is present

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
├── functions/                          # Lambda function code
│   ├── ftrs_service/                   # FTRS service implementation
│   │   ├── fhir_mapper/                # Mapping between data models and FHIR
│   │   ├── repository/                 # Data access layer
│   │   ├── config.py                   # Configuration handling
│   │   └── ftrs_service.py             # Main service logic
│   └── dos_search_ods_code_function.py # Lambda handler entry point
├── tests/                              # Test suite
│   ├── unit/                           # Unit tests
│   ├── conftest.py                     # Test configuration and fixtures
│   └── manual_test.py                  # Script for local testing
└── ...                                 # Configuration files
```

### Proposed code structure (per-endpoint)

This is the proposed structure when migrating to one Lambda per endpoint. It keeps shared code in `common/` and places each endpoint implementation under `endpoints/` with a small handler wrapper.

```plain
├── endpoints/                          # Per-endpoint Lambda code
│   ├── organisation/                   # /Organization endpoint
│   │   ├── handler.py                  # Lambda entrypoint (handler.lambda_handler)
│   │   └── dos_search_ods_code_function.py  # Implementation/shared imports
│   └── triage_code/                    # /triage_code endpoint
│       ├── handler.py
│       └── triage_code_function.py
├── common/                             # Shared code included in each package
│   ├── organization_query_params.py
│   ├── error_util.py
│   └── ftrs_service/                    # (optional) shared service helpers
├── health_check/                       # Health/status endpoint
│   └── handler.py
├── scripts/
│   └── package_endpoint_lambdas.py     # Builds one zip per endpoint
└── tests/
    └── unit/
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
