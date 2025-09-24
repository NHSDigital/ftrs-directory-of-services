# Service Test Automation Framework

## Overview

This is a Service Test Automation Framework using pytest-bdd and Playwright for validating API Testing,
AWS Infra Testing like Buckets, etc. and UI Testing.
It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```text
service_automation
├── allure-reports
├── allure-results
├── downloads
├── tests
│   ├── csv_files
│   ├── features
│   │   ├── is_api_features
│   │   └── is_infra_features
│   ├── oas_schemas
│   ├── pages
│   │   └── ui_pages
│   ├── step_definitions
│   │   ├── is_api_steps
│   │   ├── is_infra_steps
│   │   └── ui_steps
│   └── utilities
│       ├── common
│       └── infra
├── .tool-versions
├── Makefile
├── README.MD
└── pyproject.toml
```

## Prerequisites

- [asdf](https://asdf-vm.com/) for runtime version management
- Access to appropriate AWS services
- You have read and followed the root `README.md` for first steps

### Clone the repository

```shell
git clone <repository-url>
cd <repository-directory>
```

### Setup development environment

```shell
# From root directory
make config

# Then in the service_automation directory
cd tests/service_automation
make config
```

### AWS Configuration

Make sure your AWS CLI is configured and authenticated:

```shell
aws configure
aws sts get-caller-identity
```

You'll be prompted to enter:

```plain
AWS Access Key ID:
AWS Secret Access Key:
Default region (e.g., us-east-1, us-west-2):
Output format (json, table, text – default is json):
```

Alternatively, configure manually by editing these files:

```plain
Linux/macOS: ~/.aws/credentials and ~/.aws/config
Windows: C:\Users\USERNAME\.aws\credentials and C:\Users\USERNAME\.aws\config
```

Change aws config file with values listed in Service Teams - Set up SSO for AWS confluence page. Also use Dos developer profile from your aws console for your CLI connection.

### Service Test Configuration

The `.env.sample` file of the framework contains the variables that are required to be set when running locally.

Create a copy of `.env.sample` and name it `.env`, filling in the missing variable values.

This dotenv file will be automatically loaded when running the tests.

The workspace is defined as:

```shell
WORKSPACE= # when running against the main branch
WORKSPACE=dr-xxx  # when running against task branch dr-xxx
```

Note that if the branch has not been pushed with the dev pipeline successfully deployed the app then the script will fail as there will not be any infrastructure built that relates to the branch.

## Running Tests

### Running UI tests

```shell
make test MARKERS="ui"
```

### Running IS API tests

```shell
make test MARKERS="is-api"
```

### Running IS Infrastructure tests

```shell
make test MARKERS="is-infra"
```

### Running specific marked tests

Run specific marked tests, for example `@is-api`

```shell
make test MARKERS="is-api"
```

### Running Data Migration tests

```shell
make test MARKERS="data-migration"
```

Or you can run tests for multiple markers

```shell
make test MARKERS="is-api is-infra"
```

### Running specific feature tests

```shell
poetry run pytest tests/step_definitions/is_infra_steps/test_s3_bucket.py -p allure_pytest_bdd --alluredir=allure-results
```

### Generate Allure reports

```shell
make report
```

### Run all tests and generate Allure reports

```shell
make --ignore-errors clean install test report
```

Note that we add the `--ignore-errors` parameter so that reports still generate if tests fail.

## CI/CD Integration

To integrate with CI/CD pipelines, use:

```shell
/bin/bash $(git rev-parse --show-toplevel)/scripts/workflow/service-automation-tests.sh
```

This script expects the variables `ENVIRONMENT`, `WORKSPACE`, `TEST_TAG`, `TEST_TYPE`, `COMMIT_HASH` to be set if running locally.
These variables are set in the pipeline and passed through to the script.

- `TEST_TAG` is the tag used to identify the tests that should be run, e.g. `is-pipeline`
- `TEST_TYPE` identifies the type of Allure report to generate, e.g. `ui` or `feature`

To set these if wanting to run the service-automated-tests script locally use:

```shell
export WORKSPACE=dosis-xxx  # replacing dosis-xxx with the relevant workspace
export ENVIRONMENT=dev      # replacing dev with the relevant environment
export TEST_TAG=is-pipeline # replacing is-pipeline with the relevant tag
export TEST_TYPE=api        # replace with ui if want to run the playwright ui tests
export COMMIT_HASH=abc123   # replacing with actual 6-character commit hash
```

## Troubleshooting

- If reports are blank, ensure that the command to generate the report has been run in the same directory as the allure-results directory
- If you encounter issues with asdf tools, try `asdf reshim` to update the shims
- For Playwright issues, try `poetry run playwright install --with-deps` to install all system dependencies

## NOTE - TODO

The Feature: API DoS Service Search APIM has been defined with the tag manual as the supporting APIM proxy infrastructure is not yet available.

These tests can only be run from command line for the main workspace at current and with the api-name and proxy-name passed in.

Add a test tag to the feature file and then run the command below replacing "api-name" and "api proxy name" for the relevant data

```
poetry run pytest -m "test" --api-name=<api-name>  --proxy-name=<api proxy name> -p allure_pytest_bdd --alluredir=allure-results
```
