import json

import boto3
import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from step_definitions.common_steps.data_steps import *  # noqa: F403
from utilities.common.resource_name import get_resource_name
from utilities.infra.lambda_util import LambdaWrapper

# Load feature file
scenarios("./infra_features/dos-search-lambda.feature")

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


@then('the lambda response contains a bundle')
def lambda_check_bundle(fLambda_payload):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert response["resourceType"] == "Bundle"


@then(parsers.parse('the lambda response contains "{number}" "{resource_type}" resources'))
def lambda_number_resources(fLambda_payload, number, resource_type):
    response = json.loads(fLambda_payload["body"])
    assert fLambda_payload["statusCode"] == 200
    assert count_resources(response, resource_type) == int(number)


def count_resources(lambda_response, resource_type):
    return sum(
        entry.get("resource", {}).get("resourceType") == resource_type
        for entry in lambda_response.get("entry", [])
        )


def create_lambda_params(odscode):
    return {
        "version": "2.0",
        "rawPath": "/Organization",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{odscode}",
            "_revinclude": "Endpoint:organization",
        },
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
            "stage": "$default",
            "http": {
                "method": "GET",
            },
        },
        "body": None,
    }
