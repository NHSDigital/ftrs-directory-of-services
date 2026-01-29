"""Slack webhook client for sending messages."""

import json
import logging
import os
from typing import Any, Dict

import urllib3

logger = logging.getLogger(__name__)

http = urllib3.PoolManager()

SUCCESS_STATUS_CODE = 200


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
