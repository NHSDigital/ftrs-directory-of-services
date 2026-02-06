"""Test resource setup for LocalStack.

This module provides functions to create test resources in LocalStack,
such as S3 buckets, SQS queues, and Secrets Manager secrets.

These resources mirror the structure of the real AWS environment so that
tests can run locally without modification.
"""

import json
import os
from typing import Any

import boto3
from loguru import logger

try:
    from ftrs_common.testing.dynamodb_fixtures import create_dynamodb_tables
    from ftrs_common.testing.table_config import get_dynamodb_table_configs
except ImportError:  # pragma: no cover
    create_dynamodb_tables = None
    get_dynamodb_table_configs = None


def get_resource_name_parts() -> dict[str, str]:
    """Get the resource naming parts from environment variables."""
    return {
        "project": os.environ.get("PROJECT_NAME", "ftrs-dos"),
        "environment": os.environ.get("ENVIRONMENT", "local"),
        "workspace": os.environ.get("WORKSPACE", "test"),
    }


def setup_test_s3_buckets(endpoint_url: str) -> list[str]:
    """Create test S3 buckets in LocalStack.

    Creates buckets that mirror the naming convention used in real AWS:
    {project}-{environment}-{stack}-{resource}-{workspace}

    Args:
        endpoint_url: LocalStack endpoint URL

    Returns:
        List of created bucket names
    """
    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    parts = get_resource_name_parts()
    project = parts["project"]
    env = parts["environment"]
    workspace = parts["workspace"]

    # Define buckets to create (matching production naming)
    bucket_configs = [
        f"{project}-{env}-data-migration-input-{workspace}",
        f"{project}-{env}-data-migration-output-{workspace}",
        f"{project}-{env}-etl-ods-data-{workspace}",
        f"{project}-{env}-exports-{workspace}",
    ]

    created_buckets = []
    for bucket_name in bucket_configs:
        try:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
            logger.info(f"Created S3 bucket: {bucket_name}")
            created_buckets.append(bucket_name)
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.debug(f"S3 bucket already exists: {bucket_name}")
            created_buckets.append(bucket_name)
        except Exception as e:
            logger.error(f"Failed to create bucket {bucket_name}: {e}")

    return created_buckets


def setup_test_sqs_queues(endpoint_url: str) -> dict[str, str]:
    """Create test SQS queues in LocalStack.

    Creates queues that mirror the naming convention used in real AWS.

    Args:
        endpoint_url: LocalStack endpoint URL

    Returns:
        Dict mapping queue name to queue URL
    """
    sqs_client = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    parts = get_resource_name_parts()
    project = parts["project"]
    env = parts["environment"]
    workspace = parts["workspace"]

    # Define queues to create (matching production naming)
    queue_configs = [
        f"{project}-{env}-etl-ods-extraction-queue-{workspace}",
        f"{project}-{env}-etl-ods-transform-queue-{workspace}",
        f"{project}-{env}-etl-ods-load-queue-{workspace}",
        f"{project}-{env}-etl-ods-queue-{workspace}",
        f"{project}-{env}-crud-api-queue-{workspace}",
    ]

    created_queues = {}
    for queue_name in queue_configs:
        try:
            response = sqs_client.create_queue(QueueName=queue_name)
            queue_url = response["QueueUrl"]
            logger.info(f"Created SQS queue: {queue_name} at {queue_url}")
            created_queues[queue_name] = queue_url
        except Exception as e:
            logger.error(f"Failed to create queue {queue_name}: {e}")

    return created_queues


def setup_test_secrets(endpoint_url: str) -> list[str]:
    """Create test secrets in LocalStack Secrets Manager.

    Creates secrets that mirror the structure used in real AWS,
    with test values suitable for local testing.

    Args:
        endpoint_url: LocalStack endpoint URL

    Returns:
        List of created secret names
    """
    secrets_client = boto3.client(
        "secretsmanager",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    env = os.environ.get("ENVIRONMENT", "local")

    # Define secrets to create (matching production naming)
    secret_configs = [
        {
            "name": f"/ftrs-directory-of-services/{env}/api-ca-pk",
            "value": "-----BEGIN PRIVATE KEY-----\ntest-private-key\n-----END PRIVATE KEY-----",  # gitleaks:allow
        },
        {
            "name": f"/ftrs-directory-of-services/{env}/api-ca-cert",
            "value": "-----BEGIN CERTIFICATE-----\ntest-certificate\n-----END CERTIFICATE-----",
        },
        {
            "name": f"/ftrs-dos/{env}/ods-terminology-api-key",
            "value": json.dumps({"api_key": "test-ods-api-key"}),
        },
    ]

    created_secrets = []
    for secret_config in secret_configs:
        try:
            secrets_client.create_secret(
                Name=secret_config["name"],
                SecretString=secret_config["value"],
            )
            logger.info(f"Created secret: {secret_config['name']}")
            created_secrets.append(secret_config["name"])
        except secrets_client.exceptions.ResourceExistsException:
            # Update existing secret
            secrets_client.put_secret_value(
                SecretId=secret_config["name"],
                SecretString=secret_config["value"],
            )
            logger.debug(f"Updated existing secret: {secret_config['name']}")
            created_secrets.append(secret_config["name"])
        except Exception as e:
            logger.error(f"Failed to create secret {secret_config['name']}: {e}")

    return created_secrets


def setup_test_dynamodb_tables(endpoint_url: str) -> list[str]:
    """Create test DynamoDB tables in LocalStack.

    Uses the shared table configurations from ftrs_common.testing.

    Args:
        endpoint_url: LocalStack endpoint URL

    Returns:
        List of created table names
    """
    if create_dynamodb_tables is None or get_dynamodb_table_configs is None:
        raise RuntimeError(
            "ftrs_common testing helpers are required to create DynamoDB tables"
        )

    dynamodb_client = boto3.client(
        "dynamodb",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )

    # Get table configurations for all table types
    table_configs = get_dynamodb_table_configs(
        include_core=True,
        include_triage_code=True,
        include_data_migration_state=True,
    )

    return create_dynamodb_tables(dynamodb_client, table_configs)


def setup_all_test_resources(endpoint_url: str) -> dict[str, Any]:
    """Setup all test resources in LocalStack.

    Convenience function that creates all resources needed for testing.

    Args:
        endpoint_url: LocalStack endpoint URL

    Returns:
        Dict with all created resources
    """
    logger.info("Setting up all test resources in LocalStack...")

    buckets = setup_test_s3_buckets(endpoint_url)
    queues = setup_test_sqs_queues(endpoint_url)
    secrets = setup_test_secrets(endpoint_url)
    tables = setup_test_dynamodb_tables(endpoint_url)

    logger.info(
        f"Test resources created: {len(buckets)} buckets, {len(queues)} queues, "
        f"{len(secrets)} secrets, {len(tables)} tables"
    )

    return {
        "buckets": buckets,
        "queues": queues,
        "secrets": secrets,
        "tables": tables,
    }
