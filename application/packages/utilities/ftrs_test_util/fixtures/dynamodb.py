import pytest
from testcontainers.localstack import LocalStackContainer
from typing import Generator, Any
from ftrs_test_util.settings import TestSettings
import boto3
from mypy_boto3_dynamodb import DynamoDBClient
from itertools import batched
from ftrs_test_util.table_config import get_dynamodb_table_configs


@pytest.fixture(scope="function")
def dynamodb_client(
    localstack_container: LocalStackContainer,
) -> Generator[DynamoDBClient, None, None]:
    """
    Provides the DynamoDB endpoint URL from the LocalStack container.
    """
    settings = TestSettings()

    if settings.existing_dynamodb_endpoint is not None:
        client = boto3.client(
            "dynamodb",
            endpoint_url=settings.existing_dynamodb_endpoint,
            region_name="eu-west-2",
        )
    else:
        client = localstack_container.get_client("dynamodb")

    try:
        reset_dynamodb_tables(client, settings)
        yield client
    finally:
        reset_dynamodb_tables(client, settings)


@pytest.fixture(scope="function")
def dynamodb_endpoint(dynamodb_client: DynamoDBClient) -> str:
    """
    Provides the DynamoDB endpoint URL from the LocalStack container.
    """
    return dynamodb_client.meta.endpoint_url


def reset_dynamodb_tables(client: DynamoDBClient, settings: TestSettings) -> None:
    """
    Sets up the DynamoDB tables in LocalStack before tests run.

    If the table already exists, it will be left as is. This is a no-op if the tables are
    already created by the testcontainers fixture.
    """

    table_configs = get_dynamodb_table_configs(
        include_core=True,
        include_triage_code=True,
        include_data_migration_state=True,
        environment=settings.environment,
        workspace=settings.workspace,
    )

    for config in table_configs:
        table_name = config["TableName"]
        key_schema = get_key_schema(client, table_name)

        if not key_schema:
            create_dynamodb_table(client, config)
        else:
            clear_dynamodb_table(client, table_name, key_schema)


def get_key_schema(
    client: DynamoDBClient, table_name: str
) -> list[dict[str, str]] | None:
    """
    Get the key schema of a DynamoDB table.

    Args:
        table_name: Name of the DynamoDB table

    Returns:
        List of key schema elements (AttributeName and KeyType)
    """
    try:
        response = client.describe_table(TableName=table_name)
        return response["Table"]["KeySchema"]
    except client.exceptions.ResourceNotFoundException:
        return None


def create_dynamodb_table(
    client: DynamoDBClient,
    config: dict[str, Any],
) -> None:
    """
    Create a DynamoDB table based on the provided configuration.

    Args:
        client: Boto3 DynamoDB client
        config: Table configuration dictionary

    Raises:
        Exception: If table creation fails
    """
    client.create_table(**config)
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=config["TableName"])


def clear_dynamodb_table(
    client: DynamoDBClient,
    table_name: str,
    key_schema: list[dict[str, str]],
) -> None:
    """
    Delete all items from a DynamoDB table without dropping the table.

    This is faster than dropping and recreating the table when you need
    to reset data between tests.

    Args:
        client: Boto3 DynamoDB client
        table_name: Name of the table to clear
        key_schema: Key schema of the table (list of dicts with AttributeName and KeyType)
    """
    key_names = [key["AttributeName"] for key in key_schema]
    scan_kwargs: dict[str, str] = {"ProjectionExpression": ", ".join(key_names)}

    while True:
        response = client.scan(TableName=table_name, **scan_kwargs)
        items = response.get("Items", [])

        if not items:
            break

        # Batch delete items (max 25 per request)
        for batch in batched(items, 25):
            delete_requests = [
                {"DeleteRequest": {"Key": {k: item[k] for k in key_names}}}
                for item in batch
            ]
            client.batch_write_item(RequestItems={table_name: delete_requests})

        # Check for pagination
        if "LastEvaluatedKey" not in response:
            break
        scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
