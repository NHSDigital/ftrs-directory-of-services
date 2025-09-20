import boto3
from botocore.exceptions import ClientError
from loguru import logger

class ApiGatewayToService:
    """
    Encapsulates Amazon API Gateway functions that are used to create a REST API that
    integrates with another AWS service.
    """

    def __init__(self):
        """
        :param apig_client: A Boto3 API Gateway client.
        """

        self.apig_client = boto3.client("apigateway")
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
                    (item for item in page['items'] if item['name'] == api_name), None
                )
                if rest_api is not None:
                    break
            self.api_id = rest_api['id']
        except ClientError:
            logger.info("Couldn't find ID for API %s.", api_name)
            raise
        else:
            return rest_api['id']
