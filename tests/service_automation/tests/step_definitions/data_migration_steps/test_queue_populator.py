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

# Import all common steps to register them (this includes "the test environment is configured")
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403, F401

# Load feature file - use absolute path from this file's location
FEATURE_FILE = str(Path(__file__).parent.parent.parent / "features" / "data_migration_features" / "queue_populator_lambda.feature")
scenarios(FEATURE_FILE)


# Note: "the test environment is configured" step is provided by common_steps.data_migration_steps
# which is imported above, so no need to redefine it here


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


@when("the queue populator Lambda is invoked with event:")
def invoke_queue_populator_lambda(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    datatable: list[list[str]],
    project: str,
    workspace: str,
    env: str,
):
    """
    Invoke the queue populator Lambda with specified event parameters.

    Args:
        context: Test context to store Lambda response and timing
        aws_lambda_client: Lambda client wrapper
        datatable: Table of key-value pairs for the event payload from the feature file
        project: Project name from fixtures (e.g., 'ftrs-dos')
        workspace: Workspace suffix from fixtures
        env: Environment name from fixtures (e.g., 'dev', 'test')
    """
    # Parse the datatable into a dictionary
    # First row is the header, subsequent rows are data
    event_payload = {}

    if not datatable or len(datatable) < 2:
        raise ValueError("Event datatable must have at least a header row and one data row")

    # Skip header row (index 0), process data rows
    for row in datatable[1:]:
        if len(row) != 2:
            raise ValueError(f"Each row must have exactly 2 columns (key, value), got: {row}")

        key = row[0]
        value = row[1]

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
    # Lambda naming: {project}-{env}-{stack}-{resource}-{workspace}
    context.lambda_name = get_resource_name(
        project=project,
        workspace=workspace,
        env=env,
        stack="data-migration",
        resource="queue-populator-lambda"
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
def verify_sqs_message_count(
    context: Context, min_messages: int, project: str, workspace: str, env: str
):
    """
    Verify that the migration SQS queue contains at least the expected number of messages.

    Args:
        context: Test context
        min_messages: Minimum expected number of messages in the queue
        project: Project name from fixtures
        workspace: Workspace suffix from fixtures
        env: Environment name from fixtures
    """
    # Get the migration queue URL based on resource naming convention
    queue_name = get_resource_name(
        project=project,
        workspace=workspace,
        env=env,
        stack="data-migration",
        resource="queue"
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
