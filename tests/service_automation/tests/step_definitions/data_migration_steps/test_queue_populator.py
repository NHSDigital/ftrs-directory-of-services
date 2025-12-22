"""Step definitions for Queue Populator Lambda tests"""
import json
import time
from pathlib import Path
import pytest
from pytest_bdd import parsers, scenarios, then, when
from utilities.common.context import Context
from utilities.common.resource_name import get_resource_name
from loguru import logger

# Import all common steps to register them (this includes "the test environment is configured")
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403, F401

# Load feature file - use absolute path from this file's location
FEATURE_FILE = str(Path(__file__).parent.parent.parent / "features" / "data_migration_features" / "queue_populator_lambda.feature")
scenarios(FEATURE_FILE)


# Note: "the test environment is configured" step is provided by common_steps.data_migration_steps
# which is imported above, so no need to redefine it here


@when("the queue populator Lambda is invoked with event:")
def invoke_queue_populator_lambda(
    context: Context,
    project,
    workspace,
    env,
    sqs_queues,
    dos_db_with_migration,
    datatable,
):
    """
    Invoke queue populator logic directly (not via Lambda).

    Args:
        context: Test context
        project: Project name
        workspace: Workspace suffix
        env: Environment name
        sqs_queues: SQS fixture with queue URLs
        dos_db_with_migration: DoS database session
        datatable: Event parameters from feature file
    """
    from queue_populator.lambda_handler import populate_sqs_queue
    from queue_populator.config import QueuePopulatorConfig
    from common.config import DatabaseConfig
    import os

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

    logger.info(f"Invoking queue populator with payload: {json.dumps(event_payload, indent=2)}")

    # Get Lambda name for context (even though we won't invoke it)
    context.lambda_name = get_resource_name(
        project=project,
        workspace=workspace,
        env=env,
        stack="data-migration",
        resource="queue-populator-lambda"
    )

    # Build config for queue populator
    # Use database connection from dos_db_with_migration fixture
    db_connection_string = dos_db_with_migration.bind.url.render_as_string(hide_password=False)

    # Set environment variable for SQS queue URL
    # In CI/CD, this will be None and should be set from environment
    if sqs_queues["queue_url"]:
        os.environ["SQS_QUEUE_URL"] = sqs_queues["queue_url"]

    config = QueuePopulatorConfig(
        db_config=DatabaseConfig.from_uri(db_connection_string),
        type_ids=event_payload.get("type_ids"),
        status_ids=event_payload.get("status_ids"),
        service_id=event_payload.get("service_id"),
        record_id=event_payload.get("record_id"),
        full_sync=event_payload.get("service_id") is None,
        table_name=event_payload.get("table_name", "services"),
    )

    # Record start time
    start_time = time.time()

    try:
        # Only monkey-patch SQS_CLIENT for LocalStack (local dev)
        # In CI/CD, use the real AWS client
        if sqs_queues["endpoint_url"]:  # LocalStack
            import queue_populator.lambda_handler as qp_module
            original_sqs_client = qp_module.SQS_CLIENT
            qp_module.SQS_CLIENT = sqs_queues["client"]

        # Call the queue populator directly
        populate_sqs_queue(config=config)

        # Restore original SQS client if we patched it
        if sqs_queues["endpoint_url"]:
            qp_module.SQS_CLIENT = original_sqs_client

        # Record end time and duration
        end_time = time.time()
        context.lambda_duration_ms = (end_time - start_time) * 1000

        # Store response
        context.lambda_response = {"statusCode": 200}
        context.sqs_client = sqs_queues["client"]
        context.queue_url = sqs_queues["queue_url"]

        logger.info(f"Queue populator completed in {context.lambda_duration_ms:.2f}ms")
    except Exception as e:
        logger.exception(f"Queue populator failed: {e}")
        context.lambda_error = str(e)
        raise

    return context

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
    context: Context, log_reference: str, caplog
):
    """
    Verify that logs contain the expected log reference.
    Since we're calling the code directly, we check captured logs.

    Args:
        context: Test context containing Lambda name
        log_reference: The log reference pattern to search for (e.g., "DM_QP_000")
        caplog: Pytest fixture for capturing logs
    """
    logger.info(f"Verifying logs contain: {log_reference}")

    # Check if the log reference appears in any captured log message
    found = any(log_reference in record.message for record in caplog.records)

    assert found, (
        f"Log reference '{log_reference}' not found in captured logs. "
        f"Available logs: {[r.message for r in caplog.records]}"
    )

    logger.info(f"Successfully found log reference: {log_reference}")



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
        context: Test context with SQS client and queue URL
        min_messages: Minimum expected number of messages in the queue
    """
    logger.info(f"Verifying SQS queue contains at least {min_messages} message(s)")

    try:
        # Get message count from queue attributes
        response = context.sqs_client.get_queue_attributes(
            QueueUrl=context.queue_url,
            AttributeNames=["ApproximateNumberOfMessages"]
        )

        actual_count = int(response["Attributes"]["ApproximateNumberOfMessages"])

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

