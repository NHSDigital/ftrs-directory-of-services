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
        │   │── report_YYYYMMDD_HHMM.html # Stores test reports
        │── README.md                    # Project documentation
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

Install Playwright browsers (required for API testing via Playwright)

playwright install
```

### Configuration

Modify config.yaml to update API details:

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

    Run all tests using:

        pytest --bdd --html=reports/report.html --self-contained-html

Run specific feature tests:

```
pytest tests/step_definitions/test_api_google_search.py --html=reports/report.html --self-contained-html
```

## Generating Reports

After execution, open the generated report:

```
open reports/report.html  # macOS/Linux
start reports\report.html  # Windows
```

## CI/CD Integration

To integrate with CI/CD pipelines, use:

```
pytest -v -s --html=report.html --self-contained-html --tb=short --capture=sys;

pytest --html=reports/report_$(date +%Y%m%d_%H%M%S).html --self-contained-html
```

This ensures unique report generation per run.

## Troubleshooting

If ModuleNotFoundError: No module named 'playwright' occurs, ensure Playwright is installed using:

```
pip install playwright
playwright install

If HTML reports are blank, ensure you use --self-contained-html in pytest options.
