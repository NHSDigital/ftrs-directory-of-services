# Slack Notification Lambda

This Lambda function processes CloudWatch alarm notifications and sends flattened JSON to Slack.

## Purpose

- Receives SNS notifications from CloudWatch alarms
- Flattens nested JSON structure to ensure Slack compatibility
- Formats alarm data into a readable Slack message
- Sends alerts to a configured Slack workspace

## Features

- **JSON Flattening**: Converts nested JSON to single-level key-value pairs
- **Secure Webhook Storage**: Slack webhook URL stored in AWS Secrets Manager
- **Color-coded Alerts**: Different colors for ALARM, OK, and INSUFFICIENT_DATA states
- **Field Limiting**: Truncates long values and limits fields to prevent Slack limits
- **Error Handling**: Comprehensive logging and error handling

## Environment Variables

- `SLACK_WEBHOOK_SECRET_ARN`: ARN of the Secrets Manager secret containing the Slack webhook URL
- `ENVIRONMENT`: Current environment (dev, test, prod, etc.)

## Deployment

The Lambda function is deployed via Terraform in `slack_notifications.tf`.

### Prerequisites

1. Create a Slack App and generate an Incoming Webhook URL
2. Store the webhook URL in AWS Secrets Manager
3. Update the Terraform variables with the secret ARN

## Testing

To test locally:

```python
import json
from index import flatten_dict, build_slack_message

# Test flattening
nested_data = {
    "AlarmName": "test-alarm",
    "StateValue": "ALARM",
    "Trigger": {
        "MetricName": "Errors",
        "Threshold": 5
    }
}

flattened = flatten_dict(nested_data)
print(json.dumps(flattened, indent=2))
```

## Slack Webhook Setup

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Enable "Incoming Webhooks"
4. Add New Webhook to Workspace
5. Select target channel
6. Copy the webhook URL
7. Store in Secrets Manager
