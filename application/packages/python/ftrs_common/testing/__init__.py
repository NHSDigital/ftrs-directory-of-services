"""Shared testing utilities for FtRS services.

This module provides common test fixtures and utilities that can be used
across different service test suites, including:

- DynamoDB testcontainer fixtures for integration testing
- S3 testcontainer fixtures for integration testing
- SQS testcontainer fixtures for integration testing
- Secrets Manager testcontainer fixtures for integration testing
- Table configuration helpers
- Repository factory functions for local testing

Usage (table config only - no extra dependencies):
    from ftrs_common.testing.table_config import (
        get_table_name,
        get_dynamodb_table_configs,
    )

Usage (full fixtures - requires testcontainers, boto3, loguru):
    from ftrs_common.testing.dynamodb_fixtures import (
        localstack_container,
        dynamodb_client,
        dynamodb_resource,
        s3_client,
        s3_resource,
        create_dynamodb_tables,
        create_s3_bucket,
        make_local_repository,
    )

    from ftrs_common.testing.sqs_fixtures import (
        sqs_client,
        sqs_queue,
        create_sqs_queue,
        create_etl_ods_queues,
    )

    from ftrs_common.testing.secrets_fixtures import (
        secrets_client,
        create_secret,
        get_secret,
        create_etl_ods_secrets,
    )
"""

# Table config is always available (no external dependencies)
from ftrs_common.testing.table_config import (
    get_dynamodb_table_configs,
    get_table_name,
)

__all__ = [
    # Table helpers (always available)
    "get_table_name",
    "get_dynamodb_table_configs",
]


def __getattr__(name: str):
    """Lazy import for fixture-related items that require external dependencies."""
    dynamodb_exports = {
        # LocalStack container
        "localstack_container",
        # DynamoDB fixtures
        "dynamodb_client",
        "dynamodb_resource",
        "create_dynamodb_tables",
        "cleanup_dynamodb_tables",
        "truncate_dynamodb_table",
        "dynamodb_tables",
        "dynamodb_tables_session",
        "make_local_repository",
        # S3 fixtures
        "s3_client",
        "s3_resource",
        "s3_bucket",
        "s3_bucket_session",
        "create_s3_bucket",
        "cleanup_s3_bucket",
        "upload_to_s3",
        "download_from_s3",
    }

    sqs_exports = {
        # SQS fixtures
        "sqs_client",
        "sqs_queue",
        "sqs_queue_session",
        "create_sqs_queue",
        "cleanup_sqs_queue",
        "purge_sqs_queue",
        "get_queue_messages",
        "get_queue_message_count",
        "etl_ods_queues",
        "etl_ods_queues_session",
        "create_etl_ods_queues",
        "cleanup_etl_ods_queues",
    }

    secrets_exports = {
        # Secrets Manager fixtures
        "secrets_client",
        "create_secret",
        "get_secret",
        "delete_secret",
        "list_secrets",
        "etl_ods_secrets",
        "etl_ods_secrets_session",
        "create_etl_ods_secrets",
        "cleanup_etl_ods_secrets",
    }

    if name in dynamodb_exports:
        from ftrs_common.testing import dynamodb_fixtures

        return getattr(dynamodb_fixtures, name)

    if name in sqs_exports:
        from ftrs_common.testing import sqs_fixtures

        return getattr(sqs_fixtures, name)

    if name in secrets_exports:
        from ftrs_common.testing import secrets_fixtures

        return getattr(secrets_fixtures, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
