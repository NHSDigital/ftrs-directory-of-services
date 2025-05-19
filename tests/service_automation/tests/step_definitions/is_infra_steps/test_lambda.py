import pytest
import boto3
import json
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra.lambda_util import LambdaWrapper

# Load feature file
scenarios("./is_infra_features/lambda.feature")


@pytest.fixture(scope="module")
def aws_lambda_client():
    """Fixture to initialize AWS Lambda utility"""
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    wrapper = LambdaWrapper(lambda_client, iam_resource)
    return wrapper


@given(parsers.parse('that the lambda function "{lambda_function}" exists for stack "{stack}"'), target_fixture='flambda_name')
def confirm_lambda_exists(aws_lambda_client, project, lambda_function, stack, workspace, env):
    lambda_name = aws_lambda_client.get_lambda_name(project, workspace, env, stack, lambda_function)
    lambda_exists = aws_lambda_client.check_function_exists(lambda_name)
    assert lambda_exists is True
    return lambda_name


@when(parsers.parse('I invoke the lambda with the ods code "{odscode}"'), target_fixture='fLambda_payload')
def invoke_lambda(aws_lambda_client, odscode, flambda_name):
    lambda_params = {
        "odsCode": odscode
    }
    lambda_payload = aws_lambda_client.invoke_function(flambda_name, lambda_params)
    return lambda_payload


@when(('I invoke the lambda with the ods code value not set'), target_fixture='fLambda_payload')
def invoke_lambda_no_odscode(aws_lambda_client, flambda_name):
    lambda_params = {
        "odsCode": ""
    }
    lambda_payload = aws_lambda_client.invoke_function(flambda_name, lambda_params)
    return lambda_payload


@when(('I invoke the lambda with an empty event'), target_fixture='fLambda_payload')
def invoke_lambda_empty_event(aws_lambda_client, flambda_name):
    lambda_params = {
    }
    lambda_payload = aws_lambda_client.invoke_function(flambda_name, lambda_params)
    return lambda_payload


@then(parsers.parse('the lambda response contains the ods code "{odscode}"'))
def lambda_ods_code(fLambda_payload, odscode):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["entry"][0]["resource"]["identifier"][0]["system"] =="https://fhir.nhs.uk/Id/ods-organization-code" and \
        response["entry"][0]["resource"]["identifier"][0]["value"] == odscode


@then(parsers.parse('the lambda response contains an empty bundle'))
def lambda_empty_response(fLambda_payload):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["entry"] == []


@then(parsers.parse('the lambda returns the error message "{error_message}" with status code "{status_code}"'))
def lambda_error_message(fLambda_payload, error_message, status_code):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 500
    assert response["issue"][0]["details"]["coding"][0]["code"] == "INTERNAL_SERVER_ERROR" and \
    response["issue"][0]["details"]["coding"][0]["display"] == error_message


@then('the lambda response does not contain an endpoint resource')
def lambda_no_endpoints(fLambda_payload):
    response = json.loads(fLambda_payload["body"])
    # Check if any entry in response has a resourceType of "Endpoint"
    endpoint_exists = any(
        entry.get("resource", {}).get("resourceType") == "Endpoint"
        for entry in response.get("entry", [])
    )
    assert fLambda_payload["statusCode"] == 200
    assert len(response["entry"]) == 1
    assert endpoint_exists is False


