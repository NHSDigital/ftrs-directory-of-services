# DoS Search Service

This service provides FHIR-compliant API endpoints for healthcare system integrations, specifically designed to search for Directory of Services (DoS) endpoints by ODS code.

## Table of Contents

- [DoS Search Service](#dos-search-service)
  - [Table of Contents](#table-of-contents)
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
  - [Dependency Management](#dependency-management)
  - [Monitoring and Alerting](#monitoring-and-alerting)
    - [Alarm Configuration](#alarm-configuration)
    - [Slack Notifications](#slack-notifications)
    - [Architecture Flow](#architecture-flow)
  - [Troubleshooting](#troubleshooting)
    - [Common Issues](#common-issues)

## Overview

The DoS Search service retrieves healthcare organization endpoints from a DynamoDB database based on ODS (Organization Data Service) codes and returns them in a FHIR-compliant Bundle format. This allows healthcare systems to discover electronic communication endpoints for specific organizations.

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
├── infrastructure/stacks/dos_search/   # Infrastructure as Code
│   ├── alarms/
│   │   └── lambda-config.json          # Alarm metric definitions
│   ├── alarms.tf                       # SNS topic for alarms
│   ├── cloudwatch_alarms.tf            # CloudWatch alarm resources
│   ├── slack_notifications.tf          # Slack notification Lambda
│   └── variables.tf                    # Terraform variables (alarm thresholds)
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

## Monitoring and Alerting

The service includes CloudWatch alarms and Slack notifications for operational monitoring:

### Alarm Configuration

Alarms are configured using Terraform variables and JSON configuration files:

- **Alarm Definitions**: [`alarms/lambda-config.json`](../../infrastructure/stacks/dos_search/alarms/lambda-config.json) defines which metrics to monitor and alarm conditions
- **Threshold Values**: Terraform variables in [`variables.tf`](../../infrastructure/stacks/dos_search/variables.tf) set the threshold values for each alarm (`Line 136` onwards)
- **Alarm Creation**: [`cloudwatch_alarms.tf`](../../infrastructure/stacks/dos_search/cloudwatch_alarms.tf) creates CloudWatch alarms by combining the configuration and thresholds

Monitored metrics for both Search and Health Check Lambdas:
- **Duration**: Average execution time
- **Concurrent Executions**: Number of simultaneous executions
- **Throttles**: Lambda throttling events
- **Errors**: Error count over evaluation period
- **Invocations**: Invocation rate (alerts if too low)

### Slack Notifications

CloudWatch alarms are automatically sent to Slack via:

- **SNS Topic**: [`alarms.tf`](../../infrastructure/stacks/dos_search/alarms.tf) creates the SNS topic for alarm notifications
- **Lambda Function**: [`slack_notifications.tf`](../../infrastructure/stacks/dos_search/slack_notifications.tf) defines a Lambda that flattens alarm JSON and sends to Slack
- **Webhook**: Slack webhook URL is managed via Terraform variables (not in code)

### Architecture Flow

1. CloudWatch detects metric threshold breach
2. Alarm publishes to SNS topic
3. SNS triggers Slack notification Lambda
4. Lambda flattens alarm data and sends to `#ftrs-dos-search-alerts` slack channel.

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
