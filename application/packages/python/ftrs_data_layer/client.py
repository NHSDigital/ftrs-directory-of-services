from functools import cache

import boto3
from mypy_boto3_dynamodb import DynamoDBClient, DynamoDBServiceResource


@cache
def get_dynamodb_client(
    endpoint_url: str | None = None,
    region_name: str = "eu-west-2",
) -> DynamoDBClient:
    """
    Cached DynamoDB client for accessing the DynamoDB service.
    """
    return boto3.client("dynamodb", endpoint_url=endpoint_url, region_name=region_name)


@cache
def get_dynamodb_resource(
    endpoint_url: str | None = None,
    region_name: str = "eu-west-2",
) -> DynamoDBServiceResource:
    """
    Cached DynamoDB client for accessing the DynamoDB service.
    """
    return boto3.resource(
        "dynamodb", endpoint_url=endpoint_url, region_name=region_name
    )
