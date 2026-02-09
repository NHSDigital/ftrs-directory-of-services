"""Integration tests for SQS message flow in ETL-ODS pipeline.

These tests verify that messages flow correctly through the SQS queues
using LocalStack testcontainers for realistic AWS interactions.
"""

import json
from typing import Any

import boto3
from ftrs_common.testing.sqs_fixtures import (
    get_queue_message_count,
    get_queue_messages,
)


class TestSQSMessageFlow:
    """Test SQS message sending and receiving with LocalStack."""

    def test_send_and_receive_single_message(
        self,
        sqs_client: Any,
        sqs_queue: dict[str, str],
    ) -> None:
        """Test sending and receiving a single message."""
        message_body = {"org_id": "test-org-123", "action": "create"}

        # Send message
        sqs_client.send_message(
            QueueUrl=sqs_queue["queue_url"],
            MessageBody=json.dumps(message_body),
        )

        # Receive message
        messages = get_queue_messages(
            sqs_client,
            sqs_queue["queue_url"],
            max_messages=1,
            wait_time_seconds=1,
            delete_after_receive=True,
        )

        assert len(messages) == 1
        received_body = json.loads(messages[0]["Body"])
        assert received_body["org_id"] == "test-org-123"
        assert received_body["action"] == "create"

    def test_send_batch_messages(
        self,
        sqs_client: Any,
        sqs_queue: dict[str, str],
    ) -> None:
        """Test sending a batch of messages."""
        messages = [
            {"Id": str(i), "MessageBody": json.dumps({"org_id": f"org-{i}"})}
            for i in range(5)
        ]

        # Send batch
        response = sqs_client.send_message_batch(
            QueueUrl=sqs_queue["queue_url"],
            Entries=messages,
        )

        assert len(response.get("Successful", [])) == 5
        assert len(response.get("Failed", [])) == 0

        # Verify message count
        count = get_queue_message_count(sqs_client, sqs_queue["queue_url"])
        assert count == 5


class TestETLODSQueues:
    """Test the ETL-ODS specific queue setup."""

    def test_etl_ods_queues_created(
        self,
        etl_ods_queues: dict[str, dict[str, str]],
    ) -> None:
        """Verify all ETL-ODS queues are created."""
        assert "extraction-queue" in etl_ods_queues
        assert "transform-queue" in etl_ods_queues
        assert "queue" in etl_ods_queues

        for queue_suffix, queue_info in etl_ods_queues.items():
            assert "queue_name" in queue_info
            assert "queue_url" in queue_info
            assert queue_suffix in queue_info["queue_name"]

    def test_extraction_to_transform_flow(
        self,
        sqs_client: Any,
        etl_ods_queues: dict[str, dict[str, str]],
        clean_queues: None,
    ) -> None:
        """Test message flow from extraction to transform queue."""
        extraction_queue = etl_ods_queues["extraction-queue"]
        transform_queue = etl_ods_queues["transform-queue"]

        # Simulate extractor sending org IDs to extraction queue
        org_ids = ["org-001", "org-002", "org-003"]
        for org_id in org_ids:
            sqs_client.send_message(
                QueueUrl=extraction_queue["queue_url"],
                MessageBody=json.dumps({"org_id": org_id}),
            )

        # Simulate transformer reading from extraction queue
        messages = get_queue_messages(
            sqs_client,
            extraction_queue["queue_url"],
            max_messages=10,
            delete_after_receive=True,
        )

        assert len(messages) == 3

        # Simulate transformer sending transformed data to transform queue
        for msg in messages:
            original = json.loads(msg["Body"])
            transformed = {
                "org_id": original["org_id"],
                "transformed": True,
                "resource_type": "Organization",
            }
            sqs_client.send_message(
                QueueUrl=transform_queue["queue_url"],
                MessageBody=json.dumps(transformed),
            )

        # Verify messages in transform queue
        transform_messages = get_queue_messages(
            sqs_client,
            transform_queue["queue_url"],
            max_messages=10,
        )

        assert len(transform_messages) == 3
        for msg in transform_messages:
            body = json.loads(msg["Body"])
            assert body["transformed"] is True
            assert body["resource_type"] == "Organization"


class TestSecretsManager:
    """Test Secrets Manager integration with LocalStack."""

    def test_etl_ods_secrets_created(
        self,
        etl_ods_secrets: dict[str, str],
    ) -> None:
        """Verify all ETL-ODS secrets are created."""
        assert "ods_api_key" in etl_ods_secrets
        assert "jwt_credentials" in etl_ods_secrets

    def test_retrieve_ods_api_key(
        self,
        secrets_client: Any,
        etl_ods_secrets: dict[str, str],
    ) -> None:
        """Test retrieving the ODS API key secret."""
        from ftrs_common.testing.secrets_fixtures import get_secret

        secret = get_secret(secrets_client, etl_ods_secrets["ods_api_key"])

        assert isinstance(secret, dict)
        assert "api_key" in secret
        assert secret["api_key"] == "test-ods-api-key"

    def test_retrieve_jwt_credentials(
        self,
        secrets_client: Any,
        etl_ods_secrets: dict[str, str],
    ) -> None:
        """Test retrieving JWT credentials secret."""
        from ftrs_common.testing.secrets_fixtures import get_secret

        secret = get_secret(secrets_client, etl_ods_secrets["jwt_credentials"])

        assert isinstance(secret, dict)
        assert "private_key" in secret
        assert "key_id" in secret
        assert "api_key" in secret
        assert secret["key_id"] == "test-key-id"


class TestEnvironmentSetup:
    """Test the complete ETL-ODS environment setup."""

    def test_environment_variables_set(
        self,
        etl_ods_environment: dict[str, str],
    ) -> None:
        """Verify environment variables are correctly set."""
        import os

        assert os.environ.get("AWS_REGION") == "eu-west-2"
        assert os.environ.get("ENVIRONMENT") == "test"
        assert os.environ.get("PROJECT_NAME") == "ftrs"
        assert "AWS_ENDPOINT_URL" in os.environ

    def test_boto3_uses_localstack(
        self,
        etl_ods_environment: dict[str, str],
    ) -> None:
        """Verify boto3 can connect to LocalStack."""
        import os

        endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
        assert endpoint_url is not None

        # Create a client using the environment endpoint
        sqs = boto3.client(
            "sqs",
            endpoint_url=endpoint_url,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="eu-west-2",
        )

        # Verify we can list queues
        response = sqs.list_queues()
        assert "QueueUrls" in response or response.get("QueueUrls") is None
