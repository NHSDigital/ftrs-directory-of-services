import re
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import boto3
from botocore.exceptions import ClientError
from loguru import logger


class CloudWatchLogsWrapper:
    def __init__(self):
        try:
            self.logs_client = boto3.client("logs")
        except ClientError as e:
            logger.error(f"Error initializing CloudWatch Logs client: {e}")
            raise

    def get_lambda_logs(self, lambda_name: str, filter_pattern: str = "") -> List[dict]:
        """
        Convenience method to retrieve logs for a Lambda function by name.

        Args:
            lambda_name: Name of the Lambda function
            filter_pattern: CloudWatch Logs filter pattern

        Returns:
            List of log events
        """
        log_group_name = f"/aws/lambda/{lambda_name}"
        return self.get_logs_by_filter(log_group_name, filter_pattern)

    def find_log_message(
        self,
        lambda_name: str,
        message_pattern: str,
        timeout: int = 90,
        interval: int = 5,
    ) -> bool:
        """
        Search for a specific message pattern in Lambda logs with polling.

        Args:
            lambda_name: Name of the Lambda function
            message_pattern: String pattern to search for
            timeout: Maximum seconds to poll for logs (default: 90)
            interval: Seconds between polling attempts (default: 5)

        Returns:
            True if message pattern is found, False otherwise
        """
        elapsed = 0
        while elapsed < timeout:
            log_events = self.get_lambda_logs(
                lambda_name, filter_pattern=message_pattern
            )
            if log_events:
                logger.info(
                    f"Found log message '{message_pattern}' in {lambda_name} after {elapsed}s"
                )
                return True
            time.sleep(interval)
            elapsed += interval
            logger.info(f"Log message not found yet, retrying... ({elapsed}s elapsed)")

        logger.warning(
            f"Log message '{message_pattern}' not found in {lambda_name} after {timeout}s"
        )
        return False

    def get_logs_by_filter(
        self, log_group_name: str, filter_pattern: str = "", minutes: int = 30
    ) -> List[dict]:
        """
        Retrieve CloudWatch logs for a log group using a filter pattern.

        Args:
            log_group_name: Name of the CloudWatch log group (e.g., /aws/lambda/function-name)
            filter_pattern: CloudWatch Logs filter pattern to search for
            minutes: How many minutes back to search (default: 15)

        Returns:
            List of log events with 'timestamp', 'message', and other metadata
        """
        try:
            # Add time window to avoid searching entire log history
            end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
            start_time = int(
                (datetime.now(timezone.utc) - timedelta(minutes=minutes)).timestamp()
                * 1000
            )

            params = {
                "logGroupName": log_group_name,
                "startTime": start_time,
                "endTime": end_time,
                "limit": 10000,
            }

            if filter_pattern:
                params["filterPattern"] = filter_pattern

            log_events = []
            response = self.logs_client.filter_log_events(**params)
            log_events.extend(response.get("events", []))

            # Handle pagination
            while "nextToken" in response:
                params["nextToken"] = response["nextToken"]
                response = self.logs_client.filter_log_events(**params)
                log_events.extend(response.get("events", []))

            return log_events

        except ClientError as e:
            logger.error(f"Error retrieving logs from {log_group_name}: {e}")
            return []


# ==================== Standalone Log Helper Functions ====================


def extract_pattern_from_logs(
    logs: List[dict], pattern: str, group_index: int = 1
) -> Optional[str]:
    """
    Extract a pattern from CloudWatch logs using regex.

    Args:
        logs: List of log events from CloudWatch (with 'message' field)
        pattern: Regex pattern to search for
        group_index: Which regex capture group to return (default: 1)

    Returns:
        First matching string found, or None if no match
    """
    for event in logs:
        message = event.get("message", "")
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            try:
                extracted_value = match.group(group_index)
                logger.info(f"Extracted pattern from logs: {extracted_value}")
                return extracted_value
            except IndexError:
                logger.warning(f"Pattern matched but group {group_index} not found")
                continue

    logger.warning(f"No match found for pattern: {pattern}")
    return None


def extract_correlation_id_from_logs(
    logs: List[dict], pattern: str = r"correlation[_-]?id[\"\\s:]+([a-f0-9-]+)"
) -> Optional[str]:
    """
    Extract correlation_id from CloudWatch logs using common patterns.

    Args:
        logs: List of log events from CloudWatch
        pattern: Regex pattern to match correlation_id (default: matches common formats)

    Returns:
        Correlation ID string if found, None otherwise
    """
    return extract_pattern_from_logs(logs, pattern, group_index=1)
