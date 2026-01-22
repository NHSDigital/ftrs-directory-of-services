"""
Lambda function to send CloudWatch alarm notifications to Slack.
Sends essential alert information: metric trigger, threshold, API, endpoint, period, and timestamp.
"""

import json
import logging
import os
import boto3
import urllib3
from typing import Any, Dict
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()
secrets_client = boto3.client("secretsmanager")


# API and endpoint mappings for metrics
METRIC_CONTEXT = {
    "Duration": {
        "api": "DoS Search API",
        "endpoint": "/Organization?{query}",
        "period": "5-minute evaluation window",
    },
    "ConcurrentExecutions": {
        "api": "DoS Search API",
        "endpoint": "/Organization?{query}",
        "period": "5-minute evaluation window",
    },
    "Throttles": {
        "api": "DoS Search API",
        "endpoint": "/Organization?{query}",
        "period": "5-minute evaluation window",
    },
    "Invocations": {
        "api": "DoS Search API",
        "endpoint": "/Organization?{query} & /health",
        "period": "5-minute evaluation window",
    },
    "Errors": {
        "api": "DoS Search API",
        "endpoint": "/Organization?{query}",
        "period": "5-minute evaluation window",
    },
}


def get_slack_webhook_url() -> str:
    """
    Retrieve Slack webhook URL from AWS Secrets Manager.

    Returns:
        str: The Slack webhook URL
    """
    secret_arn = os.environ.get("SLACK_WEBHOOK_SECRET_ARN")

    if not secret_arn:
        raise ValueError("SLACK_WEBHOOK_SECRET_ARN environment variable not set")

    try:
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        secret = response.get("SecretString", "")
        return secret.strip()
    except Exception as e:
        logger.error(f"Failed to retrieve Slack webhook URL from Secrets Manager: {str(e)}")
        raise


def flatten_dict(data: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
    """
    Flatten nested dictionary to single level.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Dict: Flattened dictionary
    """
    items = []

    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Convert lists to comma-separated strings
            items.append((new_key, ", ".join(str(item) for item in v)))
        else:
            items.append((new_key, v))

    return dict(items)


def parse_cloudwatch_alarm(message: str) -> Dict[str, Any]:
    """
    Parse CloudWatch alarm SNS message.

    Args:
        message: SNS message body

    Returns:
        Dict: Parsed alarm data
    """
    try:
        alarm_data = json.loads(message)
        return alarm_data
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse alarm message: {str(e)}")
        return {"raw_message": message}


def extract_lambda_name(alarm_name: str) -> str:
    """
    Extract Lambda function name from alarm name.

    Args:
        alarm_name: Full alarm name from CloudWatch

    Returns:
        str: Extracted Lambda function name
    """
    parts = alarm_name.split("-")
    if len(parts) >= 3:
        return "-".join(parts[:-2]) if "lambda" in alarm_name.lower() else alarm_name
    return alarm_name


def get_metric_context(metric_name: str) -> Dict[str, str]:
    """
    Get API endpoint and period context for a metric.

    Args:
        metric_name: CloudWatch metric name

    Returns:
        Dict: Context with API, endpoint, and period
    """
    context = METRIC_CONTEXT.get(metric_name, {})
    return {
        "api": context.get("api", "DoS Search API"),
        "endpoint": context.get("endpoint", "Unknown"),
        "period": context.get("period", "5-minute evaluation window"),
    }


def format_timestamp(timestamp_val: Any) -> str:
    """
    Format timestamp for display.

    Args:
        timestamp_val: Timestamp from CloudWatch (various formats)

    Returns:
        str: Formatted timestamp string (e.g., "21/01/2026 at 10:30am")
    """
    try:
        if isinstance(timestamp_val, (int, float)):
            dt = datetime.fromtimestamp(int(timestamp_val))
            return dt.strftime("%d/%m/%Y at %I:%M%p").lower()
        elif isinstance(timestamp_val, str):
            return timestamp_val
        else:
            return "Unknown"
    except (ValueError, TypeError):
        return "Unknown"


def build_slack_message(alarm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a Slack message with essential alert information.

    Includes:
    - Why the alert was triggered (metric and threshold)
    - API and endpoint it relates to
    - Alert period
    - Timestamp

    Args:
        alarm_data: Flattened alarm data from CloudWatch

    Returns:
        Dict: Slack message payload
    """
    # Extract key fields
    alarm_name = alarm_data.get("AlarmName", "Unknown Alarm")
    state_value = alarm_data.get("StateValue", "UNKNOWN")
    state_reason = alarm_data.get("StateReason", "No reason provided")
    trigger_metric = alarm_data.get("Trigger_MetricName", "Unknown")
    trigger_threshold = alarm_data.get("Trigger_Threshold", "N/A")
    trigger_statistic = alarm_data.get("Trigger_Statistic", "N/A")
    timestamp_val = alarm_data.get("StateUpdatedTimestamp", "Unknown")

    # Get context for this metric
    context = get_metric_context(trigger_metric)

    # Format timestamp
    timestamp = format_timestamp(timestamp_val)

    # Determine color and emoji based on state
    color_map = {
        "ALARM": "#FF0000",              # Red
        "OK": "#00AA00",                # Green
        "INSUFFICIENT_DATA": "#FFAA00"  # Orange
    }
    emoji_map = {
        "ALARM": "🚨",
        "OK": "✅",
        "INSUFFICIENT_DATA": "⚠️"
    }
    color = color_map.get(state_value, "#808080")
    emoji = emoji_map.get(state_value, "📊")

    # Extract lambda name for context
    lambda_name = extract_lambda_name(alarm_name)

    # Build Slack message
    slack_message = {
        "text": f"{emoji} {alarm_name} - {state_value}",
        "attachments": [
            {
                "color": color,
                "title": f"{emoji} {alarm_name}",
                "text": state_reason,
                "fields": [
                    {
                        "title": "Metric Triggered",
                        "value": f"{trigger_metric} ({trigger_statistic})",
                        "short": True
                    },
                    {
                        "title": "Threshold",
                        "value": str(trigger_threshold),
                        "short": True
                    },
                    {
                        "title": "API",
                        "value": context["api"],
                        "short": True
                    },
                    {
                        "title": "Endpoint",
                        "value": context["endpoint"],
                        "short": True
                    },
                    {
                        "title": "Alert Period",
                        "value": context["period"],
                        "short": False
                    },
                    {
                        "title": "Timestamp",
                        "value": timestamp,
                        "short": False
                    }
                ],
                "footer": f"Lambda: {lambda_name}",
                "mrkdwn_in": ["text"]
            }
        ]
    }

    return slack_message


def send_to_slack(webhook_url: str, message: Dict[str, Any]) -> bool:
    """
    Send message to Slack webhook.

    Args:
        webhook_url: Slack webhook URL
        message: Slack message payload

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        encoded_msg = json.dumps(message).encode("utf-8")
        resp = http.request(
            "POST",
            webhook_url,
            body=encoded_msg,
            headers={"Content-Type": "application/json"}
        )

        if resp.status == 200:
            logger.info("Successfully sent message to Slack")
            return True
        else:
            logger.error(f"Failed to send message to Slack: HTTP {resp.status}")
            logger.error(f"Response: {resp.data.decode('utf-8')}")
            return False
    except Exception as e:
        logger.error(f"Exception while sending to Slack: {str(e)}")
        return False


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function for processing CloudWatch alarms and sending to Slack.

    Args:
        event: SNS event from CloudWatch
        context: Lambda context

    Returns:
        Dict: Response with status
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract SNS message
        sns_message = event.get("Records", [{}])[0].get("Sns", {}).get("Message", "")

        if not sns_message:
            logger.error("No SNS message found in event")
            return {"statusCode": 400, "body": "No SNS message found"}

        # Parse CloudWatch alarm
        alarm_data = parse_cloudwatch_alarm(sns_message)

        # Flatten the alarm data
        flattened_data = flatten_dict(alarm_data)
        logger.info(f"Flattened alarm data: {json.dumps(flattened_data)}")

        # Build Slack message
        slack_message = build_slack_message(flattened_data)

        # Get Slack webhook URL
        webhook_url = get_slack_webhook_url()

        # Send to Slack
        success = send_to_slack(webhook_url, slack_message)

        if success:
            return {
                "statusCode": 200,
                "body": json.dumps("Message sent to Slack successfully")
            }
        else:
            return {
                "statusCode": 500,
                "body": json.dumps("Failed to send message to Slack")
            }

    except Exception as e:
        logger.error(f"Error processing alarm: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {str(e)}")
        }
