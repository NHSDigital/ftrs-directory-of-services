# Infra Test Automation Framework

## Overview

This is an Infra Test Automation Framework using pytest-bdd and Playwright for validating Google Custom Search API responses. It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```

├── infra_automation/
│   ├── tests/
│   │   ├── step_definitions/
│   │   │   ├── test_s3_bucket.py
├── features/
│   ├── test_s3_bucket.feature
│── utilities/
├── infra/
│   ├── s3_util.py
│── README.md
```

## Prerequisites

Ensure you have Python 3.12+ installed. You also need pip and virtualenv for managing dependencies.

## Installation
```
pip install pytest pytest-bdd boto3
```

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

Run all tests using:
```
ppytest -v -s --html=report.html --self-contained-html --tb=short --capture=sys
```
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
If HTML reports are blank, ensure you use --self-contained-html in pytest options.
