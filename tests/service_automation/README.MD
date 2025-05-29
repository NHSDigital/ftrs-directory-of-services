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

Make a copy of config_template.yaml and name it config.yaml, and update it with details as explained below:

```yaml
project: "aws project name"
workspace: "workspace"
```

The workspace is defined as

```plain
workspace = default when running against the main branch
workspace = dr-xxx when running against task branch dr-xxx
```

### API Test Configuration

Update config.yaml with API details as explained below:

```yaml
base_url: "https://www.googleapis.com/customsearch/v1"
api_key: "YOUR_GOOGLE_API_KEY"
search_engine_id: "YOUR_SEARCH_ENGINE_ID"
```

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

## Using the Variables Locally

The config file of the framework contains the variables that are required to be set when running locally.

If the branch has not been pushed and the dev pipeline successfully deployed the app then the script will fail as there will not be any infrastructure built that relates to the branch.

## CI/CD Integration

To integrate with CI/CD pipelines, use:

```shell
/bin/bash $(git rev-parse --show-toplevel)/scripts/workflow/service-automated-tests.sh
```

This script expects the variables ENVIRONMENT, WORKSPACE, TEST_TAG, TEST_TYPE to be set if running locally. These variables are set in the pipeline and passed through to the script.
TEST_TAG is the tag used to identify the tests that should be run, for example is-pipeline
TEST_TYPE identifies the type of Allure report to generate
```
ui or feature
```

To set these if wanting to run the service-automated-tests script locally use:

```shell
export WORKSPACE=dosis-xxx (replacing dosis-xxx with the relevant workspace)
export ENVIRONMENT=dev
export TEST_TAG=is-pipeline (replacing is-pipeline with the relevant tag)
export TEST_TYPE=api (replace with ui if want to run the playwright ui tests)
```

## Troubleshooting

- If reports are blank, ensure that the command to generate the report has been run in the same directory as the allure-results directory
- If you encounter issues with asdf tools, try `asdf reshim` to update the shims
- For Playwright issues, try `poetry run playwright install --with-deps` to install all system dependencies
