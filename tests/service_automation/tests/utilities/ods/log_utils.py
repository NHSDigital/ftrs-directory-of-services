import time
from typing import List

from utilities.common.context import Context
from utilities.infra.logs_util import (
    CloudWatchLogsWrapper,
    extract_correlation_id_from_logs,
)


def get_log_group_name(context: Context) -> str:
    """Get the appropriate log group name based on context."""
    queue_type = getattr(context, "current_queue_type", None)

    if (
        queue_type
        and hasattr(context, "queue_configs")
        and queue_type in context.queue_configs
    ):
        lambda_name = context.queue_configs[queue_type]["lambda_name"]
        log_group_name = f"/aws/lambda/{lambda_name}"
        return log_group_name
    else:
        log_group_name = f"/aws/lambda/{context.lambda_name}"
        return log_group_name


def get_logs_for_correlation_id(
    context: Context,
    cloudwatch_logs: CloudWatchLogsWrapper,
    correlation_id: str,
    log_group_name: str = None,
) -> List[dict]:
    """Fetch and cache logs for correlation_id."""
    if not hasattr(context, "correlation_id_logs_cache"):
        context.correlation_id_logs_cache = {}
    if correlation_id in context.correlation_id_logs_cache:
        return context.correlation_id_logs_cache[correlation_id]

    log_group_name = log_group_name or get_log_group_name(context)

    # Try filter patterns
    for pattern in [
        f'"{correlation_id}"',
        f'{{ $.correlation_id = "{correlation_id}" }}',
        correlation_id,
    ]:
        try:
            logs = cloudwatch_logs.get_logs_by_filter(
                log_group_name=log_group_name, filter_pattern=pattern, minutes=60
            )
            if logs:
                # Remove duplicates
                seen = set()
                unique_logs = []
                for log in logs:
                    msg = log.get("message", "")
                    if msg not in seen:
                        seen.add(msg)
                        unique_logs.append(log)
                context.correlation_id_logs_cache[correlation_id] = unique_logs
                return unique_logs
        except Exception:
            continue

    context.correlation_id_logs_cache[correlation_id] = []
    return []


def assert_message_in_logs(
    context: Context,
    cloudwatch_logs: CloudWatchLogsWrapper,
    correlation_id: str,
    expected_message: str,
    case_sensitive: bool = True,
    log_group_name: str = None,
):
    """Assert that a specific message appears in logs for the given correlation_id."""
    # Retry logic for log availability
    max_retries = 3
    for attempt in range(max_retries):
        if attempt > 0:
            time.sleep(15)  # Wait longer between retries
            # Clear cache to force fresh log retrieval
            if (
                hasattr(context, "correlation_id_logs_cache")
                and correlation_id in context.correlation_id_logs_cache
            ):
                del context.correlation_id_logs_cache[correlation_id]

        logs = get_logs_for_correlation_id(
            context, cloudwatch_logs, correlation_id, log_group_name
        )
        if logs:
            break

    assert logs, (
        f"No logs found for correlation_id: {correlation_id} after {max_retries} attempts. Wait longer between execution and verification."
    )

    log_text = " ".join([event.get("message", "") for event in logs])
    found = (
        expected_message in log_text
        if case_sensitive
        else expected_message.lower() in log_text.lower()
    )

    assert found, (
        f"Expected message '{expected_message}' not found in logs for correlation_id {correlation_id}. Log content: {log_text[:500]}..."
    )


def validate_lambda_logs_for_extraction(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    """Validate lambda logs contain expected extraction patterns."""
    time.sleep(30)  # Central wait_for_logs()
    extraction_pattern = (
        f'"Fetching outdated organizations for date: {context.extraction_date}."'
    )
    transformation_pattern = '"Fetching ODS Data returned .* outdated organisations."'
    publishing_pattern = "Succeeded to send"

    assert cloudwatch_logs.find_log_message(context.lambda_name, extraction_pattern)
    assert cloudwatch_logs.find_log_message(context.lambda_name, transformation_pattern)
    assert cloudwatch_logs.find_log_message(context.lambda_name, publishing_pattern)


def verify_malformed_json_logs(
    context: Context,
    expected_text: str,
    cloudwatch_logs: CloudWatchLogsWrapper,
    log_group_name: str,
):
    """Handle malformed JSON message log verification."""
    time.sleep(10)  # Wait for logs to be available
    logs = cloudwatch_logs.get_logs_by_filter(
        log_group_name=log_group_name, filter_pattern="", minutes=15
    )
    assert logs, f"No recent logs found in {log_group_name}"

    log_text = " ".join([event.get("message", "") for event in logs])
    found = expected_text.lower() in log_text.lower()
    assert found, (
        f"Expected message '{expected_text}' not found in recent lambda logs. Searched {len(logs)} log events. Full log content: {log_text}"
    )


def assert_cloudwatch_logs(
    lambda_name: str, cloudwatch_logs: CloudWatchLogsWrapper, expected_log: str
):
    """Validate a log message exists in CloudWatch for the given Lambda."""
    found_log = cloudwatch_logs.find_log_message(lambda_name, expected_log)
    assert found_log, f"Expected log '{expected_log}' not found in Lambda {lambda_name}"


def verify_validation_error_logged(
    context, cloudwatch_logs: CloudWatchLogsWrapper, error_code: str
):
    """Verify validation error is logged."""
    assert_cloudwatch_logs(
        lambda_name=context.lambda_name,
        cloudwatch_logs=cloudwatch_logs,
        expected_log=error_code,
    )


def verify_all_messages_share_correlation_id(context, cloudwatch_logs) -> None:
    """Verify all messages in extractor, transformer, and consumer lambdas share the same correlation_id."""
    # Get correlation ID from extractor lambda logs
    extractor_log_group = f"/aws/lambda/{context.lambda_name}"
    extractor_logs = cloudwatch_logs.get_logs_by_filter(
        log_group_name=extractor_log_group,
        filter_pattern="",
    )

    assert extractor_logs, "No logs found in extractor lambda"
    extractor_corr_id = extract_correlation_id_from_logs(extractor_logs)
    assert extractor_corr_id is not None, (
        "Could not extract correlation_id from extractor logs"
    )

    # Check transformer lambda logs for the same correlation ID
    if hasattr(context, "queue_configs") and "transform" in context.queue_configs:
        transformer_lambda_name = context.queue_configs["transform"]["lambda_name"]
        transformer_log_group = f"/aws/lambda/{transformer_lambda_name}"

        assert_message_in_logs(
            context,
            cloudwatch_logs,
            extractor_corr_id,
            "",
            case_sensitive=False,
            log_group_name=transformer_log_group,
        )

    # Check consumer lambda logs for the same correlation ID
    if hasattr(context, "queue_configs") and "load" in context.queue_configs:
        consumer_lambda_name = context.queue_configs["load"]["lambda_name"]
        consumer_log_group = f"/aws/lambda/{consumer_lambda_name}"

        assert_message_in_logs(
            context,
            cloudwatch_logs,
            extractor_corr_id,
            "",
            case_sensitive=False,
            log_group_name=consumer_log_group,
        )


def verify_message_in_logs(
    context: Context, expected_text: str, cloudwatch_logs
) -> None:
    """Verify expected text appears in logs for the test message's correlation_id."""
    log_group_name = get_log_group_name(context)

    # Handle malformed JSON separately
    if hasattr(context, "test_message_raw"):
        verify_malformed_json_logs(
            context, expected_text, cloudwatch_logs, log_group_name
        )
        return

    assert hasattr(context, "message_correlation_id"), (
        "No message_correlation_id found in context. Ensure create_test_message was called."
    )
    correlation_id = context.message_correlation_id
    assert_message_in_logs(
        context,
        cloudwatch_logs,
        correlation_id,
        expected_text,
        case_sensitive=False,
        log_group_name=log_group_name,
    )


def verify_lambda_logs(context: Context, cloudwatch_logs) -> None:
    """Verify lambda logs for extraction process."""
    validate_lambda_logs_for_extraction(context, cloudwatch_logs)
