# Slack Notifier Service

A reusable service that sends formatted CloudWatch alarm notifications to Slack channels, providing real-time visibility into system health and performance issues.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview

This service acts as a bridge between AWS CloudWatch alarms and Slack, automatically processing alarm notifications from SNS topics and delivering them as rich, formatted messages to designated Slack channels. The service is designed to be reusable across multiple alarm types and services within the platform.

It provides essential alert information including:

- **Why** the alert was triggered (metric and threshold)
- **What** service/resource is affected
- **When** the alarm occurred
- **Where** to find more information (direct AWS console links)

## Features

### Core Functionality

- **Automatic Processing**: Triggered by SNS notifications from CloudWatch alarms
- **Rich Formatting**: Converts raw CloudWatch data into readable Slack messages with blocks and attachments
- **Severity Detection**: Automatically identifies warning vs critical alarms based on naming conventions
- **Multi-Alarm Support**: Processes multiple alarm notifications in a single invocation

### Message Content

- Metric name and statistical method (Average, Sum, etc.)
- Threshold values that triggered the alarm
- Evaluation period and duration
- Timestamp with Slack-native date formatting
- State change reason from CloudWatch
- Lambda function name and AWS region

### AWS Console Integration

- Direct link to CloudWatch alarm details
- Lambda function logs (CloudWatch Logs)
- Lambda function metrics dashboard

### Error Handling

- Graceful handling of malformed messages
- Detailed logging for troubleshooting
- Partial success reporting (processes valid records even if some fail)

## Architecture

```text
CloudWatch Alarm → SNS Topic → Lambda Function → Slack Webhook → Slack Channel
```

### Components

- **slack_alarm_handler.py**: Main Lambda handler that orchestrates the notification flow
- **functions/alarm_parser.py**: Parses and flattens CloudWatch alarm JSON messages
- **functions/slack_formatter.py**: Builds Slack message blocks with formatting and links
- **functions/aws_url_builder.py**: Generates AWS console URLs for alarms and resources
- **functions/slack_client.py**: Handles Slack webhook communication

## Prerequisites

- Python 3.12 or later
- Poetry for dependency management

## Configuration

### Environment Variables

The Lambda function expects the following environment variable:

- `SLACK_WEBHOOK_ALARMS_URL`: Name of the URL that that's used to send messages to Slack.

### CloudWatch Alarm Naming Convention

For proper severity detection, alarms should follow these naming patterns:

- `<service>-<metric>-warning`: For warning-level alarms (⚠️)
- `<service>-<metric>-critical`: For critical-level alarms (🚨)

Example: `dos-search-error-rate-critical`

## Usage

The service is triggered automatically when CloudWatch alarms publish to the configured SNS topic. It processes the alarm data and sends formatted notifications to Slack.

## Development

### Installation

Install dependencies using Poetry:

```bash
make install
```

Or manually:

```bash
poetry install
```

### Code Quality

Run linting with Ruff:

```bash
make lint
```

The project uses Ruff for linting with the following checks enabled:

- Pycodestyle (E, W)
- Pyflakes (F)
- Import sorting (I)
- Naming conventions (N)
- Security checks (S)
- And more (see pyproject.toml)

### Local Testing

Create a test event file (`test_event.json`) with sample SNS data:

```json
{
  "Records": [
    {
      "Sns": {
        "Message": "{\"AlarmName\":\"test-alarm-critical\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold exceeded\"}"
      }
    }
  ]
}
```

Test locally:

```bash
poetry run python -c "import json; from slack_alarm_handler import lambda_handler; lambda_handler(json.load(open('test_event.json')), None)"
```

## Testing

### Run All Tests

```bash
make test
```

### Run Specific Test Files

```bash
poetry run pytest tests/unit/test_alarm_parser.py -v
```

### Test Coverage

The project uses pytest-cov for coverage reporting:

```bash
poetry run pytest --cov=. --cov-report=html
```

View the HTML report at `htmlcov/index.html`

### Test Structure

- `tests/unit/test_alarm_parser.py`: Tests for CloudWatch message parsing
- `tests/unit/test_slack_formatter.py`: Tests for Slack message formatting
- `tests/unit/test_aws_url_builder.py`: Tests for AWS console URL generation
- `tests/unit/test_slack_client.py`: Tests for Slack webhook communication

## Deployment

### Build Artifacts

Build the Lambda deployment package:

```bash
make build
```

This creates:

- `slack_notifier-<version>-py3-none-any.whl`: Python wheel package
- `slack-notifier-dependencies-layer.zip`: Lambda layer with dependencies

### Build Dependency Layer

Create a Lambda layer with all runtime dependencies:

```bash
make build-dependency-layer
```

## Troubleshooting

### Common Issues

#### Slack Messages Not Appearing

- Check Lambda execution logs for errors
- Verify webhook URL is correctly configured
- Ensure SNS message format is valid

#### Malformed Messages

- Validate SNS message matches CloudWatch alarm structure
- Review `alarm_parser.py` logs for parsing errors
- Check JSON structure of the alarm message

#### Missing Information in Slack

- Ensure CloudWatch alarms include all required fields
- Check the flattened data structure in logs
- Verify alarm naming follows the severity convention

## License

Unless stated otherwise, the codebase is released under the MIT License.
