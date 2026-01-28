import json
import pytest
from pytest_bdd import given, scenarios, then, when
from loguru import logger
import uuid
from ftrs_data_layer.domain import DBModel, Organisation
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from utilities.common.context import Context
from utilities.infra.lambda_util import LambdaWrapper
from datetime import datetime, date
from utilities.infra.logs_util import get_logs
from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.setup_steps import *  # noqa: F403

from utilities.ods.scenario_manager import (
    ods_empty_payload_scenario,
    ods_invalid_data_types_scenario,
    ods_missing_required_fields_scenario,
    ods_extra_unexpected_field_scenario,
    ods_request_too_old_scenario,
    ods_unauthorized_scenario,
    ods_unknown_resource_type_scenario,
    ods_server_error_scenario,
    ods_happy_path_scenario,
    ods_missing_optional_fields_scenario,
    ods_invalid_odscode_format_scenario,
    ScenarioManager,
)

scenarios("./etl_ods_features/etl_ods_mock.feature")


def get_from_repo(
    model_repo: AttributeLevelRepository, model_id: str
) -> ModelType | None:
    logger.debug(f"Fetching record with ID: {model_id}")
    item = model_repo.get(model_id)
    if item is None:
        logger.error(f"No data found for model ID: {model_id}")
    return item


def generic_lambda_log_check_function(
    context: Context, lambda_name: str, field: str, message: str
) -> None:
    """Assert the lambda log contains the expected message filtered by correlation_id."""
    field = field if field else "message"
    expected_message = message
    correlation_id = (
        context.correlation_id.replace("/", r"\/") if context.correlation_id else ""
    )
    start_time = (
        int(context.lambda_invocation_time.timestamp() * 1000)
        if context.lambda_invocation_time
        else None
    )
    query = (
        f"fields @timestamp, @message, correlation_id, {field} "
        f'| filter correlation_id = "{correlation_id}" '
        f'| filter {field} = "{expected_message}" '
        f"| sort @timestamp desc"
    )
    logs = get_logs(query=query, lambda_name=lambda_name, start_time=start_time)
    logger.info(f"Checking logs for Lambda: {lambda_name}")
    logger.info(f"Logs retrieved: {logs}")
    assert message in logs, (
        f"ERROR!!.. '{lambda_name}' logs did not contain the expected message: '{message}' "
        f"for correlation_id '{context.correlation_id}'."
    )


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
    context: Context,
    lambda_name: str,
    aws_lambda_client: LambdaWrapper,
    scenario_date: str,
) -> dict:
    context.lambda_invocation_time = datetime.utcnow()
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


@given("the ETL ODS processor Lambda is configured with ODS mock")
def lambda_configured(lambda_with_ods_mock, context: Context):
    lambda_name, mock_manager = lambda_with_ods_mock
    context.lambda_name = lambda_name
    logger.info(f"Lambda configured for testing: {context.lambda_name}")
    mock_url = mock_manager.get_mock_endpoint_url()
    context.other["mock_manager"] = mock_manager
    context.other["mock_url"] = mock_url


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
def verify_validation_error_handled(context: Context):
    """Verify Lambda detected and handled invalid data."""
    # Check for validation error logging
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "FHIR_001"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Lambda should process the organizations successfully")
def verify_successful_processing(context: Context):
    """Verify Lambda successfully processed organizations from happy path."""
    expected_log = "ETL_PROCESSOR_002"
    assert context.lambda_response.get("statusCode") == 200
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )
    body = context.lambda_response.get("body", "")
    if isinstance(body, str) and body != "Processing complete":
        try:
            parsed_body = json.loads(body) if isinstance(body, str) else body
            assert "error" not in str(parsed_body).lower()
        except json.JSONDecodeError:
            pass


@then("the Lambda should handle empty results gracefully")
def verify_empty_results_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "ETL_PROCESSOR_020"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Lambda should handle missing fields gracefully")
def verify_missing_fields_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "ETL_PROCESSOR_027"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Lambda should handle unexpected fields gracefully")
def verify_unexpected_fields_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "ETL_PROCESSOR_026"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the message should be sent to the queue successfully")
def verify_unexpected_fields_handled(context: Context):
    expected_log = "ETL_PROCESSOR_014"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Consumer should log the successful processing of the request")
def verify_unexpected_fields_handled(context: Context):
    expected_log = "ETL_CONSUMER_007"
    generic_lambda_log_check_function(
        context, "etl-ods-consumer-lambda", "reference", expected_log
    )


@then("the CRUD API should log the update request for the organisation")
def verify_unexpected_fields_handled(context: Context):
    expected_log = "ORGANISATION_008"
    generic_lambda_log_check_function(
        context, "crud-apis-organisations-lambda", "reference", expected_log
    )


@then("the Lambda should handle old requests gracefully")
def verify_old_requests_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "ETL_PROCESSOR_020"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Lambda should handle upstream server errors")
def verify_server_errors_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 500
    expected_log = "ETL_UTILS_003"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )
    error_message = extract_error_message(context.lambda_response)
    assert any(
        keyword in error_message.lower() for keyword in ["error", "failed", "exception"]
    )


@then("the Lambda should handle unknown resource types")
def verify_unknown_resource_types_handled(context: Context):
    """Verify Lambda handles unknown resource types by filtering them out (resulting in empty results)."""
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "ETL_PROCESSOR_020"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Lambda should handle the authorization error")
def verify_authorization_error_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 500
    expected_log = "ETL_UTILS_003"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )
    error_message = extract_error_message(context.lambda_response)
    assert "unauthorized" in error_message.lower(), f"{error_message}"


@then("the Lambda should handle the invalid ODS format gracefully")
def verify_invalid_ods_format_handled(context: Context):
    """Verify Lambda detected and handled invalid data."""
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "FHIR_001"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the Lambda should handle missing optional fields gracefully")
def verify_missing_optional_fields_handled(context: Context):
    assert context.lambda_response.get("statusCode") == 200
    expected_log = "ETL_PROCESSOR_026"
    generic_lambda_log_check_function(
        context, "etl-ods-processor-lambda", "reference", expected_log
    )


@then("the extra unexpected fields should not be saved to DynamoDB")
def assert_details_match(model_repo: AttributeLevelRepository) -> None:
    item = get_from_repo(model_repo, "befa3684-518d-4e67-a83e-978db11a539f")
    assert item, "No data found in repository"
    assert item.identifier_ODS_ODSCode == "Y01234", "Mismatch in identifier_ODS_ODSCode"
    assert item.name == "Test Practice With Extra Fields", "Mismatch in name"
    assert item.type == "GP Practice", "Mismatch in type"
    assert item.primary_role_code == "RO177", "Mismatch in primary_role_code"
    assert item.active is True, "Expected 'active' to be True"
    assert item.telecom == [], "Expected 'telecom' to be an empty list"
    # Legal dates check
    legal_dates = item.legalDates
    assert legal_dates and legal_dates.start == date(1974, 4, 1), (
        "Expected 'start' date to be '1974-04-01'"
    )
    assert legal_dates.end is None, "Expected 'end' date to be None"
    # Non-primary role code check
    assert "RO76" in item.non_primary_role_codes, (
        "Expected 'RO76' to be present in non_primary_role_codes"
    )


@then("the organisation data should be updated in DynamoDB")
def assert_org_details_match(model_repo: AttributeLevelRepository) -> None:
    item = get_from_repo(model_repo, "befa3684-518d-4e67-a83e-978db11a539f")
    assert item, "No data found in repository"
    assert item.identifier_ODS_ODSCode == "Y01234", "Mismatch in identifier_ODS_ODSCode"
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
    assert legal_dates.start == date(1974, 4, 1), (
        "Expected 'start' date to be '1974-04-01'"
    )
    assert legal_dates.end is None, "Expected 'end' date to be None"

    # Non-primary role code check
    assert "RO76" in item.non_primary_role_codes, (
        "Expected 'RO76' to be present in non_primary_role_codes"
    )


@then("the telecom data should remain unchanged in DynamoDB")
def assert_telecom_details_match(model_repo: AttributeLevelRepository) -> None:
    item = get_from_repo(model_repo, "befa3684-518d-4e67-a83e-978db11a539f")
    assert item, "No data found in repository"
    assert item.identifier_ODS_ODSCode == "Y01234", "Mismatch in identifier_ODS_ODSCode"
    assert item.name == "Test Medical Centre", "Mismatch in name"
    assert item.type == "GP Practice", "Mismatch in type"
    assert item.primary_role_code == "RO177", "Mismatch in primary_role_code"
    assert item.active is True, "Expected 'active' to be True"
    assert item.telecom == [], "Expected 'telecom' to be an empty list"
    # Legal dates check
    legal_dates = item.legalDates
    assert legal_dates.start == date(1974, 4, 1), (
        "Expected 'start' date to be '1974-04-01'"
    )
    assert legal_dates.end is None, "Expected 'end' date to be None"

    # Non-primary role code check
    assert "RO76" in item.non_primary_role_codes, (
        "Expected 'RO76' to be present in non_primary_role_codes"
    )
