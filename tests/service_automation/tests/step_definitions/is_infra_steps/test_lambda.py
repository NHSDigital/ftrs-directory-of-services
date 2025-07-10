import json

import boto3
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from utilities.common.resource_name import get_resource_name
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
    lambda_name = get_resource_name(project, workspace, env, stack, lambda_function)
    lambda_exists = aws_lambda_client.check_function_exists(lambda_name)
    assert lambda_exists is True
    return lambda_name

@when(parsers.re(r'I invoke the lambda with the ods code "(?P<odscode>.*)"'), target_fixture='fLambda_payload')
def invoke_lambda(aws_lambda_client, odscode, flambda_name):
    lambda_params = create_lambda_params(odscode)
    lambda_payload = aws_lambda_client.invoke_function(flambda_name, lambda_params)
    return lambda_payload


@when('I invoke the lambda with an empty event', target_fixture='fLambda_payload')
def invoke_lambda_empty_event(aws_lambda_client, flambda_name):
    lambda_params = {
    }
    lambda_payload = aws_lambda_client.invoke_function(flambda_name, lambda_params)
    return lambda_payload


@then(parsers.parse('the lambda response contains the ods code "{odscode}"'))
def lambda_ods_code(fLambda_payload, odscode):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["entry"][0]["resource"]["identifier"][0]["system"] =="https://fhir.nhs.uk/Id/ods-organization-code"
    assert response["entry"][0]["resource"]["identifier"][0]["value"] == odscode

@then(parsers.parse('the lambda response contains the endpoint id "{endpoint_id}"'))
def lambda_endpoint_id(fLambda_payload, endpoint_id):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["entry"][1]["resource"]["resourceType"] == "Endpoint"
    assert response["entry"][1]["resource"]["id"] == endpoint_id

@then(parsers.parse('the lambda response contains an empty bundle'))
def lambda_empty_response(fLambda_payload):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["entry"] == []


@then(parsers.parse('the lambda returns the error code "{error_code}"'))
def lambda_error_code(fLambda_payload, error_code):
    response = json.loads(fLambda_payload["body"])
    assert response["issue"][0]["details"]["coding"][0]["code"] == error_code


@then(parsers.parse('the lambda returns the status code "{status_code}"'))
def lambda_status_code(fLambda_payload, status_code):
    assert fLambda_payload["statusCode"] == int(status_code)


@then(parsers.parse('the lambda returns the message "{error_message}"'))
def lambda_error_message(fLambda_payload, error_message):
    response = json.loads(fLambda_payload["body"])
    assert response["issue"][0]["details"]["text"] == error_message


@then(parsers.parse('the lambda returns the diagnostics "{diagnostics}"'))
def lambda_diagnostics(fLambda_payload, diagnostics):
    response = json.loads(fLambda_payload["body"])
    assert response["issue"][0]["diagnostics"] == diagnostics


@then('the lambda response contains a bundle')
def lambda_check_bundle(fLambda_payload):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["resourceType"] == "Bundle"


@then(parsers.parse('the lambda response contains "{number}" "{resource_type}" resources'))
def lambda_number_resources(fLambda_payload, number, resource_type):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert countResources(response, resource_type) == int(number)


def countResources(lambda_response, resource_type):
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
        )

def create_lambda_params(odscode):
    return {
        "path": "/organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{odscode}",
            "_revinclude": "Endpoint:organization",
        },
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "body": None,
    }
