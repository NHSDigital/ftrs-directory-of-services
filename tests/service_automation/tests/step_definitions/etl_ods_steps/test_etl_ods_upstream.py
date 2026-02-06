import json
import time
import uuid
from datetime import date

from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository, ModelType
from loguru import logger
from pytest_bdd import given, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403
from utilities.common.context import Context
from utilities.common.resource_name import get_resource_name
from utilities.infra.lambda_util import LambdaWrapper
from utilities.infra.logs_util import CloudWatchLogsWrapper
from utilities.ods.scenario_manager import *  # noqa: F403

scenarios("./etl_ods_features/etl_ods_mock.feature")


def get_from_repo(
    model_repo: AttributeLevelRepository, model_id: str
) -> ModelType | None:
    logger.debug(f"Fetching record with ID: {model_id}")
    item = model_repo.get(model_id)
    if item is None:
        logger.error(f"No data found for model ID: {model_id}")
    return item


def extract_error_message(lambda_response: dict) -> str:
    """Extracts an error message from Lambda response if present."""
    if "body" in lambda_response:
        try:
            body = lambda_response["body"]
            if isinstance(body, str):
                body = json.loads(body)
            if isinstance(body, dict) and "error" in body:
                return str(body["error"])
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
    return lambda_response.get("error", "")


def invoke_lambda_with_scenario(
    context: Context,
    lambda_name: str,
    aws_lambda_client: LambdaWrapper,
    scenario_date: str,
) -> dict:
    context.correlation_id = str(uuid.uuid4())
    event = {
        "date": scenario_date,
        "headers": {"X-Correlation-ID": context.correlation_id},
    }
    response = aws_lambda_client.lambda_client.invoke(
        FunctionName=lambda_name, Payload=json.dumps(event)
    )
    logger.info(f"Correlation-ID: {context.correlation_id}")
    return json.loads(response["Payload"].read())


def assert_cloudwatch_logs(
    lambda_name: str,
    cloudwatch_logs: CloudWatchLogsWrapper,
    expected_log: str,
):
    """Validate a log message exists in CloudWatch for the given Lambda."""
    found_log = cloudwatch_logs.find_log_message(lambda_name, expected_log)
    assert found_log, f"Expected log '{expected_log}' not found in Lambda {lambda_name}"


def assert_lambda_response(
    context: Context,
    cloudwatch_logs: CloudWatchLogsWrapper,
    expected_status: int,
    expected_log: str = None,
    expected_error_keywords: list[str] = None,
):
    """
    Unified helper to validate Lambda response.

    Args:
        context: Test context with Lambda response
        cloudwatch_logs: CloudWatchLogsWrapper instance
        expected_status: Expected HTTP status code
        expected_log: Expected log message to verify in CloudWatch
        expected_error_keywords: List of keywords to check in Lambda error message
    """
    assert context.lambda_response.get("statusCode") == expected_status

    if expected_log and cloudwatch_logs:
        found_log = cloudwatch_logs.find_log_message(context.lambda_name, expected_log)
        assert found_log, (
            f"Expected log '{expected_log}' not found in Lambda {context.lambda_name}"
        )

    if expected_error_keywords:
        error_message = extract_error_message(context.lambda_response).lower()
        assert any(
            keyword.lower() in error_message for keyword in expected_error_keywords
        ), (
            f"Expected one of {expected_error_keywords} in error message, got: {error_message}"
        )


def retry_assertion(assertion_func, retries=7, delay=30):
    """
    Retry an assertion function until it passes or the maximum number of retries is reached.

    Args:
        assertion_func: The assertion function to execute.
        retries: Maximum number of retries.
        delay: Delay (in seconds) between retries.

    Raises:
        AssertionError: If the assertion fails after all retries.
    """
    for attempt in range(1, retries + 1):
        try:
            assertion_func()
            return
        except AssertionError as e:
            if attempt < retries:
                logger.warning(f"Retry {attempt}/{retries} after failure: {e}")
                time.sleep(delay)
            else:
                raise AssertionError(f"Assertion failed after {retries} retries: {e}")


@given("the ETL ODS processor Lambda is configured with ODS mock")
def lambda_configured(
    lambda_with_ods_mock,
    context: Context,
    project,
    workspace,
    env,
):
    lambda_name, mock_manager = lambda_with_ods_mock
    context.lambda_name = lambda_name
    context.other["mock_manager"] = mock_manager
    context.other["mock_url"] = mock_manager.get_mock_endpoint_url()
    context.transform_lambda = get_resource_name(
        project, workspace, env, "etl-ods-transformer", "lambda"
    )
    context.crud_lambda = get_resource_name(
        project, workspace, env, "crud-apis-organisations", "lambda"
    )


@when("I trigger the Lambda with empty results scenario")
def trigger_lambda_empty_scenario(
    context: Context, aws_lambda_client: LambdaWrapper, ods_empty_payload_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_empty_payload_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with empty payload scenario")
def trigger_lambda_empty_payload(
    context: Context, aws_lambda_client: LambdaWrapper, ods_empty_payload_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_empty_payload_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with happy path scenario")
def trigger_lambda_happy_path(
    context: Context, aws_lambda_client: LambdaWrapper, ods_happy_path_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_happy_path_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with invalid data scenario")
def trigger_lambda_invalid_data(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_invalid_data_types_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_invalid_data_types_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with missing required fields scenario")
def trigger_lambda_missing_fields(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_missing_required_fields_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context,
        context.lambda_name,
        aws_lambda_client,
        ods_missing_required_fields_scenario,
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with extra unexpected field scenario")
def trigger_lambda_extra_field(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_extra_unexpected_field_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context,
        context.lambda_name,
        aws_lambda_client,
        ods_extra_unexpected_field_scenario,
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with request too old scenario")
def trigger_lambda_request_too_old(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_request_too_old_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_request_too_old_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with unauthorized scenario")
def trigger_lambda_unauthorized(
    context: Context, aws_lambda_client: LambdaWrapper, ods_unauthorized_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_unauthorized_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with server error scenario")
def trigger_lambda_server_error(
    context: Context, aws_lambda_client: LambdaWrapper, ods_server_error_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context, context.lambda_name, aws_lambda_client, ods_server_error_scenario
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with unknown resource type scenario")
def trigger_lambda_unknown_resource_type(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_unknown_resource_type_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context,
        context.lambda_name,
        aws_lambda_client,
        ods_unknown_resource_type_scenario,
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with an invalid ODS format")
def trigger_lambda_invalid_odscode_format(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_invalid_odscode_format_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context,
        context.lambda_name,
        aws_lambda_client,
        ods_invalid_odscode_format_scenario,
    )
    logger.info(f"lambda response: {context.lambda_response}")


@when("I trigger the Lambda with missing optional fields scenario")
def trigger_lambda_missing_optional_fields(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_missing_optional_fields_scenario: str,
):
    context.lambda_response = invoke_lambda_with_scenario(
        context,
        context.lambda_name,
        aws_lambda_client,
        ods_missing_optional_fields_scenario,
    )
    logger.info(f"lambda response: {context.lambda_response}")


@then("the Lambda should handle the validation error")
def verify_validation_error_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    validation_logs = [
        "Error processing organisation with ods_code",
        "Payload validation failed",
    ]
    assert context.lambda_response.get("statusCode") == 200
    found_validation_log = any(
        cloudwatch_logs.find_log_message(context.lambda_name, log_msg)
        for log_msg in validation_logs
    )
    logger.info(
        f"Validation scenario completed for lambda {context.lambda_name}, validation log found: {found_validation_log}"
    )


@then("the Lambda should process the organizations successfully")
def verify_successful_processing(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200, "Fetching ODS Data returned")


@then("the Lambda should handle empty results gracefully")
def verify_empty_results_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200, "ETL_EXTRACTOR_020")


@then("the Lambda should handle missing fields gracefully")
def verify_missing_fields_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(
        context, cloudwatch_logs, 200, "Error processing organisation"
    )


@then("the Lambda should handle unexpected fields gracefully")
def verify_unexpected_fields_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200, "messages to sqs queue")


@then("the Lambda should handle old requests gracefully")
def verify_old_requests_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200, "ETL_EXTRACTOR_020")


@then("the Lambda should handle upstream server errors")
def verify_server_errors_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(
        context,
        cloudwatch_logs,
        500,
        "ETL_COMMON_013",
        ["error", "failed", "exception"],
    )


@then("the Lambda should handle unknown resource types")
def verify_unknown_resource_types_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200, "ETL_EXTRACTOR_020")


@then("the Lambda should handle the authorization error")
def verify_authorization_error_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(
        context, cloudwatch_logs, 500, "ETL_COMMON_013", ["unauthorized"]
    )


@then("the Lambda should handle the invalid ODS format gracefully")
def verify_invalid_ods_format_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200)
    assert_cloudwatch_logs(
        lambda_name=context.transform_lambda,
        cloudwatch_logs=cloudwatch_logs,
        expected_log="FHIR_001",
    )


@then("the Lambda should handle missing optional fields gracefully")
def verify_missing_optional_fields_handled(
    context: Context, cloudwatch_logs: CloudWatchLogsWrapper
):
    assert_lambda_response(context, cloudwatch_logs, 200, "ETL_EXTRACTOR_002")


@then("the Transformer Lambda should transform the organisation data correctly")
def verify_message_sent_to_db(context: Context, cloudwatch_logs: CloudWatchLogsWrapper):
    assert_cloudwatch_logs(
        lambda_name=context.transform_lambda,
        cloudwatch_logs=cloudwatch_logs,
        expected_log="ETL_TRANSFORMER_026",
    )


@then("the extra unexpected fields should not be saved to DynamoDB")
def assert_details_match(model_repo: AttributeLevelRepository) -> None:
    def assertion():
        item = get_from_repo(model_repo, "befa3684-518d-4e67-a83e-978db11a539f")
        assert item, "No data found in repository"
        assert item.identifier_ODS_ODSCode == "Y01234", (
            "Mismatch in identifier_ODS_ODSCode"
        )
        assert item.name == "Test Practice With Extra Fields", "Mismatch in name"
        assert item.type == "GP Practice", "Mismatch in type"
        assert item.primary_role_code == "RO177", "Mismatch in primary_role_code"
        assert item.active is True, "Expected 'active' to be True"
        assert item.telecom == [], "Expected 'telecom' to be an empty list"
        # Legal dates check
        legal_dates = item.legalDates
        assert legal_dates is not None, "Expected legal_dates to exist"
        assert legal_dates.start == date(1974, 4, 1), (
            "Expected 'start' date to be '1974-04-01'"
        )
        assert legal_dates.end is None, "Expected 'end' date to be None"
        # Non-primary role code check
        assert "RO76" in item.non_primary_role_codes, (
            "Expected 'RO76' to be present in non_primary_role_codes"
        )

    retry_assertion(assertion)


@then("the organisation data should be updated in DynamoDB")
def assert_org_details_match(model_repo: AttributeLevelRepository) -> None:
    def assertion():
        item = get_from_repo(model_repo, "befa3684-518d-4e67-a83e-978db11a539f")
        assert item, "No data found in repository"
        assert item.identifier_ODS_ODSCode == "Y01234", (
            "Mismatch in identifier_ODS_ODSCode"
        )
        assert item.name == "Test Medical Centre", "Mismatch in name"
        assert item.type == "GP Practice", "Mismatch in type"
        assert item.primary_role_code == "RO177", "Mismatch in primary_role_code"
        assert item.active is True, "Expected 'active' to be True"
        # Telecom assertions
        telecom = item.telecom
        assert telecom, "telecom list is empty"
        assert isinstance(telecom, list), "telecom should be a list"
        assert len(telecom) > 0, "Expected at least one telecom entry"
        telecom_entry = telecom[0]
        assert telecom_entry.isPublic is True, "Expected 'isPublic' to be True"
        assert telecom_entry.type == "phone", "Expected 'type' to be 'phone'"
        assert telecom_entry.value == "01252 723326", (
            "Expected 'value' to be '01252 723326'"
        )
        # Legal dates check
        legal_dates = item.legalDates
        assert legal_dates is not None, "Expected legal_dates to exist"
        assert legal_dates.start == date(1974, 4, 1), (
            "Expected 'start' date to be '1974-04-01'"
        )
        assert legal_dates.end is None, "Expected 'end' date to be None"

        # Non-primary role code check
        assert "RO76" in item.non_primary_role_codes, (
            "Expected 'RO76' to be present in non_primary_role_codes"
        )
        retry_assertion(assertion)


@then("the telecom data should be updated in DynamoDB")
def assert_telecom_details_match(model_repo: AttributeLevelRepository) -> None:
    def assertion():
        item = get_from_repo(model_repo, "befa3684-518d-4e67-a83e-978db11a539f")
        assert item, "No data found in repository"
        assert item.identifier_ODS_ODSCode == "Y01234", (
            "Mismatch in identifier_ODS_ODSCode"
        )
        assert item.name == "Test Medical Centre", "Mismatch in name"
        assert item.type == "GP Practice", "Mismatch in type"
        assert item.primary_role_code == "RO177", "Mismatch in primary_role_code"
        assert item.active is True, "Expected 'active' to be True"
        assert item.telecom == [], "Expected 'telecom' to be an empty list"
        # Legal dates check
        legal_dates = item.legalDates
        assert legal_dates is not None, "Expected legal_dates to exist"
        assert legal_dates.start == date(1974, 4, 1), (
            "Expected 'start' date to be '1974-04-01'"
        )
        assert legal_dates.end is None, "Expected 'end' date to be None"

        # Non-primary role code check
        assert "RO76" in item.non_primary_role_codes, (
            "Expected 'RO76' to be present in non_primary_role_codes"
        )

    retry_assertion(assertion)
