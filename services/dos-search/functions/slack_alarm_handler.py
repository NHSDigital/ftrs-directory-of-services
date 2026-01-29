"""
Lambda function to send CloudWatch alarm notifications to Slack.
Sends essential alert information: metric trigger, threshold, API, endpoint, period, and timestamp.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict
from urllib.parse import quote

import urllib3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

http = urllib3.PoolManager()

# Constants
DOS_SEARCH_API = "DoS Search API"
ENDPOINT_TEMPLATE = "/Organization?{query}"
SUCCESS_STATUS_CODE = 200

# API and endpoint mappings for metrics
METRIC_CONTEXT = {
    "Duration": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
    },
    "ConcurrentExecutions": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
    },
    "Throttles": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
    },
    "Invocations": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE + " & /health",
    },
    "Errors": {
        "api": DOS_SEARCH_API,
        "endpoint": ENDPOINT_TEMPLATE,
    },
}

# State formatting for Slack messages
EMOJI_MAP = {"ALARM": "🚨", "OK": "✅", "INSUFFICIENT_DATA": "⚠️"}


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
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(
                        flatten_dict(item, f"{new_key}{sep}{i}", sep=sep).items()
                    )
                else:
                    items.append((f"{new_key}{sep}{i}", item))
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


def get_metric_context(metric_name: str) -> Dict[str, str]:
    """
    Get API endpoint context for a metric.

    Args:
        metric_name: CloudWatch metric name

    Returns:
        Dict: Context with API and endpoint
    """
    context = METRIC_CONTEXT.get(metric_name, {})
    return {
        "api": context.get("api", DOS_SEARCH_API),
        "endpoint": context.get("endpoint", "Unknown"),
    }


def format_timestamp(timestamp_str: str) -> str:
    """
    Format timestamp for Slack date formatting.

    Args:
        timestamp_str: ISO timestamp string from CloudWatch

    Returns:
        str: Slack-formatted date string
    """
    if not timestamp_str:
        return "Unknown"

    try:
        # Handle CloudWatch timestamp format: "2026-01-29T17:47:08.980+0000"
        timestamp_str = timestamp_str.replace("+0000", "+00:00")
        dt = datetime.fromisoformat(timestamp_str)
        unix_ts = int(dt.timestamp())
    except (ValueError, AttributeError):
        return timestamp_str
    else:
        return f"<!date^{unix_ts}^{{date_short_pretty}} at {{time}}|{timestamp_str}>"


def build_cloudwatch_url(alarm_name: str, region: str = "eu-west-2") -> str:
    """
    Build CloudWatch console URL for the alarm.

    Args:
        alarm_name: CloudWatch alarm name
        region: AWS region

    Returns:
        str: CloudWatch console URL
    """
    encoded_name = quote(alarm_name, safe="")
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
    encoded_name = quote(lambda_name, safe="")
    return f"https://{region}.console.aws.amazon.com/cloudwatch/home?region={region}#logsV2:log-groups/log-group/$252Faws$252Flambda$252F{encoded_name}"


def build_lambda_metrics_url(lambda_name: str, region: str = "eu-west-2") -> str:
    """
    Build Lambda metrics URL.

    Args:
        lambda_name: Lambda function name
        region: AWS region

    Returns:
        str: Lambda metrics console URL
    """
    encoded_name = quote(lambda_name, safe="")
    return f"https://{region}.console.aws.amazon.com/lambda/home?region={region}#/functions/{encoded_name}?tab=monitoring"


def extract_region_code(alarm_arn: str) -> str:
    """
    Extract AWS region code from alarm ARN.

    Args:
        alarm_arn: CloudWatch alarm ARN

    Returns:
        str: AWS region code (e.g., 'eu-west-2')
    """
    arn_region_index = 3
    default_region = "eu-west-2"
    try:
        parts = alarm_arn.split(":")
        return (
            parts[arn_region_index] if len(parts) > arn_region_index else default_region
        )
    except (IndexError, AttributeError):
        return default_region


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
    # Extract key fields from flattened structure
    alarm_name = alarm_data.get("alarmName", "Unknown Alarm")
    alarm_arn = alarm_data.get("historyData_publishedMessage_default_AlarmArn", "")
    state_value = alarm_data.get(
        "historyData_publishedMessage_default_NewStateValue", "UNKNOWN"
    )
    state_reason = alarm_data.get(
        "historyData_publishedMessage_default_NewStateReason", "No reason provided"
    )
    trigger_threshold = alarm_data.get(
        "historyData_publishedMessage_default_Trigger_Threshold", "N/A"
    )
    trigger_statistic = alarm_data.get(
        "historyData_publishedMessage_default_Trigger_Statistic", "N/A"
    )
    trigger_metric = alarm_data.get(
        "historyData_publishedMessage_default_Trigger_MetricName", "Unknown"
    )
    trigger_period = alarm_data.get(
        "historyData_publishedMessage_default_Trigger_Period", 30
    )
    trigger_eval_periods = alarm_data.get(
        "historyData_publishedMessage_default_Trigger_EvaluationPeriods", 1
    )
    timestamp_val = alarm_data.get(
        "historyData_publishedMessage_default_StateChangeTime"
    )
    lambda_name = alarm_data.get(
        "historyData_publishedMessage_default_Trigger_Dimensions_0_value",
        "Unknown Lambda",
    )
    aws_region = extract_region_code(alarm_arn)

    logger.info(f"Extracted state_value: {state_value}")

    # Get context for this metric
    context = get_metric_context(trigger_metric)

    # Build period description from trigger data
    period_desc = f"{trigger_period}s evaluation over {trigger_eval_periods} period(s)"

    # Format timestamp
    timestamp = format_timestamp(timestamp_val)

    # Determine emoji based on state (handle both uppercase and as-is)
    emoji = EMOJI_MAP.get(
        state_value.upper() if isinstance(state_value, str) else state_value, "📊"
    )

    # Build CloudWatch console URL
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
                    {"type": "mrkdwn", "text": f"*Endpoint:*\n`{context['endpoint']}`"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Period:*\n{period_desc}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{timestamp}"},
                ],
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Reason:*\n{state_reason}"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{cloudwatch_url}|🔗 View Alarm> | <{lambda_logs_url}|📋 Lambda Logs> | <{lambda_metrics_url}|📊 Lambda Metrics>",
                },
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
