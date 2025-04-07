from functools import cache

import boto3
from mypy_boto3_dynamodb import DynamoDBClient, DynamoDBServiceResource


@cache
def get_dynamodb_client(
    endpoint_url: str | None = None,
) -> DynamoDBClient:
    """
    Cached DynamoDB client for accessing the DynamoDB service.
    """
    return boto3.client("dynamodb", endpoint_url=endpoint_url)


@cache
def get_dynamodb_resource(
    endpoint_url: str | None = None,
) -> DynamoDBServiceResource:
    """
    Cached DynamoDB client for accessing the DynamoDB service.
    """
    return boto3.resource("dynamodb", endpoint_url=endpoint_url)
