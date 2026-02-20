# Slack Notifier Service

Sends CloudWatch alarm notifications to Slack with formatted messages including metric details, thresholds, and AWS console links.

## Overview

Lambda function triggered by SNS that processes CloudWatch alarms and delivers formatted notifications to Slack channels.

## Components

- `functions/slack_alarm_handler.py`: Lambda handler
- `functions/alarm_parser.py`: Parses CloudWatch alarm messages
- `functions/slack_formatter.py`: Builds Slack message blocks
- `functions/aws_url_builder.py`: Generates AWS console URLs
- `functions/slack_client.py`: Slack webhook client

## Configuration

Set `SLACK_WEBHOOK_ALARMS_URL` environment variable with your Slack webhook URL.

Alarm naming convention for severity detection:

- `*-warning`: Warning alarms (⚠️)
- `*-critical`: Critical alarms (🚨)

## Development

```bash
make install  # Install dependencies
make lint     # Run linting
make lint-fix # Fix linting issues
make test     # Run tests
```

## Deployment

```bash
make build  # Build Lambda package and dependency layer
```
