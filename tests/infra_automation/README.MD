# Infra Test Automation Framework

## Overview

This is an Infra Test Automation Framework using pytest-bdd and Playwright for validating AWS Infra Testing like Buckets etc. It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```
├── infra_automation/
    ├── tests
    │   ├── features
    │   │   └── test_s3_bucket.feature
    │   ├── step_definitions
    │   │   └── test_s3_bucket.py
    │   ├── config.py
    │   ├── conftest.py
    │   └── report.html
    ├── README.MD
    ├── pytest.ini
    └── report.html

```

## Prerequisites

Ensure you have Python 3.12+ installed. You also need pip and virtualenv for managing dependencies.

### Clone the repository

```
git clone https://github.com/NHSDigital/ftrs-directory-of-services.git
cd tests
cd infra_automation
```

### Install dependencies

```
pip install -r requirements.txt
```
Install Playwright browsers (required for API testing via Playwright)

```
playwright install
```

AWS CLI Not Found
```
brew install awscli  # macOS
sudo apt install awscli  # Linux
```

### aws Configuration
Make sure your AWS CLI is configured and authenticated:
```
aws configure
aws sts get-caller-identity
```
You'll be prompted to enter:
```
AWS Access Key ID:
AWS Secret Access Key:
Default region (e.g., us-east-1, us-west-2):
Output format (json, table, text – default is json):
Alternatively, configure manually by editing these files:
```

```
Linux/macOS: ~/.aws/credentials and ~/.aws/config
Windows: C:\Users\USERNAME\.aws\credentials and C:\Users\USERNAME\.aws\config
```

change aws config file with values listed in Service Teams - Set up SSO for AWS confluence page. Also use Dos developer profile from your aws console for your CLI connection.

### Configuration

Make a copy of config_template.yaml and name it config.yaml, and update it with API details as explained below:
```
bucket_type: "Bucket Name which need to locate"
project: "aws project name"
```

## Create a virtual environment & activate it (optional)

```
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

## Running Tests

Run specific feature tests:

```
pytest tests/step_definitions/test_s3_bucket.py
```
To run the tests and save the report results to a folder called allure-results
```
pytest
allure generate --single-file -c -o allure-reports allure-results
```
To generate a single page report in the folder allure-report
```
allure generate --single-file -c -o allure-reports allure-results
```

## Using the Variables Locally

The pipeline script will define the workspace based on the branch name. If the branch has not been pushed and the dev pipeline successfully deployed the app then the script will fail as they will not be any infrastructure

```
workspace  = default when running against the main branch
workspace = dr-xxx when running against task branch dr-xxx
```

Project and Service-name should be set in the config file of the framework

Set environment variables that are derived in the pipeline
```
export WORKSPACE=dr-999  (where dr-999 is the branch name)
export ENV=dev
```
set PYTHONPATH to run test from tests folder from infra project and access utilities
```
export PYTHONPATH=$(pwd)../../../
```

## Generating Reports

To generate a single page report in the folder allure-report
```
allure generate --single-file -c -o allure-reports allure-results
```

## CI/CD Integration

To integrate with CI/CD pipelines, use:

```
pytest -p allure_pytest_bdd --alluredir=allure-results
```

This ensures unique report generation per run.

## Troubleshooting
If HTML reports are blank, ensure you use --self-contained-html in pytest options.
