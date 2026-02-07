"""DynamoDB and S3 testcontainer fixtures for integration testing.

This module provides pytest fixtures for running integration tests against
real AWS services (DynamoDB, S3) using LocalStack testcontainers.

Usage in conftest.py:
    from ftrs_common.testing import (
        localstack_container,
        dynamodb_client,
        dynamodb_resource,
        s3_client,
        s3_resource,
        make_local_repository,
    )

    # Re-export fixtures for pytest discovery
    localstack_container = localstack_container
    dynamodb_client = dynamodb_client
    dynamodb_resource = dynamodb_resource
    s3_client = s3_client
    s3_resource = s3_resource

Example DynamoDB test:
    def test_create_organisation(dynamodb_resource, dynamodb_client):
        repo = make_local_repository(
            table_name="organisation",
            model_cls=Organisation,
            dynamodb_resource=dynamodb_resource,
        )
        org = Organisation(name="Test Org", ...)
        repo.create(org)
        assert repo.get(org.id) is not None

Example S3 test:
    def test_upload_file(s3_client, s3_bucket):
        s3_client.put_object(
            Bucket=s3_bucket,
            Key="test-file.txt",
            Body=b"test content",
        )
        response = s3_client.get_object(Bucket=s3_bucket, Key="test-file.txt")
        assert response["Body"].read() == b"test content"
"""

from typing import Any, Generator, TypeVar

import boto3
import pytest
from loguru import logger
from testcontainers.localstack import LocalStackContainer

from ftrs_common.testing.table_config import get_dynamodb_table_configs

# Type variable for model classes
ModelT = TypeVar("ModelT")


@pytest.fixture(scope="session")
def localstack_container() -> Generator[LocalStackContainer, None, None]:
    """
    LocalStack container with DynamoDB for testing.

    This is a session-scoped fixture that starts a LocalStack container
    once per test session and tears it down at the end.

    Yields:
        LocalStackContainer instance
    """
    container = LocalStackContainer(image="localstack/localstack:3.0")
    container.start(timeout=120)  # Increased timeout for CI runners
    try:
        logger.debug(f"LocalStack started at {container.get_url()}")
        yield container
    finally:
        container.stop()


@pytest.fixture(scope="session")
def dynamodb_client(
    localstack_container: LocalStackContainer,
) -> Generator[Any, None, None]:
    """
    Boto3 DynamoDB client connected to LocalStack.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Boto3 DynamoDB client
    """
    endpoint_url = localstack_container.get_url()
    client = boto3.client(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )
    yield client


@pytest.fixture(scope="session")
def dynamodb_resource(
    localstack_container: LocalStackContainer,
) -> Generator[Any, None, None]:
    """
    Boto3 DynamoDB resource connected to LocalStack.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Boto3 DynamoDB resource
    """
    endpoint_url = localstack_container.get_url()
    resource = boto3.resource(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )
    yield resource


@pytest.fixture(scope="session")
def s3_client(
    localstack_container: LocalStackContainer,
) -> Generator[Any, None, None]:
    """
    Boto3 S3 client connected to LocalStack.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Boto3 S3 client
    """
    endpoint_url = localstack_container.get_url()
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )
    yield client


@pytest.fixture(scope="session")
def s3_resource(
    localstack_container: LocalStackContainer,
) -> Generator[Any, None, None]:
    """
    Boto3 S3 resource connected to LocalStack.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Boto3 S3 resource
    """
    endpoint_url = localstack_container.get_url()
    resource = boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )
    yield resource


def create_s3_bucket(
    client: Any,
    bucket_name: str,
    region: str = "eu-west-2",
) -> str:
    """
    Create an S3 bucket for testing.

    Args:
        client: Boto3 S3 client
        bucket_name: Name of the bucket to create
        region: AWS region for the bucket (default: eu-west-2)

    Returns:
        The bucket name

    Raises:
        Exception: If bucket creation fails
    """
    try:
        # For eu-west-2, we need to specify LocationConstraint
        if region != "us-east-1":
            client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        else:
            client.create_bucket(Bucket=bucket_name)
        logger.debug(f"Created S3 bucket: {bucket_name}")
        return bucket_name
    except client.exceptions.BucketAlreadyExists:
        logger.debug(f"S3 bucket {bucket_name} already exists")
        return bucket_name
    except client.exceptions.BucketAlreadyOwnedByYou:
        logger.debug(f"S3 bucket {bucket_name} already owned by you")
        return bucket_name
    except Exception as e:
        logger.error(f"Failed to create S3 bucket {bucket_name}: {e}")
        raise


def cleanup_s3_bucket(client: Any, bucket_name: str) -> None:
    """
    Delete all objects from an S3 bucket and then delete the bucket.

    Args:
        client: Boto3 S3 client
        bucket_name: Name of the bucket to clean up
    """
    try:
        # First, delete all objects in the bucket
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name):
            objects = page.get("Contents", [])
            if objects:
                delete_keys = [{"Key": obj["Key"]} for obj in objects]
                client.delete_objects(
                    Bucket=bucket_name, Delete={"Objects": delete_keys}
                )
                logger.debug(f"Deleted {len(delete_keys)} objects from {bucket_name}")

        # Delete any object versions (for versioned buckets)
        try:
            paginator = client.get_paginator("list_object_versions")
            for page in paginator.paginate(Bucket=bucket_name):
                versions = page.get("Versions", [])
                delete_markers = page.get("DeleteMarkers", [])
                all_versions = versions + delete_markers
                if all_versions:
                    delete_keys = [
                        {"Key": v["Key"], "VersionId": v["VersionId"]}
                        for v in all_versions
                    ]
                    client.delete_objects(
                        Bucket=bucket_name, Delete={"Objects": delete_keys}
                    )
        except Exception:
            pass  # Bucket may not be versioned

        # Now delete the bucket
        client.delete_bucket(Bucket=bucket_name)
        logger.debug(f"Deleted S3 bucket: {bucket_name}")
    except client.exceptions.NoSuchBucket:
        logger.debug(f"S3 bucket {bucket_name} does not exist")
    except Exception as e:
        logger.error(f"Failed to cleanup S3 bucket {bucket_name}: {e}")


def upload_to_s3(
    client: Any,
    bucket_name: str,
    key: str,
    content: bytes | str,
    content_type: str = "application/octet-stream",
) -> None:
    """
    Upload content to an S3 bucket.

    Args:
        client: Boto3 S3 client
        bucket_name: Name of the bucket
        key: Object key (path in bucket)
        content: Content to upload (bytes or string)
        content_type: MIME type of the content
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=content,
        ContentType=content_type,
    )
    logger.debug(f"Uploaded {key} to s3://{bucket_name}")


def download_from_s3(client: Any, bucket_name: str, key: str) -> bytes:
    """
    Download content from an S3 bucket.

    Args:
        client: Boto3 S3 client
        bucket_name: Name of the bucket
        key: Object key (path in bucket)

    Returns:
        The content as bytes
    """
    response = client.get_object(Bucket=bucket_name, Key=key)
    return response["Body"].read()


@pytest.fixture(scope="function")
def s3_bucket(s3_client: Any) -> Generator[str, None, None]:
    """
    S3 bucket fixture for each test.

    Creates a unique bucket for the test and cleans it up afterwards.

    Yields:
        The bucket name
    """
    import uuid

    bucket_name = f"test-bucket-{uuid.uuid4().hex[:8]}"
    try:
        create_s3_bucket(s3_client, bucket_name)
        yield bucket_name
    finally:
        cleanup_s3_bucket(s3_client, bucket_name)


@pytest.fixture(scope="session")
def s3_bucket_session(s3_client: Any) -> Generator[str, None, None]:
    """
    Session-scoped S3 bucket fixture.

    Creates a bucket once per session. Use this when tests don't
    interfere with each other's data or when you want maximum performance.

    Yields:
        The bucket name
    """
    bucket_name = "test-bucket-session"
    try:
        create_s3_bucket(s3_client, bucket_name)
        yield bucket_name
    finally:
        cleanup_s3_bucket(s3_client, bucket_name)


def create_dynamodb_tables(
    client: Any,
    table_configs: list[dict[str, Any]] | None = None,
) -> list[str]:
    """
    Create DynamoDB tables for testing.

    Args:
        client: Boto3 DynamoDB client
        table_configs: Optional list of table configurations.
                       If not provided, uses get_dynamodb_table_configs().

    Returns:
        List of created table names

    Raises:
        Exception: If table creation fails
    """
    if table_configs is None:
        table_configs = get_dynamodb_table_configs()

    created_tables: list[str] = []
    logger.debug(f"Creating {len(table_configs)} DynamoDB tables")

    for config in table_configs:
        table_name = config["TableName"]
        try:
            client.create_table(**config)
            waiter = client.get_waiter("table_exists")
            waiter.wait(TableName=table_name)
            logger.debug(f"Created table: {table_name}")
            created_tables.append(table_name)
        except client.exceptions.ResourceInUseException:
            logger.debug(f"Table {table_name} already exists")
            created_tables.append(table_name)
        except Exception as e:
            logger.error(f"Failed to create table {table_name}: {e}")
            raise

    logger.debug(f"DynamoDB tables ready: {created_tables}")
    return created_tables


def cleanup_dynamodb_tables(client: Any) -> None:
    """
    Clean up all DynamoDB tables.

    Args:
        client: Boto3 DynamoDB client
    """
    try:
        response = client.list_tables()
        table_names = response.get("TableNames", [])

        for table_name in table_names:
            try:
                client.delete_table(TableName=table_name)
                waiter = client.get_waiter("table_not_exists")
                waiter.wait(TableName=table_name)
                logger.debug(f"Deleted DynamoDB table: {table_name}")
            except Exception as e:
                logger.error(f"Failed to delete table {table_name}: {e}")
    except Exception as e:
        logger.error(f"DynamoDB cleanup failed: {e}")


def truncate_dynamodb_table(client: Any, resource: Any, table_name: str) -> None:
    """
    Delete all items from a DynamoDB table without dropping the table.

    This is faster than dropping and recreating the table when you need
    to reset data between tests.

    Args:
        client: Boto3 DynamoDB client
        resource: Boto3 DynamoDB resource
        table_name: Name of the table to truncate
    """
    try:
        table = resource.Table(table_name)

        # Get key schema to know which attributes to use for deletion
        response = client.describe_table(TableName=table_name)
        key_schema = response["Table"]["KeySchema"]
        key_names = [key["AttributeName"] for key in key_schema]

        # Scan and delete all items
        scan_kwargs: dict[str, Any] = {"ProjectionExpression": ", ".join(key_names)}

        while True:
            response = table.scan(**scan_kwargs)
            items = response.get("Items", [])

            if not items:
                break

            with table.batch_writer() as batch:
                for item in items:
                    key = {k: item[k] for k in key_names}
                    batch.delete_item(Key=key)

            # Check for pagination
            if "LastEvaluatedKey" not in response:
                break
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        logger.debug(f"Truncated table: {table_name}")
    except Exception as e:
        logger.error(f"Failed to truncate table {table_name}: {e}")
        raise


def make_local_repository(
    table_name: str,
    model_cls: type[ModelT],
    dynamodb_resource: Any,
    endpoint_url: str | None = None,
) -> Any:
    """
    Create an AttributeLevelRepository wired to a LocalStack DynamoDB table.

    This factory function creates a repository instance configured to use
    a local DynamoDB table, suitable for integration testing.

    Args:
        table_name: The DynamoDB table name (can be just the resource name
                    like 'organisation', or the full table name)
        model_cls: The Pydantic model class for the repository
        dynamodb_resource: Boto3 DynamoDB resource connected to LocalStack
        endpoint_url: The LocalStack endpoint URL (e.g. http://localhost:4566)

    Returns:
        Configured AttributeLevelRepository instance

    Example:
        repo = make_local_repository(
            table_name="ftrs-dos-dev-database-organisation-test",
            model_cls=Organisation,
            dynamodb_resource=dynamodb_resource,
            endpoint_url="http://localhost:4566",
        )
    """
    # Import here to avoid circular dependency issues
    from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

    # Create repository instance with endpoint_url to avoid region requirement
    repo = AttributeLevelRepository(
        model_cls=model_cls,
        table_name=table_name,
        endpoint_url=endpoint_url,
    )

    # Override resource and table to point to LocalStack
    repo.resource = dynamodb_resource
    repo.table = dynamodb_resource.Table(table_name)

    return repo


@pytest.fixture(scope="function")
def dynamodb_tables(
    dynamodb_client: Any,
    dynamodb_resource: Any,
) -> Generator[dict[str, Any], None, None]:
    """
    DynamoDB fixture with pre-created tables for each test.

    Creates all standard tables at the start and cleans up at the end.
    Tables are truncated (not dropped) between tests for faster execution.

    Yields:
        Dictionary with client, resource, endpoint_url, and table_names
    """
    try:
        table_names = create_dynamodb_tables(dynamodb_client)
        yield {
            "client": dynamodb_client,
            "resource": dynamodb_resource,
            "table_names": table_names,
        }
    finally:
        # Truncate tables instead of dropping for faster test runs
        for table_name in table_names:
            try:
                truncate_dynamodb_table(dynamodb_client, dynamodb_resource, table_name)
            except Exception:
                pass  # Ignore cleanup errors


@pytest.fixture(scope="session")
def dynamodb_tables_session(
    dynamodb_client: Any,
    dynamodb_resource: Any,
) -> Generator[dict[str, Any], None, None]:
    """
    Session-scoped DynamoDB fixture with pre-created tables.

    Creates all standard tables once per session. Use this when tests
    don't interfere with each other's data or when you want maximum
    performance.

    Yields:
        Dictionary with client, resource, and table_names
    """
    try:
        table_names = create_dynamodb_tables(dynamodb_client)
        yield {
            "client": dynamodb_client,
            "resource": dynamodb_resource,
            "table_names": table_names,
        }
    finally:
        cleanup_dynamodb_tables(dynamodb_client)
