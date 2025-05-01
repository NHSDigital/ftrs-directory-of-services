import json
from botocore.exceptions import ClientError
from loguru import logger

class LambdaWrapper:
    def __init__(self, lambda_client, iam_resource):
        self.lambda_client = lambda_client
        self.iam_resource = iam_resource


def get_function(self, function_name):
        """
        Gets data about a Lambda function.

        :param function_name: The name of the function.
        :return: The function data.
        """
        response = None
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                print("Function {} does not exist.", function_name)
                logger.debug("Function{} does not exist.", function_name)
            else:
                logger.debug("Couldn't get function {} Here's why: {}: {}",
                    function_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],)
                raise
        return response


def invoke_function(self, function_name, function_params, get_log=False):
    """
    Invokes a Lambda function.

    :param function_name: The name of the function to invoke.
    :param function_params: The parameters of the function as a dict. This dict
                            is serialized to JSON before it is sent to Lambda.
    :param get_log: When true, the last 4 KB of the execution log are included in
                    the response.
    :return: The response from the function invocation.
    """
    try:
        response = self.lambda_client.invoke(
            FunctionName=function_name,
            Payload=json.dumps(function_params).encode('utf-8'),
            LogType="Tail" if get_log else "None",
        )
        logger.debug("Invoked function {}.", function_name)
        payload = json.loads(response['Payload'].read().decode())
        logger.debug("Payload {}.", payload)
    except ClientError:
        logger.debug("Couldn't invoke function {}.", function_name)
        raise
    return payload


def get_lambda_name(self, project, workspace, env, stack, lambda_function):
    logger.debug(f"project: {project},  lambda_function: {lambda_function}, stack: {stack}, env: {env}, workspace: {workspace}")
    if workspace == "":
        lambda_name = project + "-" + env + "-" + stack + "-" + lambda_function
    else:
        lambda_name = project + "-" + env + "-" + stack + "-" + lambda_function + "-" + workspace
    logger.debug("lambda name {}", lambda_name)
    return lambda_name


def check_function_exists(self, lambda_name):
    """
    Determine whether the lambda function exists and you have access to it.
    :return: True when the lambda function exists; otherwise, False.
    """
    try:
        get_function(self, lambda_name)
        exists = True
    except Exception:
        logger.error("Error: bucket not found")
        exists = False
    return exists
