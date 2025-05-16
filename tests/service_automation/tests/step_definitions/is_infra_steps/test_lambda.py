import pytest
import boto3
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


@then(parsers.parse('the lambda response contains the ods code "{odscode}"'))
def lambda_response_message(fLambda_payload, odscode):
    logger.debug("Checking for ods code {} in lambda response: {}", odscode, fLambda_payload)
    assert fLambda_payload["statusCode"] == 200
    assert odscode in fLambda_payload["body"]

