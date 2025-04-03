# Service Test Automation Framework

## Overview

This is an Service Test Automation Framework using pytest-bdd and Playwright for validating API Testing, AWS Infra Testing like Buckets etc and UI Testing. It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```
├── service_automation/
    ├── tests
    │   ├── features
    |   |   ├── is_api_features
    │   |   |    └── test_api.feature
    |   |   ├── is_infra_features
    │   |   |    └── test_s3_bucket.feature
    │   ├── pages
    |   |   ├── ui_pages
    │   |   |     └── search.py
    │   ├── step_definitions
    |   |   ├── is_api_steps
    │   │   |     └──test_api.py
    |   |   ├── is_infra_steps
    │   │   |     └── test_s3_bucket.py
        |   ├── ui_steps
    │   │   |     └── test_ui_search.py
    │   ├── utilities
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
cd service_automation
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

install allure to generate report
```
brew install allure
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

### Service Test Configuration

Make a copy of config_template.yaml and name it config.yaml, and update it with API details as explained below:
```
project: "aws project name"
```

### API Test Configuration

Make a copy of config-template.yaml and name it config.yaml, and update it with API details as explained below:
```
base_url: "https://www.googleapis.com/customsearch/v1"
api_key: "YOUR_GOOGLE_API_KEY"
search_engine_id: "YOUR_SEARCH_ENGINE_ID"
```

## Create a virtual environment & activate it (optional)

```
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
```

## Running Tests

To run the tests and save the report results to a folder called allure-results
```
pytest
allure generate --single-file -c -o allure-reports allure-results
```
Run specific feature tests:
```
pytest tests/step_definitions/is_infra_steps/test_s3_bucket.py
```
Run specific tagged tests, for example @is-api:
```
pytest -m "is-api"
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

## Generating Reports

To generate a single page report in the folder allure-report
```
allure generate --single-file -c -o allure-reports allure-results
```

## CI/CD Integration

To integrate with CI/CD pipelines, use:

```
/bin/bash ./scripts/workflow/service-automated-tests.sh
```
This script expects the variables ENV, WORKSPACE, TEST_TAG to be set if running locally.
TEST_TAG is the tag used to identify the tests that should be run, for example is-pipeline


## Troubleshooting
If reports are blank, ensure that the command to generate the report has been run in the same directory as the allure-results directory
