import json
from botocore.exceptions import ClientError
from loguru import logger


class LambdaWrapper:
    def __init__(self, lambda_client, iam_resource):
        self.lambda_client = lambda_client
        self.iam_resource = iam_resource


    def get_function(self, function_name):
        response = None
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.debug("Function {} does not exist.", function_name)
            else:
                logger.debug("Couldn't get function {} Here's why: {}: {}",
                    function_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],)
                raise
        return response


    def invoke_function(self, function_name, function_params, get_log=False):
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(function_params)
            )
            logger.debug("Invoked function {}.", function_name)
            payload = json.loads(response['Payload'].read().decode())
        except ClientError:
            logger.debug("Couldn't invoke function {}.", function_name)
            raise
        return payload


    def get_lambda_name(self, project, workspace, env, stack, lambda_function):
        logger.info(f"project: {project},  lambda_function: {lambda_function}, stack: {stack}, env: {env}, workspace: {workspace}")
        if workspace == "default":
            lambda_name = project + "-" + env + "-" + stack + "-" + lambda_function
        else:
            lambda_name = project + "-" + env + "-" + stack + "-" + lambda_function + "-" + workspace
        logger.info("lambda name {}", lambda_name)
        return lambda_name


    def check_function_exists(self, lambda_name):
        try:
            self.get_function(lambda_name)
            exists = True
        except Exception:
            logger.error("Error: function not found")
            exists = False
        return exists
