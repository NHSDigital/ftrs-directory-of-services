import json
import os
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError
from loguru import logger


def create_lambda_client(endpoint_url: Optional[str] = None) -> Any:
    """Create a Lambda client, optionally configured for LocalStack.

    Args:
        endpoint_url: Optional endpoint URL for LocalStack or other compatible services.
                     If not provided, checks AWS_ENDPOINT_URL environment variable,
                     then falls back to real AWS.

    Returns:
        Boto3 Lambda client
    """
    endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
    client_kwargs = {"region_name": "eu-west-2"}
    if endpoint:
        client_kwargs["endpoint_url"] = endpoint
        logger.debug(f"Using Lambda endpoint: {endpoint}")
    return boto3.client("lambda", **client_kwargs)


def create_iam_resource(endpoint_url: Optional[str] = None) -> Any:
    """Create an IAM resource, optionally configured for LocalStack.

    Args:
        endpoint_url: Optional endpoint URL for LocalStack or other compatible services.
                     If not provided, checks AWS_ENDPOINT_URL environment variable,
                     then falls back to real AWS.

    Returns:
        Boto3 IAM resource
    """
    endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
    resource_kwargs = {"region_name": "eu-west-2"}
    if endpoint:
        resource_kwargs["endpoint_url"] = endpoint
        logger.debug(f"Using IAM endpoint: {endpoint}")
    return boto3.resource("iam", **resource_kwargs)


class LambdaWrapper:
    """Lambda wrapper that supports both real AWS and LocalStack.

    Args:
        lambda_client: Boto3 Lambda client (if None, creates one using endpoint_url)
        iam_resource: Boto3 IAM resource (if None, creates one using endpoint_url)
        endpoint_url: Optional endpoint URL for LocalStack. Only used if lambda_client
                     or iam_resource are not provided.
    """

    def __init__(
        self,
        lambda_client: Optional[Any] = None,
        iam_resource: Optional[Any] = None,
        endpoint_url: Optional[str] = None,
    ):
        self.lambda_client = lambda_client or create_lambda_client(endpoint_url)
        self.iam_resource = iam_resource or create_iam_resource(endpoint_url)

    def get_function(self, function_name):
        response = None
        try:
            response = self.lambda_client.get_function(FunctionName=function_name)
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.debug("Function {} does not exist.", function_name)
            else:
                logger.debug(
                    "Couldn't get function {} Here's why: {}: {}",
                    function_name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
        return response

    def invoke_function(self, function_name, function_params, get_log=False):
        try:
            response = self.lambda_client.invoke(
                FunctionName=function_name, Payload=json.dumps(function_params)
            )
            logger.debug("Invoked function {}.", function_name)
            payload = json.loads(response["Payload"].read().decode())
        except ClientError:
            logger.debug("Couldn't invoke function {}.", function_name)
            raise
        return payload

    def check_function_exists(self, lambda_name):
        try:
            self.get_function(lambda_name)
            exists = True
        except Exception:
            logger.error("Error: function not found")
            exists = False
        return exists
