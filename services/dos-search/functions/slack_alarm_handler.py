"""
Lambda function to send CloudWatch alarm notifications to Slack.
Sends essential alert information: metric trigger, threshold, API, endpoint, period, and timestamp.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import quote

import urllib3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()

# Constants
DOS_SEARCH_API = "DoS Search API"
ENDPOINT_TEMPLATE = "/Organization?{query}"
PERIOD = "5-minute evaluation window"
MIN_ALARM_NAME_PARTS = 3
SUCCESS_STATUS_CODE = 200

# API and endpoint mappings for metrics
METRIC_CONTEXT = {
    "Duration": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
        "period": PERIOD,
    },
    "ConcurrentExecutions": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
        "period": PERIOD,
    },
    "Throttles": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
        "period": PERIOD,
    },
    "Invocations": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE + " & /health",
        "period": PERIOD,
    },
    "Errors": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
        "period": PERIOD,
    },
}

# State formatting for Slack messages
EMOJI_MAP = {"ALARM": "🚨", "OK": "✅", "INSUFFICIENT_DATA": "⚠️"}
COLOR_MAP = {"ALARM": "danger", "OK": "good", "INSUFFICIENT_DATA": "warning"}
ALERT_GROUP_ID = "S09D388PZ7H"


def get_slack_webhook_url() -> str:
    """
    Retrieve Slack webhook URL from environment variable.

    Returns:
        str: The Slack webhook URL

    Raises:
        ValueError: If SLACK_WEBHOOK_URL environment variable is not set
    """
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")

    if webhook_url:
        return webhook_url.strip()
    msg = "SLACK_WEBHOOK_URL environment variable not set"
    raise ValueError(msg)


def flatten_dict(
    data: Dict[str, Any], parent_key: str = "", sep: str = "_"
) -> Dict[str, Any]:
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
        return json.loads(message)
    except json.JSONDecodeError:
        logger.exception("Failed to parse alarm message")
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
    if len(parts) >= MIN_ALARM_NAME_PARTS and "lambda" in alarm_name.lower():
        return "-".join(parts[:-2])
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
        "api": context.get("api", DOS_SEARCH_API),
        "endpoint": context.get("endpoint", "Unknown"),
        "period": context.get("period", "5-minute evaluation window"),
    }


def format_timestamp(timestamp_val: int | float | str) -> str:
    """
    Format timestamp for Slack date formatting.

    Args:
        timestamp_val: Timestamp from CloudWatch (various formats)

    Returns:
        str: Slack-formatted date string or fallback
    """
    try:
        if isinstance(timestamp_val, (int, float)):
            ts = int(timestamp_val)
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            fallback = dt.strftime("%B %d, %Y at %I:%M%p %Z")
            return f"<!date^{ts}^{{date_short_pretty}} at {{time}}|{fallback}>"
        elif isinstance(timestamp_val, str):
            return timestamp_val
        else:
            return "Unknown"
    except (ValueError, TypeError):
        return "Unknown"


def build_cloudwatch_url(alarm_name: str, region: str = "eu-west-2") -> str:
    """
    Build CloudWatch console URL for the alarm.

    Args:
        alarm_name: CloudWatch alarm name
        region: AWS region

    Returns:
        str: CloudWatch console URL
    """
    encoded_name = quote(alarm_name)
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#alarmsV2:alarm/{encoded_name}"


def build_lambda_logs_url(lambda_name: str, region: str = "eu-west-2") -> str:
    """
    Build CloudWatch Logs URL for Lambda function.

    Args:
        lambda_name: Lambda function name
        region: AWS region

    Returns:
        str: CloudWatch Logs console URL
    """
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/$252Faws$252Flambda$252F{lambda_name}"


def build_lambda_metrics_url(lambda_name: str, region: str = "eu-west-2") -> str:
    """
    Build Lambda metrics URL.

    Args:
        lambda_name: Lambda function name
        region: AWS region

    Returns:
        str: Lambda metrics console URL
    """
    return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{lambda_name}?tab=monitoring"


def build_slack_message(alarm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a Slack message with essential alert information using blocks and attachments.

    Includes:
    - Why the alert was triggered (metric and threshold)
    - API and endpoint it relates to
    - Alert period
    - Timestamp

    Args:
        alarm_data: Flattened alarm data from CloudWatch

    Returns:
        Dict: Slack message payload with blocks and attachments
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

    # Determine emoji based on state
    emoji = EMOJI_MAP.get(state_value, "📊")

    # Extract lambda name for context
    lambda_name = extract_lambda_name(alarm_name)

    # Build CloudWatch console URL
    aws_region = alarm_data.get("Region", "eu-west-2")
    cloudwatch_url = build_cloudwatch_url(alarm_name, aws_region)

    # Build action buttons
    lambda_logs_url = build_lambda_logs_url(lambda_name, aws_region)
    lambda_metrics_url = build_lambda_metrics_url(lambda_name, aws_region)

    return {
        "text": f"{emoji} CloudWatch Alarm: {state_value}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {state_value}: {alarm_name}",
                },
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Metric:*\n{trigger_metric} ({trigger_statistic})",
                    },
                    {"type": "mrkdwn", "text": f"*Threshold:*\n{trigger_threshold}"},
                    {"type": "mrkdwn", "text": f"*API:*\n{context['api']}"},
                    {"type": "mrkdwn", "text": f"*Endpoint:*\n{context['endpoint']}"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Period:*\n{context['period']}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Reason:*\n{state_reason}"},
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Alarm"},
                        "url": cloudwatch_url,
                        "style": "danger" if state_value == "ALARM" else "primary",
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Lambda Logs"},
                        "url": lambda_logs_url,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Lambda Metrics"},
                        "url": lambda_metrics_url,
                    },
                ],
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Lambda: {lambda_name} | Region: {aws_region}",
                    }
                ],
            },
        ],
    }


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
        logger.info("Sending to Slack: %s", json.dumps(message, indent=2))
        resp = http.request(
            "POST",
            webhook_url,
            body=encoded_msg,
            headers={"Content-Type": "application/json"},
        )

        if resp.status == SUCCESS_STATUS_CODE:
            logger.info("Successfully sent message to Slack")
            return True
        else:
            logger.error("Failed to send message to Slack: HTTP %s", resp.status)
            logger.error("Response: %s", resp.data.decode("utf-8"))
            return False
    except Exception:
        logger.exception("Exception while sending to Slack")
        return False


def lambda_handler(event: Dict[str, Any], context: object) -> Dict[str, Any]:
    """
    Lambda handler function for processing CloudWatch alarms and sending to Slack.

    Args:
        event: SNS event from CloudWatch
        context: Lambda context

    Returns:
        Dict: Response with status
    """
    logger.info("Received event: %s", json.dumps(event))

    try:
        # Extract SNS message
        records = event.get("Records", [])
        if not records:
            logger.error("No records found in event")
            return {"statusCode": 400, "body": "No records found in event"}

        sns_message = records[0].get("Sns", {}).get("Message", "")

        if not sns_message:
            logger.error("No SNS message found in event")
            return {"statusCode": 400, "body": "No SNS message found"}

        # Parse CloudWatch alarm
        alarm_data = parse_cloudwatch_alarm(sns_message)

        # Flatten the alarm data
        flattened_data = flatten_dict(alarm_data)
        logger.info("Flattened alarm data: %s", json.dumps(flattened_data))

        # Build Slack message
        slack_message = build_slack_message(flattened_data)

        # Get Slack webhook URL
        webhook_url = get_slack_webhook_url()

        # Send to Slack
        success = send_to_slack(webhook_url, slack_message)

        if success:
            return {
                "statusCode": 200,
                "body": json.dumps("Message sent to Slack successfully"),
            }
        return {
            "statusCode": 500,
            "body": json.dumps("Failed to send message to Slack"),
        }

    except Exception as e:
        logger.error("Error processing alarm: %s", str(e), exc_info=True)
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
