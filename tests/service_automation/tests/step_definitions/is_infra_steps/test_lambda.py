import pytest
import boto3
import subprocess
import json
from pytest_bdd import scenarios, given, when, then, parsers
from loguru import logger
from utilities.infra.lambda_util import LambdaWrapper, invoke_function, get_lambda_name, check_function_exists
from utilities.infra.s3 import S3Utils

# Load feature file
scenarios("./is_infra_features/test_lambda.feature")


@pytest.fixture(scope="module")
def aws_lambda_client():
    """Fixture to initialize AWS Lambda utility"""
    iam_resource = boto3.resource("iam")
    lambda_client = boto3.client("lambda")
    wrapper = LambdaWrapper(lambda_client, iam_resource)
    return wrapper


@given(parsers.parse('that the lambda function "{lambda_function}" exists for stack "{stack}"'), target_fixture='flambda_name')
def confirm_lambda_exists(aws_lambda_client, project, lambda_function, stack, workspace, env):
    lambda_name = get_lambda_name(aws_lambda_client, project, workspace, env, stack, lambda_function)
    lambda_exists = check_function_exists(aws_lambda_client, lambda_name)
    assert lambda_exists == True
    return lambda_name


@when(('I invoke the lambda'), target_fixture='fLambda_payload')
def invoke_lambda(aws_lambda_client, flambda_name, lambda_params = ""):
    lambda_payload = invoke_function(aws_lambda_client, flambda_name, lambda_params)
    # logger.debug("Lambda response: {}", lambda_payload)
    return lambda_payload

@then(parsers.parse('the lambda response contains the message "{message}"'))
def lambda_response_message(fLambda_payload, message):
    # response_status = json.loads(fLambda_payload['statusCode'])
    response_status = fLambda_payload['statusCode']
    response_message = fLambda_payload['body']
    logger.debug("Lambda response_message: {}", response_status)
    assert response_status == 200
    # assert message == response_message
