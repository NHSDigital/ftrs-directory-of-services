import json
from unittest.mock import MagicMock, patch

import boto3
import pytest

from pipeline.migration_copy_db_trigger_lambda_handler import (
    lambda_handler,
)


@pytest.fixture(scope="module", autouse=True)
def mock_boto3() -> MagicMock:
    with patch.object(boto3, "client") as mock_boto3_client:
        mock_sqs = MagicMock()
        mock_boto3_client.return_value = mock_sqs
        mock_sqs.send_message.return_value = {"MessageId": "mocked-message-id"}
        yield mock_boto3_client


@pytest.fixture
def mock_sqs_client() -> MagicMock:
    with patch(
        "pipeline.migration_copy_db_trigger_lambda_handler.SQS_CLIENT"
    ) as mock_client:
        mock_client.send_message.return_value = {"MessageId": "test-message-id"}
        yield mock_client


@pytest.fixture
def mock_workspaces() -> MagicMock:
    with patch(
        "pipeline.migration_copy_db_trigger_lambda_handler.get_dms_workspaces"
    ) as mock_get_workspaces:
        mock_get_workspaces.return_value = ["queue-url-1", "queue-url-2"]
        yield mock_get_workspaces


def test_lambda_handler_sends_message_to_all_workspaces(
    mock_sqs_client: MagicMock, mock_workspaces: MagicMock
) -> None:
    event = {"detail": {"eventName": "INSERT"}}
    context = {}

    lambda_handler(event, context)
    send_call_count = 2

    assert mock_sqs_client.send_message.call_count == send_call_count
    mock_sqs_client.send_message.assert_any_call(
        QueueUrl="queue-url-1",
        MessageBody=json.dumps(event),
    )
    mock_sqs_client.send_message.assert_any_call(
        QueueUrl="queue-url-2",
        MessageBody=json.dumps(event),
    )


def test_lambda_handler_handles_sqs_exception(
    mock_sqs_client: MagicMock, mock_workspaces: MagicMock
) -> None:
    event = {"detail": {"eventName": "INSERT"}}
    context = {}
    send_call_count = 2
    mock_sqs_client.send_message.side_effect = [
        {"MessageId": "test-message-id"},
        Exception("SQS error"),
    ]

    lambda_handler(event, context)

    assert mock_sqs_client.send_message.call_count == send_call_count
