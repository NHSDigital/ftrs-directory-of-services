# GP Search Service

This service provides FHIR-compliant API endpoints for healthcare system integrations, specifically designed to search for GP (General Practitioner) endpoints by ODS code.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
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
   cd services/gp-search
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
├── functions/                # Lambda function code
│   ├── ftrs_service/         # FTRS service implementation
│   │   ├── fhir_mapper/      # Mapping between data models and FHIR
│   │   ├── repository/       # Data access layer
│   │   ├── config.py         # Configuration handling
│   │   └── ftrs_service.py   # Main service logic
│   └── gp_search_function.py # Lambda handler entry point
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── conftest.py           # Test configuration and fixtures
│   └── manual_test.py        # Script for local testing
└── ...                       # Configuration files
```

### Testing

Run unit tests:

```shell
# Run all tests
poetry run pytest tests/unit

# Run with coverage report
poetry run pytest --cov=functions tests/unit

# Run specific test file
poetry run pytest tests/unit/functions/test_gp_search_function.py
```

Run the lambda function locally for manual testing:

```shell
PYTHONPATH=$(git rev-parse --show-toplevel)/services/gp-search/functions poetry run python tests/manual_test.py
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
PYTHONPATH=$(git rev-parse --show-toplevel)/services/gp-search/functions poetry run python tests/manual_test.py
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
