import json
from unittest.mock import MagicMock, patch

import boto3
import pytest

from record_change_trigger.lambda_handler import (
    get_dms_workspaces,
    get_message_from_event,
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
    with patch("record_change_trigger.lambda_handler.SQS_CLIENT") as mock_client:
        mock_client.send_message.return_value = {"MessageId": "test-message-id"}
        yield mock_client


@pytest.fixture
def mock_workspaces() -> MagicMock:
    with patch(
        "record_change_trigger.lambda_handler.get_dms_workspaces"
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
        MessageBody=json.dumps({"source": "aurora_trigger", "event": event}),
    )
    mock_sqs_client.send_message.assert_any_call(
        QueueUrl="queue-url-2",
        MessageBody=json.dumps({"source": "aurora_trigger", "event": event}),
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


def test_get_message_from_event_creates_correct_message_format() -> None:
    event = {"detail": {"eventName": "INSERT"}}

    message = get_message_from_event(event)

    assert message == {"source": "aurora_trigger", "event": event}


def test_get_message_from_event_handles_empty_event() -> None:
    event = {}

    message = get_message_from_event(event)

    assert message == {"source": "aurora_trigger", "event": {}}


def test_lambda_handler_handles_complex_event_structure(
    mock_sqs_client: MagicMock, mock_workspaces: MagicMock
) -> None:
    complex_event = {
        "version": "0",
        "id": "12345678-1234-1234-1234-123456789012",
        "detail-type": "AWS API Call via CloudTrail",
        "source": "aws.rds",
        "account": "123456789012",
        "time": "2023-01-01T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {
            "eventVersion": "1.08",
            "eventSource": "rds.amazonaws.com",
            "eventName": "CreateDBInstance",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "123.45.67.89",
            "userAgent": "aws-cli/2.0.0",
        },
    }
    context = {}

    lambda_handler(complex_event, context)

    expected_message = json.dumps({"source": "aurora_trigger", "event": complex_event})

    mock_sqs_client.send_message.assert_called_with(
        QueueUrl="queue-url-2", MessageBody=expected_message
    )


@patch("record_change_trigger.lambda_handler.os.environ.get")
@patch("record_change_trigger.lambda_handler.get_parameters")
def test_returns_list_of_workspaces_when_ssm_path_exists(
    mock_get_multiple: MagicMock, mock_environ_get: MagicMock
) -> None:
    # Arrange
    mock_environ_get.return_value = "/path/to/ssm"
    mock_get_multiple.return_value = {"param1": "workspace1", "param2": "workspace2"}

    # Act
    result = get_dms_workspaces()

    # Assert
    assert result == ["workspace1", "workspace2"]
    mock_environ_get.assert_called_once_with("SQS_SSM_PATH")
    mock_get_multiple.assert_called_once_with(
        "/path/to/ssm", recursive=True, decrypt=True, max_age=300
    )


@patch("record_change_trigger.lambda_handler.os.environ.get")
def test_raises_value_error_when_ssm_path_missing(mock_environ_get: MagicMock) -> None:
    # Arrange
    mock_environ_get.return_value = None

    # Act & Assert
    with pytest.raises(
        ValueError, match="Missing required environment variable: SQS_SSM_PATH"
    ):
        get_dms_workspaces()
    mock_environ_get.assert_called_once_with("SQS_SSM_PATH")


@patch("record_change_trigger.lambda_handler.os.environ.get")
@patch("record_change_trigger.lambda_handler.get_parameters")
def test_returns_empty_list_when_no_parameters_found(
    mock_get_multiple: MagicMock, mock_environ_get: MagicMock
) -> None:
    # Arrange
    mock_environ_get.return_value = "/path/to/ssm"
    mock_get_multiple.return_value = {}

    # Act
    result = get_dms_workspaces()

    # Assert
    assert result == []
    mock_get_multiple.assert_called_once()
