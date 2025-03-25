# API Test Automation Framework

## Overview

This is an API Test Automation Framework using pytest-bdd and Playwright for validating Google Custom Search API responses. It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```
api_automation/
    │── tests/
    │   │── features/                # BDD feature files
    │   │   │── test_api_google_search.feature
    │   │── step_definitions/        # Step definitions for BDD tests
    │   │   │── test_api_google_search.py
    │   │── config.py                # Python config loader
    │   │── config.yaml              # YAML configuration file
    │   │── conftest.py              # Pytest fixtures and setup
    │── report_YYYYMMDD_HHMM.html # Stores test reports
    │── README.MD                    # Project documentation
```

## Prerequisites

Ensure you have Python 3.9+ installed. You also need pip and virtualenv for managing dependencies.

## Installation

### Clone the repository

```
git clone https://github.com/NHSDigital/ftrs-directory-of-services.git
cd tests
cd api_automation
```

### Install dependencies

```
pip install -r requirements.txt
```
Install Playwright browsers (required for API testing via Playwright)

```
playwright install
```

### Configuration

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

```
pytest tests/step_definitions/test_s3_bucket.py -p allure_pytest_bdd --alluredir=allure-results
```
To run the tests and save the report results to a folder called allure-results
```
pytest -p allure_pytest_bdd --alluredir=allure-results
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

If ModuleNotFoundError: No module named 'playwright' occurs, ensure Playwright is installed using:

```
pip install playwright
playwright install
```
If HTML reports are blank, ensure you use --self-contained-html in pytest options.
