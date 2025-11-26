import json
import pytest
from pytest_bdd import given, scenarios, then, when
from loguru import logger

from utilities.common.context import Context
from utilities.infra.lambda_util import LambdaWrapper
from utilities.ods.scenario_manager import (
    ods_empty_payload_scenario,
    ods_invalid_data_types_scenario,
    ods_unauthorized_scenario
)

scenarios("./etl_ods_features/etl_ods_mock.feature")


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
    lambda_name: str,
    aws_lambda_client: LambdaWrapper,
    scenario_date: str
) -> dict:
    """
    Helper to invoke Lambda with a scenario date.
    The scenario date (e.g., "2024-01-01") is passed as the 'date' parameter,
    which the Lambda validates and then uses as the _lastUpdated query parameter.
    The VTL mock maps specific dates to test scenarios.
    """
    event = {"date": scenario_date}

    response = aws_lambda_client.lambda_client.invoke(
        FunctionName=lambda_name,
        Payload=json.dumps(event)
    )

    result = json.loads(response["Payload"].read())
    logger.info(f"Lambda response for date {scenario_date}: {json.dumps(result, indent=2)}")
    return result


@given("the ETL ODS processor Lambda is configured with VTL mock")
def lambda_configured(lambda_with_vtl_mock, context: Context):
    """Lambda environment points to VTL mock API Gateway."""
    lambda_name, mock_manager = lambda_with_vtl_mock
    context.lambda_name = lambda_name

    mock_details = mock_manager.get_mock_details()
    context.other['mock_manager'] = mock_manager
    context.other['mock_url'] = mock_details['endpoint_url']


@when("I trigger the Lambda with empty results scenario")
def trigger_lambda_empty_scenario(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_empty_payload_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name,
        aws_lambda_client,
        ods_empty_payload_scenario
    )


@when("I trigger the Lambda with invalid data scenario")
def trigger_lambda_invalid_data(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_invalid_data_types_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name,
        aws_lambda_client,
        ods_invalid_data_types_scenario
    )


@when("I trigger the Lambda with unauthorized scenario")
def trigger_lambda_unauthorized(
    context: Context,
    aws_lambda_client: LambdaWrapper,
    ods_unauthorized_scenario: str
):
    context.lambda_response = invoke_lambda_with_scenario(
        context.lambda_name,
        aws_lambda_client,
        ods_unauthorized_scenario
    )

@then("the Lambda should handle the validation error")
def verify_validation_error_handled(context: Context):
    """Verify Lambda detected and handled invalid data."""
    assert context.lambda_response.get("statusCode") == 200


@then("the Lambda should handle the authorization error")
def verify_authorization_error_handled(context: Context):
    """Verify Lambda detected and handled 401 error from ODS."""
    assert context.lambda_response.get("statusCode") == 500
    error_message = extract_error_message(context.lambda_response)
    assert "unauthorized" in error_message.lower(), f"{error_message}"
