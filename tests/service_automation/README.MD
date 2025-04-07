# Service Test Automation Framework

## Overview

This is an Service Test Automation Framework using pytest-bdd and Playwright for validating API Testing, AWS Infra Testing like Buckets etc and UI Testing. It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```
├── service_automation/
    ├── tests
    │   ├── features
    |   |   ├── is_api_features
    |   |   ├── is_infra_features
    │   ├── pages
    |   |   ├── ui_pages
    │   ├── step_definitions
    |   |   ├── is_api_steps
    |   |   ├── is_infra_steps
    |   |   ├── ui_steps
    │   ├── utilities
    |   |   ├── common
    |   |   ├── infra
    ├── README.MD
    ├── pytest.ini

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

Install allure to generate report
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

Change aws config file with values listed in Service Teams - Set up SSO for AWS confluence page. Also use Dos developer profile from your aws console for your CLI connection.

### Service Test Configuration

Make a copy of config_template.yaml and name it config.yaml, and update it with details as explained below:
```
project: "aws project name"
workspace: "workspace"
```

The workspace is defined as
```
workspace = default when running against the main branch
workspace = dr-xxx when running against task branch dr-xxx
```

### API Test Configuration

Update config.yaml with API details as explained below:
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

## Allure reports

There are 2 different libraries used for the different test types:
- allure-pytest
- allure-pytest-bdd

To ensure that the correct report is generated the report type needs to be passed at runtime
If generated in separate folders, the results from both report types can be combined and a single report generated if required

### allure-pytest

Generates a report based on the step definition file and will generate for all the tests

### allure-pytest

Generates a report based on the feature files and will only generate for these tests

## Running Feature File BDD Tests

To run the tests, save the report results to a folder called allure-results and then generate the report in the allure-reports folder
```
pytest -p allure_pytest --alluredir=allure-results
allure generate --single-file -c -o allure-reports allure-results
```
Run specific feature tests:
```
pytest tests/step_definitions/is_infra_steps/test_s3_bucket.py -p allure_pytest --alluredir=allure-results
```
Run specific tagged tests, for example @is-api:
```
pytest -m "is-api"  -p allure_pytest --alluredir=allure-results
```
To generate a single page report in the folder allure-report
```
allure generate --single-file -c -o allure-reports allure-results
```

## Running Playwright UI Tests

To run the tests, save the report results to a folder called allure-results and then generate the report in the allure-reports folder
```
pytest -p allure_pytest --alluredir=allure-results
allure generate --single-file -c -o allure-reports allure-results
```
Run specific feature tests:
```
pytest tests/step_definitions/ui_steps/test_ui_search.py  -p allure_pytest --alluredir=allure-results
```
Run specific tagged tests, for example @pytest.mark.ui:
```
pytest -m "ui"  -p allure_pytest --alluredir=allure-results
```
To generate a single page report in the folder allure-report
```
allure generate --single-file -c -o allure-reports allure-results
```

## Using the Variables Locally

The config file of the framework contains the variables that are required to be set when running locally.

If the branch has not been pushed and the dev pipeline successfully deployed the app then the script will fail as there will not be any infrastructure built that relates to the branch


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

This script expects the variables ENVIRONMENT, WORKSPACE, TEST_TAG, TEST_TYPE to be set if running locally. These variables are set in the pipeline and passed through to the script.
TEST_TAG is the tag used to identify the tests that should be run, for example is-pipeline
TEST_TYPE identifies the type of Allure report to generate
```
ui or feature
```

To set these if wanting to run the service-automated-tests script locally use:

```
export WORKSPACE=dosis-xxx (replacing dosis-xxx with the relevant workspace)
export ENVIRONMENT=dev
export TEST_TAG=is-pipeline (replacing is-pipeline with the relevant tag)
export TEST_TYPE=api (replace with ui if want to run the playwright ui tests)
```


## Troubleshooting
If reports are blank, ensure that the command to generate the report has been run in the same directory as the allure-results directory
