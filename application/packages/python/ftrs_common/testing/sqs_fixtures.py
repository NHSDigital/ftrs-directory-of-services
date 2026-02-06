"""SQS testcontainer fixtures for integration testing.

This module provides pytest fixtures for running integration tests against
SQS using LocalStack testcontainers.

Usage in conftest.py:
    from ftrs_common.testing.sqs_fixtures import (
        sqs_client,
        create_sqs_queue,
        cleanup_sqs_queue,
        sqs_queue,
    )

    # Re-export fixtures for pytest discovery
    sqs_client = sqs_client

Example test:
    def test_send_message(sqs_client, sqs_queue):
        sqs_client.send_message(
            QueueUrl=sqs_queue["queue_url"],
            MessageBody="test message",
        )
        response = sqs_client.receive_message(
            QueueUrl=sqs_queue["queue_url"],
            MaxNumberOfMessages=1,
        )
        assert len(response["Messages"]) == 1
        assert response["Messages"][0]["Body"] == "test message"
"""

from typing import Any, Generator

import boto3
import pytest
from loguru import logger
from testcontainers.localstack import LocalStackContainer


@pytest.fixture(scope="session")
def sqs_client(
    localstack_container: LocalStackContainer,
) -> Generator[Any, None, None]:
    """
    Boto3 SQS client connected to LocalStack.

    Args:
        localstack_container: LocalStack container fixture

    Yields:
        Boto3 SQS client
    """
    endpoint_url = localstack_container.get_url()
    client = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="eu-west-2",
    )
    yield client


def create_sqs_queue(
    client: Any,
    queue_name: str,
    attributes: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Create an SQS queue for testing.

    Args:
        client: Boto3 SQS client
        queue_name: Name of the queue to create
        attributes: Optional queue attributes (e.g., VisibilityTimeout)

    Returns:
        Dict containing queue_name and queue_url

    Raises:
        Exception: If queue creation fails
    """
    try:
        response = client.create_queue(
            QueueName=queue_name,
            Attributes=attributes or {},
        )
        queue_url = response["QueueUrl"]
        logger.debug(f"Created SQS queue: {queue_name} at {queue_url}")
        return {"queue_name": queue_name, "queue_url": queue_url}
    except client.exceptions.QueueNameExists:
        # Queue already exists, get its URL
        response = client.get_queue_url(QueueName=queue_name)
        queue_url = response["QueueUrl"]
        logger.debug(f"SQS queue {queue_name} already exists at {queue_url}")
        return {"queue_name": queue_name, "queue_url": queue_url}
    except Exception as e:
        logger.error(f"Failed to create SQS queue {queue_name}: {e}")
        raise


def cleanup_sqs_queue(client: Any, queue_url: str) -> None:
    """
    Delete an SQS queue.

    Args:
        client: Boto3 SQS client
        queue_url: URL of the queue to delete
    """
    try:
        client.delete_queue(QueueUrl=queue_url)
        logger.debug(f"Deleted SQS queue: {queue_url}")
    except client.exceptions.QueueDoesNotExist:
        logger.debug(f"SQS queue {queue_url} does not exist")
    except Exception as e:
        logger.error(f"Failed to delete SQS queue {queue_url}: {e}")


def purge_sqs_queue(client: Any, queue_url: str) -> None:
    """
    Purge all messages from an SQS queue.

    Args:
        client: Boto3 SQS client
        queue_url: URL of the queue to purge
    """
    try:
        client.purge_queue(QueueUrl=queue_url)
        logger.debug(f"Purged SQS queue: {queue_url}")
    except client.exceptions.PurgeQueueInProgress:
        logger.debug(f"SQS queue {queue_url} purge already in progress")
    except Exception as e:
        logger.error(f"Failed to purge SQS queue {queue_url}: {e}")


def get_queue_messages(
    client: Any,
    queue_url: str,
    max_messages: int = 10,
    wait_time_seconds: int = 0,
    delete_after_receive: bool = False,
) -> list[dict[str, Any]]:
    """
    Receive messages from an SQS queue.

    Args:
        client: Boto3 SQS client
        queue_url: URL of the queue
        max_messages: Maximum number of messages to receive (1-10)
        wait_time_seconds: Long polling wait time (0-20 seconds)
        delete_after_receive: If True, delete messages after receiving

    Returns:
        List of message dictionaries
    """
    response = client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=min(max_messages, 10),
        WaitTimeSeconds=wait_time_seconds,
    )

    messages = response.get("Messages", [])

    if delete_after_receive and messages:
        for msg in messages:
            client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=msg["ReceiptHandle"],
            )

    return messages


def get_queue_message_count(client: Any, queue_url: str) -> int:
    """
    Get the approximate number of messages in a queue.

    Args:
        client: Boto3 SQS client
        queue_url: URL of the queue

    Returns:
        Approximate number of messages in the queue
    """
    response = client.get_queue_attributes(
        QueueUrl=queue_url,
        AttributeNames=["ApproximateNumberOfMessages"],
    )
    return int(response["Attributes"].get("ApproximateNumberOfMessages", 0))


@pytest.fixture(scope="function")
def sqs_queue(sqs_client: Any) -> Generator[dict[str, str], None, None]:
    """
    Create a temporary SQS queue for a single test.

    This fixture creates a queue before the test and deletes it after.

    Args:
        sqs_client: Boto3 SQS client fixture

    Yields:
        Dict containing queue_name and queue_url
    """
    import uuid

    queue_name = f"test-queue-{uuid.uuid4().hex[:8]}"
    queue_info = create_sqs_queue(sqs_client, queue_name)

    yield queue_info

    cleanup_sqs_queue(sqs_client, queue_info["queue_url"])


@pytest.fixture(scope="session")
def sqs_queue_session(sqs_client: Any) -> Generator[dict[str, str], None, None]:
    """
    Create a session-scoped SQS queue for tests.

    This fixture creates a queue once per test session.
    The queue is purged between tests to ensure isolation.

    Args:
        sqs_client: Boto3 SQS client fixture

    Yields:
        Dict containing queue_name and queue_url
    """
    import uuid

    queue_name = f"test-queue-session-{uuid.uuid4().hex[:8]}"
    queue_info = create_sqs_queue(sqs_client, queue_name)

    yield queue_info

    cleanup_sqs_queue(sqs_client, queue_info["queue_url"])


def create_etl_ods_queues(
    client: Any,
    env: str = "test",
    workspace: str | None = None,
) -> dict[str, dict[str, str]]:
    """
    Create all ETL-ODS SQS queues for integration testing.

    Creates the extraction-queue, transform-queue, and queue (consumer queue).

    Args:
        client: Boto3 SQS client
        env: Environment name (default: test)
        workspace: Optional workspace name

    Returns:
        Dict mapping queue suffix to queue info (name, url)
    """
    queue_suffixes = ["extraction-queue", "transform-queue", "queue"]
    queues = {}

    for suffix in queue_suffixes:
        queue_name = f"ftrs-dos-{env}-etl-ods-{suffix}"
        if workspace:
            queue_name = f"{queue_name}-{workspace}"

        queue_info = create_sqs_queue(client, queue_name)
        queues[suffix] = queue_info

    return queues


def cleanup_etl_ods_queues(
    client: Any,
    queues: dict[str, dict[str, str]],
) -> None:
    """
    Delete all ETL-ODS SQS queues.

    Args:
        client: Boto3 SQS client
        queues: Dict returned from create_etl_ods_queues
    """
    for queue_info in queues.values():
        cleanup_sqs_queue(client, queue_info["queue_url"])


@pytest.fixture(scope="function")
def etl_ods_queues(sqs_client: Any) -> Generator[dict[str, dict[str, str]], None, None]:
    """
    Create ETL-ODS queues for a single test.

    Args:
        sqs_client: Boto3 SQS client fixture

    Yields:
        Dict mapping queue suffix to queue info (name, url)
    """
    queues = create_etl_ods_queues(sqs_client, env="test")

    yield queues

    cleanup_etl_ods_queues(sqs_client, queues)


@pytest.fixture(scope="session")
def etl_ods_queues_session(
    sqs_client: Any,
) -> Generator[dict[str, dict[str, str]], None, None]:
    """
    Create session-scoped ETL-ODS queues.

    Args:
        sqs_client: Boto3 SQS client fixture

    Yields:
        Dict mapping queue suffix to queue info (name, url)
    """
    queues = create_etl_ods_queues(sqs_client, env="test")

    yield queues

    cleanup_etl_ods_queues(sqs_client, queues)
