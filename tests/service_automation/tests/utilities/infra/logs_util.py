import time
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from loguru import logger


class CloudWatchLogsWrapper:
    def __init__(self):
        try:
            self.logs_client = boto3.client('logs')
        except (ClientError) as e:
            logger.error(f"Error initializing CloudWatch Logs client: {e}")
            raise

    def get_lambda_logs(self, lambda_name, filter_pattern=None):
        """
        Retrieve CloudWatch logs for a specific Lambda function

        Args:
            lambda_name: Name of the Lambda function
            start_time: Unix timestamp (milliseconds) for log retrieval starting point
            duration_seconds: How many seconds of logs to retrieve
            filter_pattern: Optional filter pattern to apply

        Returns:
            List of log events
        """
        try:
            log_group_name = f"/aws/lambda/{lambda_name}"

            streams_response = self.logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )

            log_events = []


            for stream in streams_response.get('logStreams', []):
                stream_name = stream['logStreamName']

                start_time = stream['firstEventTimestamp'] - (30 * 1000)  # 1 minute before first event
                end_time = stream['lastEventTimestamp'] + (30 * 1000)     # 1 minute after last event

                params = {
                    'logGroupName': log_group_name,
                    'logStreamName': stream_name,
                    'startTime': start_time,
                    'endTime': end_time,
                    'limit': 100
                }

                if filter_pattern:
                    params = {
                        'logGroupName': log_group_name,
                        'filterPattern': filter_pattern,
                        'startTime': start_time,
                        'endTime': end_time,
                        'limit': 100
                    }

                    events_response = self.logs_client.filter_log_events(**params)

                    log_events.extend(events_response.get('events', []))
                else:
                    events_response = self.logs_client.get_log_events(**params)
                    log_events.extend(events_response.get('events', []))


            return log_events

        except ClientError as e:
            logger.error(f"Error retrieving CloudWatch logs: {e}")
            return []

    def find_log_message(self, lambda_name, message_pattern):
        """
        Search for a specific message pattern in Lambda logs

        Args:
            lambda_name: Name of the Lambda function
            message_pattern: String pattern to search for
            start_time: Unix timestamp (milliseconds) for log retrieval starting point
            duration_seconds: How many seconds of logs to retrieve

        Returns:
            True if message pattern is found, False otherwise
        """
        log_events = self.get_lambda_logs(
            lambda_name,
            filter_pattern=message_pattern
        )

        return len(log_events) > 0

    def find_log_message_with_retry(
        self, lambda_name, message_pattern, timeout_minutes=3, poll_interval_seconds=5
    ):
        """
        Search for a specific message pattern in Lambda logs with retry logic.
        Polls CloudWatch Logs until the message is found or timeout is reached.

        Args:
            lambda_name: Name of the Lambda function
            message_pattern: String pattern to search for
            timeout_minutes: Maximum time to wait for logs (default: 3 minutes)
            poll_interval_seconds: Time to wait between polls (default: 5 seconds)

        Returns:
            True if message pattern is found within timeout, False otherwise

        Raises:
            TimeoutError: If message is not found within timeout period
        """
        start_time = datetime.now()
        timeout_delta = timedelta(minutes=timeout_minutes)
        found_logs = []

        logger.info(
            f"Searching for pattern '{message_pattern}' in Lambda '{lambda_name}' "
            f"with {timeout_minutes} minute timeout"
        )

        while (datetime.now() - start_time) < timeout_delta:
            log_events = self.get_lambda_logs(
                lambda_name, filter_pattern=message_pattern
            )

            if log_events:
                found_logs.extend(log_events)
                logger.info(
                    f"Found {len(log_events)} log event(s) matching pattern '{message_pattern}'"
                )
                return True

            logger.debug(
                f"Pattern '{message_pattern}' not found yet. "
                f"Elapsed: {(datetime.now() - start_time).total_seconds():.1f}s. "
                f"Retrying in {poll_interval_seconds}s..."
            )
            time.sleep(poll_interval_seconds)

        # Timeout reached without finding the pattern
        elapsed_seconds = (datetime.now() - start_time).total_seconds()
        error_msg = (
            f"Timeout: Pattern '{message_pattern}' not found in Lambda '{lambda_name}' "
            f"logs after {elapsed_seconds:.1f} seconds"
        )
        logger.error(error_msg)
        raise TimeoutError(error_msg)
