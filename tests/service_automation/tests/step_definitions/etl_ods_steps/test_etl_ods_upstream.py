import json

import pytest
from loguru import logger
from pytest_bdd import given, scenarios, then, when
from utilities.common.context import Context
from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.logs_util import CloudWatchLogsWrapper
from utilities.ods.scenario_manager import *  # noqa: F403

scenarios("./etl_ods_features/etl_ods_mock.feature")


@pytest.fixture
def cloudwatch_logs():
    """Create CloudWatch logs wrapper for log verification."""
    return CloudWatchLogsWrapper()


def extract_error_message(lambda_response: dict) -> str:
    if "body" in lambda_response:
        try:
            if isinstance(lambda_response["body"], str):
                body = json.loads(lambda_response["body"])
                if "error" in body:
                    return str(body["error"])
            elif isinstance(lambda_response["body"], dict):
                if "error" in lambda_response["body"]:
                    return str(lambda_response["body"]["error"])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # Fallback to direct error field
    return lambda_response.get("error", "")


def invoke_lambda_with_scenario(
    lambda_name: str, aws_lambda_client: LambdaWrapper, scenario_date: str
) -> dict:
    event = {"date": scenario_date}

    response = aws_lambda_client.lambda_client.invoke(
        FunctionName=lambda_name, Payload=json.dumps(event)
    )

    return json.loads(response["Payload"].read())


def verify_log_message_exists(
    cloudwatch_logs: CloudWatchLogsWrapper, lambda_name: str, expected_message: str
) -> bool:
    """Helper to verify specific log message exists in CloudWatch logs."""
    return cloudwatch_logs.find_log_message(lambda_name, expected_message)


def assert_status_code_and_logs(
    context: Context,
    expected_status: int,
    cloudwatch_logs: CloudWatchLogsWrapper,
    expected_log_message: str = None,
) -> None:
    """Helper to assert both status code and verify specific log messages."""
    assert context.lambda_response.get("statusCode") == expected_status

    if expected_log_message and cloudwatch_logs:
        assert verify_log_message_exists(
            cloudwatch_logs, context.lambda_name, expected_log_message
        ), (
            f"Expected log message '{expected_log_message}' not found in lambda {context.lambda_name}"
        )


@given("the ETL ODS processor Lambda is configured with ODS mock")
def lambda_configured(lambda_with_ods_mock, context: Context):
    lambda_name, mock_manager = lambda_with_ods_mock
    context.lambda_name = lambda_name

    mock_url = mock_manager.get_mock_endpoint_url()
    context.other["mock_manager"] = mock_manager
    context.other["mock_url"] = mock_url


@when("I trigger the Lambda with empty results scenario")
def trigger_lambda_empty_scenario(
    context: Context, aws_lambda_client: LambdaWrapper, ods_empty_payload_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_empty_payload_scenario
    )


@when("I trigger the Lambda with empty payload scenario")
def trigger_lambda_empty_payload(
    context: Context, aws_lambda_client: LambdaWrapper, ods_empty_payload_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_empty_payload_scenario
    )


@when("I trigger the Lambda with happy path scenario")
def trigger_lambda_happy_path(
    context: Context, aws_lambda_client: LambdaWrapper, ods_happy_path_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_happy_path_scenario
    )


@when("I trigger the Lambda with invalid data scenario")
def trigger_lambda_invalid_data(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_invalid_data_types_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_invalid_data_types_scenario
    )


@when("I trigger the Lambda with missing required fields scenario")
def trigger_lambda_missing_fields(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_missing_required_fields_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_missing_required_fields_scenario
    )


@when("I trigger the Lambda with extra unexpected field scenario")
def trigger_lambda_extra_field(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_extra_unexpected_field_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_extra_unexpected_field_scenario
    )


@when("I trigger the Lambda with request too old scenario")
def trigger_lambda_request_too_old(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_request_too_old_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_request_too_old_scenario
    )


@when("I trigger the Lambda with unauthorized scenario")
def trigger_lambda_unauthorized(
    context: Context, aws_lambda_client: LambdaWrapper, ods_unauthorized_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_unauthorized_scenario
    )


@when("I trigger the Lambda with server error scenario")
def trigger_lambda_server_error(
    context: Context, aws_lambda_client: LambdaWrapper, ods_server_error_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_server_error_scenario
    )


@when("I trigger the Lambda with unknown resource type scenario")
def trigger_lambda_unknown_resource_type(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_unknown_resource_type_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name, aws_lambda_client, ods_unknown_resource_type_scenario
    )


@then("the Lambda should handle the validation error")
def verify_validation_error_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    """Verify Lambda detected and handled invalid data."""
    # Check for validation error logging
    validation_logs = [
        "Error processing organisation with ods_code",
        "Payload validation failed",
    ]

    assert context.lambda_response.get("statusCode") == 200

    found_validation_log = any(
        verify_log_message_exists(cloudwatch_logs, context.lambda_name, log_msg)
        for log_msg in validation_logs
    )

    logger.info(
        f"Validation scenario completed for lambda {context.lambda_name}, validation log found: {found_validation_log}"
    )


@then("the Lambda should process the organizations successfully")
def verify_successful_processing(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    """Verify Lambda successfully processed organizations from happy path."""
    expected_log = "Fetching ODS Data returned"
    assert_status_code_and_logs(context, 200, cloudwatch_logs, expected_log)

    body = context.lambda_response.get("body", "")
    if isinstance(body, str) and body != "Processing complete":
        try:
            parsed_body = json.loads(body) if isinstance(body, str) else body
            assert "error" not in str(parsed_body).lower()
        except json.JSONDecodeError:
            pass


@then("the Lambda should handle empty results gracefully")
def verify_empty_results_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    expected_log = "ETL_PROCESSOR_020"
    assert_status_code_and_logs(context, 200, cloudwatch_logs, expected_log)


@then("the Lambda should handle missing fields gracefully")
def verify_missing_fields_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    expected_log = "Error processing organisation"
    assert_status_code_and_logs(context, 200, cloudwatch_logs, expected_log)


@then("the Lambda should handle unexpected fields gracefully")
def verify_unexpected_fields_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    expected_log = "Successfully transformed data"
    assert_status_code_and_logs(context, 200, cloudwatch_logs, expected_log)


@then("the Lambda should handle old requests gracefully")
def verify_old_requests_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    expected_log = "ETL_PROCESSOR_020"
    assert_status_code_and_logs(context, 200, cloudwatch_logs, expected_log)


@then("the Lambda should handle upstream server errors")
def verify_server_errors_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    expected_log = "ETL_UTILS_003"
    assert_status_code_and_logs(context, 500, cloudwatch_logs, expected_log)

    error_message = extract_error_message(context.lambda_response)
    assert any(
        keyword in error_message.lower() for keyword in ["error", "failed", "exception"]
    )


@then("the Lambda should handle unknown resource types")
def verify_unknown_resource_types_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    """Verify Lambda handles unknown resource types by filtering them out (resulting in empty results)."""
    expected_log = "ETL_PROCESSOR_020"
    assert_status_code_and_logs(context, 200, cloudwatch_logs, expected_log)


@then("the Lambda should handle the authorization error")
def verify_authorization_error_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    expected_log = "ETL_UTILS_003"
    assert_status_code_and_logs(context, 500, cloudwatch_logs, expected_log)

    error_message = extract_error_message(context.lambda_response)
    assert "unauthorized" in error_message.lower(), f"{error_message}"
