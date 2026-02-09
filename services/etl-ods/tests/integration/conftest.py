"""Integration test fixtures for etl-ods service.

This module provides pytest fixtures for running integration tests against
real AWS services (SQS, Secrets Manager) using LocalStack testcontainers.

The fixtures set up the complete ETL-ODS environment including:
- SQS queues (extraction-queue, transform-queue, queue)
- Secrets Manager secrets (ODS API key, JWT credentials)
- Environment variables for local testing

Usage:
    def test_sqs_message_flow(sqs_client, etl_ods_queues):
        # Send message to extraction queue
        sqs_client.send_message(
            QueueUrl=etl_ods_queues["extraction-queue"]["queue_url"],
            MessageBody=json.dumps({"org_id": "test"}),
        )
        # Verify message was received
        messages = get_queue_messages(
            sqs_client,
            etl_ods_queues["extraction-queue"]["queue_url"],
        )
        assert len(messages) == 1
"""

import os
from typing import Any, Generator

import pytest

# Import shared fixtures from ftrs_common.testing
from ftrs_common.testing import (
    localstack_container,
)
from ftrs_common.testing.secrets_fixtures import (
    cleanup_etl_ods_secrets,
    create_etl_ods_secrets,
    create_secret,
    delete_secret,
    get_secret,
    list_secrets,
    secrets_client,
)
from ftrs_common.testing.sqs_fixtures import (
    cleanup_etl_ods_queues,
    cleanup_sqs_queue,
    create_etl_ods_queues,
    create_sqs_queue,
    get_queue_message_count,
    get_queue_messages,
    purge_sqs_queue,
    sqs_client,
    sqs_queue,
    sqs_queue_session,
)
from pytest_mock import MockerFixture
from testcontainers.localstack import LocalStackContainer

# Re-export fixtures for pytest discovery
localstack_container = localstack_container
sqs_client = sqs_client
secrets_client = secrets_client
sqs_queue = sqs_queue
sqs_queue_session = sqs_queue_session


@pytest.fixture(scope="session")
def localstack_endpoint(localstack_container: LocalStackContainer) -> str:
    """Get the LocalStack endpoint URL."""
    return localstack_container.get_url()


@pytest.fixture(scope="session")
def etl_ods_queues(
    sqs_client: Any,
) -> Generator[dict[str, dict[str, str]], None, None]:
    """
    Create session-scoped ETL-ODS queues.

    Creates all three queues used by the ETL pipeline:
    - extraction-queue: Receives raw org IDs from extractor
    - transform-queue: Receives transformed org data
    - queue: Final consumer queue

    Args:
        sqs_client: Boto3 SQS client fixture

    Yields:
        Dict mapping queue suffix to queue info (name, url)
    """
    queues = create_etl_ods_queues(sqs_client, env="test")

    yield queues

    cleanup_etl_ods_queues(sqs_client, queues)


@pytest.fixture(scope="session")
def etl_ods_secrets(
    secrets_client: Any,
) -> Generator[dict[str, str], None, None]:
    """
    Create session-scoped ETL-ODS secrets.

    Creates secrets needed for ODS and APIM integration:
    - ODS Terminology API key
    - JWT credentials for APIM authentication

    Args:
        secrets_client: Boto3 Secrets Manager client fixture

    Yields:
        Dict mapping secret type to secret name
    """
    secrets = create_etl_ods_secrets(secrets_client)

    yield secrets

    cleanup_etl_ods_secrets(secrets_client)


@pytest.fixture(scope="function")
def etl_ods_environment(
    localstack_endpoint: str,
    etl_ods_queues: dict[str, dict[str, str]],
    etl_ods_secrets: dict[str, str],
) -> Generator[dict[str, str], None, None]:
    """
    Set up complete environment for ETL-ODS integration tests.

    This fixture:
    1. Sets all required environment variables
    2. Configures boto3 to use LocalStack endpoint
    3. Provides queue URLs and secret names

    Args:
        localstack_endpoint: LocalStack URL
        etl_ods_queues: ETL-ODS SQS queues
        etl_ods_secrets: ETL-ODS secrets

    Yields:
        Dict with environment configuration
    """
    env_vars = {
        # AWS configuration
        "AWS_REGION": "eu-west-2",
        "AWS_DEFAULT_REGION": "eu-west-2",
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_ENDPOINT_URL": localstack_endpoint,
        # Application configuration
        "ENVIRONMENT": "test",
        "WORKSPACE": "",
        "PROJECT_NAME": "ftrs",
        # URLs for local testing
        "LOCAL_API_KEY": "test-api-key",
        "LOCAL_APIM_API_URL": "http://localhost:8080/api",
        "LOCAL_ODS_URL": "http://localhost:8080/ods",
        "LOCAL_PRIVATE_KEY": "test-private-key",
        "LOCAL_KID": "test-kid",
        "LOCAL_TOKEN_URL": "http://localhost:8080/token",
    }

    # Store original environment
    original_env = os.environ.copy()

    # Set environment variables
    os.environ.update(env_vars)

    yield {
        "endpoint_url": localstack_endpoint,
        "queues": etl_ods_queues,
        "secrets": etl_ods_secrets,
        **env_vars,
    }

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="function")
def clean_queues(
    sqs_client: Any,
    etl_ods_queues: dict[str, dict[str, str]],
) -> Generator[None, None, None]:
    """
    Purge all ETL-ODS queues before each test.

    This ensures test isolation by removing any messages
    left from previous tests.
    """
    for queue_info in etl_ods_queues.values():
        purge_sqs_queue(sqs_client, queue_info["queue_url"])

    yield


@pytest.fixture(scope="function")
def mock_ods_api(mocker: MockerFixture) -> Any:
    """
    Mock the ODS Terminology API client for integration tests.

    Use this when you want to test the SQS flow without
    making actual HTTP calls to the ODS API.

    Returns:
        Mock ODS client
    """
    mock_client = mocker.MagicMock()
    mock_client.get_organisation.return_value = {
        "resourceType": "Organization",
        "id": "test-org-123",
        "name": "Test Organisation",
        "active": True,
    }
    mock_client.get_changes.return_value = {
        "entry": [
            {"resource": {"id": "org-1", "name": "Org 1"}},
            {"resource": {"id": "org-2", "name": "Org 2"}},
        ]
    }
    mocker.patch("common.ods_client.ODSClient", return_value=mock_client)
    return mock_client


@pytest.fixture(scope="function")
def mock_apim_api(mocker: MockerFixture) -> Any:
    """
    Mock the APIM API client for integration tests.

    Use this when you want to test the SQS flow without
    making actual HTTP calls to the APIM API.

    Returns:
        Mock APIM client
    """
    mock_client = mocker.MagicMock()
    mock_client.post.return_value = {
        "status": "success",
        "id": "created-org-123",
    }
    mock_client.put.return_value = {
        "status": "success",
        "id": "updated-org-123",
    }
    mocker.patch("common.apim_client.ApimClient", return_value=mock_client)
    return mock_client


# Export utility functions for tests
__all__ = [
    # Container and clients
    "localstack_container",
    "localstack_endpoint",
    "sqs_client",
    "secrets_client",
    # Queue fixtures
    "sqs_queue",
    "sqs_queue_session",
    "etl_ods_queues",
    "clean_queues",
    # Queue utilities
    "create_sqs_queue",
    "cleanup_sqs_queue",
    "purge_sqs_queue",
    "get_queue_messages",
    "get_queue_message_count",
    "create_etl_ods_queues",
    "cleanup_etl_ods_queues",
    # Secret fixtures
    "etl_ods_secrets",
    # Secret utilities
    "create_secret",
    "get_secret",
    "delete_secret",
    "list_secrets",
    "create_etl_ods_secrets",
    "cleanup_etl_ods_secrets",
    # Environment
    "etl_ods_environment",
    # Mocks
    "mock_ods_api",
    "mock_apim_api",
]
