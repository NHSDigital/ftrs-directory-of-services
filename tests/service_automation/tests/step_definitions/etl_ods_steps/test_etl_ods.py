"""Refactored ETL ODS BDD tests using modular utilities."""

import os
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from pytest_bdd import given, parsers, scenarios, then, when

# Common Steps
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.common.constants import ENV_WORKSPACE
from utilities.common.context import Context
from utilities.common.resource_name import get_resource_name
from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.logs_util import CloudWatchLogsWrapper
from utilities.ods.log_utils import (
    assert_cloudwatch_logs,
    verify_all_messages_share_correlation_id,
    verify_lambda_logs,
    verify_message_in_logs,
    verify_validation_error_logged,
)
from utilities.ods.queue_utils import (
    create_problem_message,
    process_message_in_queue,
    setup_queue_config,
    verify_message_in_queue_by_id,
)
from utilities.ods.validation_utils import (
    assert_lambda_error_message,
    verify_consumer_success,
    verify_dynamodb_records,
    verify_lambda_status_code,
)

# Load feature files
scenarios(
    "./etl_ods_features/etl_ods_happy.feature",
    "./etl_ods_features/etl_ods_unhappy.feature",
)

# Test Configuration Constants
MESSAGE_PROCESSING_DELAY = 5  # Seconds to wait for message processing


def invoke_lambda_generic(
    context: Context,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client: LambdaWrapper,
    date_param: Optional[str] = None,
) -> Context:
    """Invoke ETL ODS extractor lambda with parameters."""
    lambda_name = get_resource_name(
        project, workspace, env, "etl-ods-extractor", "lambda"
    )
    context.lambda_name = lambda_name
    payload = {"date": date_param} if date_param else {}

    try:
        response = aws_lambda_client.invoke_function(lambda_name, payload)
    except Exception as e:
        logger.exception(f"[ERROR] Failed to invoke Lambda: {e}")
        raise

    context.lambda_response = response
    return context


# ==================== Background Steps ====================


@given("the ETL ODS infrastructure is available")
def etl_ods_infrastructure_available(
    context: Context, aws_lambda_client: LambdaWrapper
) -> None:
    context.project = "ftrs-dos"
    context.workspace = os.getenv(ENV_WORKSPACE, "")
    context.env = "dev"

    # Setup both transform and load queues
    setup_queue_config(context, "transform", aws_lambda_client)
    setup_queue_config(context, "load", aws_lambda_client)


# ==================== Given Steps ====================


@given("extract ODS organisation records using a valid date")
def extract_ods_organisation_records_valid_date(
    context: Context,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client: LambdaWrapper,
) -> None:
    """Extract ODS organisation records using the valid extraction date."""
    context = invoke_lambda_generic(
        context,
        project,
        workspace,
        env,
        aws_lambda_client,
        date_param=context.extraction_date,
    )
    context.lambda_invocation_time = int(datetime.now(timezone.utc).timestamp())


@given(
    parsers.parse("I have a {queue_type} message that will fail with {status_code:d}")
)
@given(parsers.parse("I have a {queue_type} message with {problem_type}"))
@given(parsers.parse("I have a {queue_type} message that will {error_condition}"))
def create_problem_message_step(
    context: Context,
    queue_type: str,
    problem_type: str = None,
    status_code: int = None,
    error_condition: str = None,
) -> None:
    """Create a message with specified problem type or error condition."""
    create_problem_message(
        context, queue_type, problem_type, status_code, error_condition
    )


@given(
    parsers.parse('I trigger the ODS ETL pipeline with invalid date "{invalid_date}"')
)
def step_trigger_pipeline_invalid_date(
    context: Context,
    invalid_date: str,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client: LambdaWrapper,
) -> None:
    """Trigger ETL pipeline with an invalid date parameter."""
    context = invoke_lambda_generic(
        context, project, workspace, env, aws_lambda_client, date_param=invalid_date
    )


@given("I trigger the ODS ETL pipeline without required parameters")
def step_trigger_pipeline_without_params(
    context: Context,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client: LambdaWrapper,
) -> None:
    """Trigger ETL pipeline without required parameters."""
    context = invoke_lambda_generic(
        context, project, workspace, env, aws_lambda_client, date_param=None
    )


@given(
    parsers.parse('I trigger the ODS ETL pipeline with a long past date "{past_date}"')
)
def step_trigger_pipeline_long_past_date(
    context: Context,
    past_date: str,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client: LambdaWrapper,
) -> None:
    """Trigger ETL pipeline with a date that's too far in the past."""
    context = invoke_lambda_generic(
        context, project, workspace, env, aws_lambda_client, date_param=past_date
    )


@given(
    "extract ODS organisation records modified since yesterday",
    target_fixture="context",
)
def extract_ods_codes(context):
    return context


@given(
    "extract detailed organisation information for those ODS codes",
    target_fixture="context",
)
def load_organisation_info(context):
    return context


# ==================== When Steps ====================


@given("I trigger the ODS ETL pipeline with the valid date", target_fixture="context")
@when("I trigger the ODS ETL pipeline with the valid date", target_fixture="context")
def step_invoke_valid_date(
    context: Context, project, workspace, env, aws_lambda_client
):
    context = invoke_lambda_generic(
        context,
        project,
        workspace,
        env,
        aws_lambda_client,
        date_param=context.extraction_date,
    )
    context.lambda_invocation_time = int(datetime.now(timezone.utc).timestamp())
    return context


@when(parsers.parse('the "{queue_type}" lambda processes the message'))
def process_message(context: Context, queue_type: str):
    process_message_in_queue(context, queue_type)


# ==================== Then Steps ====================
@then(parsers.parse('the error message should be "{expected_message}"'))
def assert_lambda_error_message_step(context: Context, expected_message):
    assert_lambda_error_message(context, expected_message)


@then(
    parsers.parse(
        'the Lambda extracts, transforms, and publishes the transformed message to SQS for "{ods_type}" ODS codes'
    )
)
def verify_lambda_logs_step(context: Context, cloudwatch_logs, ods_type: str):
    verify_lambda_logs(context, cloudwatch_logs)


@then("the consumer should update DynamoDB successfully")
def verify_consumer_success_step(context: Context):
    """Verify that the consumer processed messages successfully."""
    verify_consumer_success(context)


@then(parsers.parse('the logs for the message should contain "{expected_text}"'))
def verify_message_in_logs_step(
    context: Context, expected_text: str, cloudwatch_logs
) -> None:
    """Verify expected text appears in logs for the test message's correlation_id."""
    verify_message_in_logs(context, expected_text, cloudwatch_logs)


@then(
    parsers.parse(
        'the organisation data should be updated in DynamoDB for "{ods_type}" ODS codes'
    )
)
def verify_dynamodb_records_step(context: Context, model_repo, ods_type: str):
    """Verify organization data is properly stored in DynamoDB."""
    verify_dynamodb_records(context, model_repo, ods_type)


@then(parsers.parse("the lambda should return status code {status_code:d}"))
def verify_lambda_status_code_step(context: Context, status_code: int) -> None:
    """Verify lambda returned expected status code."""
    verify_lambda_status_code(context, status_code)


@then("all messages should share the same correlation_id")
def verify_all_messages_share_correlation_id_step(
    context: Context, cloudwatch_logs
) -> None:
    """Verify all messages in extractor, transformer, and consumer lambdas share the same correlation_id."""
    verify_all_messages_share_correlation_id(context, cloudwatch_logs)


@then("the ETL ODS extraction should complete successfully")
def etl_ods_extraction_success(context: Context, cloudwatch_logs) -> None:
    """Verify ETL ODS extraction completed successfully."""
    assert_cloudwatch_logs(
        context.lambda_name, cloudwatch_logs, "Extraction completed successfully"
    )


@then(parsers.parse('the "{queue_type}" {queue_or_dlq} should {have_or_not} message'))
def verify_message_in_queue_by_id_step(
    context: Context,
    queue_type: str,
    queue_or_dlq: str,
    have_or_not: str,
) -> None:
    """Check if test message is present/absent in queue by its message ID."""
    verify_message_in_queue_by_id(context, queue_type, queue_or_dlq, have_or_not)


@then(parsers.parse('the Lambda should log the validation error "{error_code}"'))
def verify_validation_error_logged_step(
    context: Context,
    cloudwatch_logs: CloudWatchLogsWrapper,
    error_code: str,
):
    verify_validation_error_logged(context, cloudwatch_logs, error_code)
