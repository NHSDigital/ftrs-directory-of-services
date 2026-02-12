"""
Lambda function to send CloudWatch alarm notifications to Slack.
Sends essential alert information: metric trigger, threshold, API, endpoint, period, and timestamp.
"""

import json
import logging
from typing import Any

from functions.alarm_parser import flatten_dict, parse_cloudwatch_alarm
from functions.slack_client import get_slack_webhook_url, send_to_slack
from functions.slack_formatter import build_slack_message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: object) -> dict[str, Any]:
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
        records = event.get("Records", [])
        if not records:
            logger.error("No records found in event")
            return {"statusCode": 400, "body": "No records found in event"}

        webhook_url = get_slack_webhook_url()
        processed = 0
        failed = 0

        for record in records:
            sns_message = record.get("Sns", {}).get("Message", "")

            if not sns_message:
                logger.warning("Skipping record with no SNS message")
                continue

            try:
                alarm_data = parse_cloudwatch_alarm(sns_message)
                flattened_data = flatten_dict(alarm_data)
                logger.info("Flattened alarm data: %s", json.dumps(flattened_data))

                slack_message = build_slack_message(flattened_data)

                if send_to_slack(webhook_url, slack_message):
                    processed += 1
                else:
                    failed += 1
                    logger.error("Failed to send alarm to Slack")

            except Exception as e:
                failed += 1
                logger.error("Error processing record: %s", str(e), exc_info=True)

        if failed > 0:
            logger.error(
                f"Failed to process {failed} of {processed + failed} record(s)"
            )

        return {
            "statusCode": 200,
            "body": json.dumps(f"Processed {processed} record(s), failed {failed}"),
        }

    except Exception as e:
        logger.error("Error processing alarm: %s", str(e), exc_info=True)
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
