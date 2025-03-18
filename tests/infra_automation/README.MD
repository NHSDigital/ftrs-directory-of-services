# Infra Test Automation Framework

## Overview

This is an Infra Test Automation Framework using pytest-bdd and Playwright for validating AWS Infra Testing like Buckets etc. It follows the BDD (Behavior Driven Development) approach using Gherkin syntax.

## Project Structure

```

├── infra_automation/
│   ├── tests/
│   │   ├── step_definitions/
│   │   │   ├── test_s3_bucket.py
        ├── features/
        │   ├── test_s3_bucket.feature
    │── README.md
│── utilities/
├── infra/
│   ├── s3_util.py

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

### Configuration

Make a copy of config_template.yaml and name it config.yaml, and update it with API details as explained below:
```
gp-search-bucket: "Bucket Name which need to locate"
project: "aws project name"
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
pytest -v -s --html=report.html --self-contained-html --tb=short --capture=sys
```
Run specific feature tests:

```
pytest tests/step_definitions/test_s3_bucket.py --html=reports/report.html --self-contained-html
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
export ENVIRONMENT=dev
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

