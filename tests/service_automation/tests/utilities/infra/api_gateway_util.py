import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from loguru import logger


class ApiGatewayToService:
    """Encapsulates Amazon API Gateway functions.

    Supports both real AWS and LocalStack for testing.

    Args:
        endpoint_url: Optional endpoint URL for LocalStack or other compatible services.
                     If not provided, checks AWS_ENDPOINT_URL environment variable,
                     then falls back to real AWS.
    """

    def __init__(self, endpoint_url: Optional[str] = None):
        endpoint = endpoint_url or os.environ.get("AWS_ENDPOINT_URL")
        client_kwargs = {}
        if endpoint:
            client_kwargs["endpoint_url"] = endpoint
            logger.debug(f"Using API Gateway endpoint: {endpoint}")

        self.apig_client = boto3.client("apigateway", **client_kwargs)
        self.api_id = None
        self.root_id = None
        self.stage = None

    def get_rest_api_id(self, api_name):
        """
        Gets the ID of a REST API from its name by searching the list of REST APIs
        for the current account. Because names need not be unique, this returns only
        the first API with the specified name.

        :param api_name: The name of the API to look up.
        :return: The ID of the specified API.
        """
        try:
            rest_api = None
            paginator = self.apig_client.get_paginator("get_rest_apis")
            for page in paginator.paginate():
                rest_api = next(
                    (item for item in page["items"] if item["name"] == api_name), None
                )
                if rest_api is not None:
                    break
            self.api_id = rest_api["id"]
        except ClientError:
            logger.info("Couldn't find ID for API %s.", api_name)
            raise
        else:
            return rest_api["id"]
