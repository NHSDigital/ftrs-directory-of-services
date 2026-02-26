"""Fetch CloudWatch alarm tags."""

import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_alarm_tags(alarm_arn: str) -> dict[str, str]:
    """Fetch tags for a CloudWatch alarm.

    Args:
        alarm_arn: ARN of the CloudWatch alarm

    Returns:
        dict: Tags with api_path and service, defaults to N/A and Unknown if not found
    """
    if not alarm_arn:
        logger.warning("No alarm ARN provided")
        return {"api_path": "N/A", "service": "Unknown"}

    try:
        cloudwatch = boto3.client("cloudwatch")
        response = cloudwatch.list_tags_for_resource(ResourceARN=alarm_arn)

        tags = {tag["Key"]: tag["Value"] for tag in response.get("Tags", [])}

        return {
            "api_path": tags.get("api_path", "N/A"),
            "service": tags.get("service", "Unknown"),
        }

    except ClientError:
        logger.exception("Failed to fetch alarm tags")
        return {"api_path": "N/A", "service": "Unknown"}
