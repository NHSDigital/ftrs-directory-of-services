"""Step definitions for Queue Populator Lambda tests"""
import json
import time
from datetime import datetime
from pathlib import Path
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from utilities.common.context import Context
from utilities.common.resource_name import get_resource_name
from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.logs_util import CloudWatchLogsWrapper
from utilities.infra.sqs_util import get_queue_url, get_approximate_message_count
import boto3
from loguru import logger

# Import common steps (this will register them)
from step_definitions.common_steps import data_migration_steps  # noqa: F401

# Load feature file - use absolute path from this file's location
FEATURE_FILE = str(Path(__file__).parent.parent.parent / "features" / "data_migration_features" / "queue_populator_lambda.feature")
scenarios(FEATURE_FILE)


@given("the test environment is configured")
def environment_configured(migration_helper, dynamodb):
    """Verify test environment is properly configured."""
    from tests.service_automation.tests.step_definitions.common_steps.data_migration_steps import DYNAMODB_CLIENT

    try:
        response = dynamodb[DYNAMODB_CLIENT].list_tables()
        table_names = response.get("TableNames", [])
        logger.info(f"DynamoDB tables available: {table_names}")
        assert len(table_names) > 0, "No DynamoDB tables found in test environment"
    except Exception as e:
        logger.error(f"Failed to verify test environment: {str(e)}")
        raise


@pytest.fixture(scope="module")
def aws_lambda_client():
    """Create Lambda client wrapper"""
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    return LambdaWrapper(lambda_client, iam_resource)


@pytest.fixture(scope="module")
def cloudwatch_logs():
    """Create CloudWatch Logs client wrapper"""
    return CloudWatchLogsWrapper()


@pytest.fixture(scope="function")
def context():
    """Create test context for each test scenario"""
    return Context()


@when(parsers.parse("the queue populator Lambda is invoked with event:\n{event_table}"))
def invoke_queue_populator_lambda(
    context: Context, aws_lambda_client: LambdaWrapper, event_table: str
):
    """
    Invoke the queue populator Lambda with specified event parameters.

    Args:
        context: Test context to store Lambda response and timing
        aws_lambda_client: Lambda client wrapper
        event_table: Table of key-value pairs for the event payload
    """
    # Parse the event table into a dictionary
    event_payload = {}
    for line in event_table.strip().split("\n"):
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) == 2 and parts[0].lower() not in ["key", "----"]:
            key = parts[0]
            value = parts[1]

            # Handle special values
            if value.lower() == "null":
                event_payload[key] = None
            elif value.startswith("[") and value.endswith("]"):
                # Parse array values like [100] or [1]
                event_payload[key] = json.loads(value)
            elif value.isdigit():
                event_payload[key] = int(value)
            else:
                event_payload[key] = value

    logger.info(f"Invoking queue populator Lambda with payload: {json.dumps(event_payload, indent=2)}")

    # Get Lambda name from resource naming convention
    # Based on manual tests: ftrs-dos-dev-data-migration-queue-populator-lambda-ftrs-1898
    context.lambda_name = get_resource_name(
        "data-migration-queue-populator-lambda",
        workspace="ftrs-1898"
    )

    # Record start time for duration measurement
    context.lambda_start_time = datetime.now()

    # Invoke Lambda
    try:
        response = aws_lambda_client.invoke_function(
            context.lambda_name,
            event_payload
        )
        context.lambda_response = response
        context.lambda_end_time = datetime.now()
        context.lambda_duration_ms = (
            context.lambda_end_time - context.lambda_start_time
        ).total_seconds() * 1000

        logger.info(f"Lambda invocation completed in {context.lambda_duration_ms:.2f}ms")
        logger.info(f"Lambda response: {json.dumps(response, indent=2)}")

    except Exception as e:
        context.lambda_error = e
        context.lambda_end_time = datetime.now()
        logger.error(f"Lambda invocation failed: {str(e)}")
        raise


@then("the Lambda execution should complete successfully")
def verify_lambda_success(context: Context):
    """
    Verify that the Lambda execution completed without errors.

    Args:
        context: Test context containing Lambda response
    """
    assert hasattr(context, "lambda_response"), "Lambda was not invoked"
    assert not hasattr(context, "lambda_error"), f"Lambda failed with error: {context.lambda_error}"

    # Check for error in response
    if isinstance(context.lambda_response, dict):
        assert "errorMessage" not in context.lambda_response, (
            f"Lambda returned error: {context.lambda_response.get('errorMessage')}"
        )
        assert context.lambda_response.get("statusCode", 200) == 200, (
            f"Lambda returned non-200 status code: {context.lambda_response.get('statusCode')}"
        )

    logger.info("Lambda execution completed successfully")


@then(parsers.parse('the CloudWatch logs should contain "{log_reference}"'))
def verify_cloudwatch_logs_contain_pattern(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper, log_reference: str
):
    """
    Verify that CloudWatch logs contain the expected log reference.
    Uses retry logic to wait for logs to appear (up to 3 minutes).

    Args:
        context: Test context containing Lambda name
        cloudwatch_logs: CloudWatch Logs client wrapper
        log_reference: The log reference pattern to search for (e.g., "DM_QP_000")
    """
    assert hasattr(context, "lambda_name"), "Lambda name not set in context"

    logger.info(f"Verifying CloudWatch logs contain: {log_reference}")

    try:
        # Use retry logic with 3 minute timeout, polling every 5 seconds
        found = cloudwatch_logs.find_log_message_with_retry(
            lambda_name=context.lambda_name,
            message_pattern=log_reference,
            timeout_minutes=3,
            poll_interval_seconds=5
        )
        assert found, f"Log reference '{log_reference}' not found in CloudWatch logs"
        logger.info(f"Successfully found log reference: {log_reference}")

    except TimeoutError as e:
        pytest.fail(str(e))


@then(parsers.parse("the Lambda execution duration should be less than {max_duration:d} milliseconds"))
def verify_lambda_duration(context: Context, max_duration: int):
    """
    Verify that the Lambda execution duration is within acceptable limits.

    Args:
        context: Test context containing Lambda duration
        max_duration: Maximum acceptable duration in milliseconds
    """
    assert hasattr(context, "lambda_duration_ms"), "Lambda duration not measured"

    actual_duration = context.lambda_duration_ms
    logger.info(f"Lambda execution duration: {actual_duration:.2f}ms (limit: {max_duration}ms)")

    assert actual_duration < max_duration, (
        f"Lambda execution took {actual_duration:.2f}ms, "
        f"which exceeds the limit of {max_duration}ms"
    )

    logger.info(f"Lambda duration within acceptable limits")


@then(parsers.parse("the migration queue should contain at least {min_messages:d} message"))
def verify_sqs_message_count(context: Context, min_messages: int):
    """
    Verify that the migration SQS queue contains at least the expected number of messages.

    Args:
        context: Test context
        min_messages: Minimum expected number of messages in the queue
    """
    # Get the migration queue URL
    # Based on resource naming convention for data-migration-queue
    queue_name = get_resource_name(
        "data-migration-queue",
        workspace="ftrs-1898"
    )

    logger.info(f"Verifying SQS queue '{queue_name}' contains at least {min_messages} message(s)")

    try:
        queue_url = get_queue_url(queue_name)
        actual_count = get_approximate_message_count(queue_url)

        assert actual_count >= min_messages, (
            f"Expected at least {min_messages} message(s) in queue, "
            f"but found {actual_count}"
        )

        logger.info(
            f"SQS queue verification passed: {actual_count} message(s) found "
            f"(minimum required: {min_messages})"
        )

    except Exception as e:
        logger.error(f"Failed to verify SQS message count: {str(e)}")
        raise
