"""Format CloudWatch alarm data into Slack message blocks."""

import logging
from datetime import datetime
from typing import Any, Dict

from functions.slack_notifier.aws_url_builder import (
    build_cloudwatch_url,
    build_lambda_logs_url,
    build_lambda_metrics_url,
    extract_region_code,
)

logger = logging.getLogger(__name__)

EMOJI_MAP = {"ALARM": "🚨", "OK": "✅", "INSUFFICIENT_DATA": "⚠️"}
SEVERITY_EMOJI_MAP = {"warning": "⚠️", "critical": "🚨"}


def get_severity_from_alarm_name(alarm_name: str) -> str:
    """Extract severity from alarm name.

    Args:
        alarm_name: CloudWatch alarm name

    Returns:
        str: Severity level ('warning', 'critical', or 'unknown')
    """
    alarm_lower = alarm_name.lower()
    if "-warning" in alarm_lower:
        return "warning"
    elif "-critical" in alarm_lower:
        return "critical"
    return "unknown"


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
        timestamp_str = timestamp_str.replace("+0000", "+00:00")
        dt = datetime.fromisoformat(timestamp_str)
        unix_ts = int(dt.timestamp())
    except (ValueError, AttributeError):
        return timestamp_str
    else:
        return f"<!date^{unix_ts}^{{date_short_pretty}} at {{time}}|{timestamp_str}>"


def build_slack_message(alarm_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a Slack message with essential alert information using blocks and attachments.

    Includes:
    - Why the alert was triggered (metric and threshold)
    - Alert period
    - Timestamp

    Args:
        alarm_data: Flattened alarm data from CloudWatch

    Returns:
        Dict: Slack message payload with blocks and attachments
    """
    logger.info(f"Available flattened keys: {list(alarm_data.keys())}")

    # Extract key fields from flattened structure
    alarm_name = alarm_data.get("AlarmName", "Unknown Alarm")
    alarm_arn = alarm_data.get("AlarmArn", "")
    state_value = alarm_data.get("NewStateValue", "UNKNOWN")
    state_reason = alarm_data.get("NewStateReason", "No reason provided")
    trigger_threshold = alarm_data.get("Trigger_Threshold", "N/A")
    trigger_statistic = alarm_data.get("Trigger_Statistic", "N/A")
    trigger_metric = alarm_data.get("Trigger_MetricName", "Unknown")
    trigger_period = alarm_data.get("Trigger_Period", 30)
    trigger_eval_periods = alarm_data.get("Trigger_EvaluationPeriods", 1)
    timestamp_val = alarm_data.get("StateChangeTime")
    lambda_name = alarm_data.get("Trigger_Dimensions_0_value", "Unknown Lambda")
    region_display = alarm_data.get("Region", "EU (London)")
    aws_region = extract_region_code(alarm_arn)

    logger.info(
        f"Extracted values - state: {state_value}, metric: {trigger_metric}, threshold: {trigger_threshold}, lambda: {lambda_name}, timestamp: {timestamp_val}, reason: {state_reason}"
    )

    period_desc = f"{trigger_period}s evaluation over {trigger_eval_periods} period(s)"
    timestamp = format_timestamp(timestamp_val)

    # Determine emoji and display state based on severity
    if state_value == "ALARM":
        severity = get_severity_from_alarm_name(alarm_name)
        emoji = SEVERITY_EMOJI_MAP.get(severity, "🚨")
        display_state = severity.upper() if severity != "unknown" else state_value
    else:
        emoji = EMOJI_MAP.get(
            state_value.upper() if isinstance(state_value, str) else state_value, "📊"
        )
        display_state = state_value

    cloudwatch_url = build_cloudwatch_url(alarm_name, aws_region)
    lambda_logs_url = build_lambda_logs_url(lambda_name, aws_region)
    lambda_metrics_url = build_lambda_metrics_url(lambda_name, aws_region)

    api_path = "/Organization"  # Needs to be fetched from relevant data source
    api_service = "DoS Search"  # Needs to be fetched from relevant data source

    return {
        "text": f"{emoji} CloudWatch Alarm: {display_state}",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {display_state}: {alarm_name}",
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
                    {"type": "mrkdwn", "text": f"*API Path:*\n`{api_path}`"},
                    {"type": "mrkdwn", "text": f"*Service:*\n`{api_service}`"},
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
                "text": {"type": "mrkdwn", "text": f"*Reason:*\n*{state_reason}*"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{cloudwatch_url}| 🔗 View Alarm> | <{lambda_logs_url}| 📋 Lambda Logs> | <{lambda_metrics_url}| 📊 Lambda Metrics>",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Lambda: {lambda_name} | Region: {region_display}",
                    }
                ],
            },
        ],
    }
