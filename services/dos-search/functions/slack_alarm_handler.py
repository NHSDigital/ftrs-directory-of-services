"""
Lambda function to send CloudWatch alarm notifications to Slack.
Sends essential alert information: metric trigger, threshold, API, endpoint, period, and timestamp.
"""

import json
import logging
from typing import Any, Dict

from functions.slack_notifier.alarm_parser import flatten_dict, parse_cloudwatch_alarm
from functions.slack_notifier.slack_client import get_slack_webhook_url, send_to_slack
from functions.slack_notifier.slack_formatter import build_slack_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
