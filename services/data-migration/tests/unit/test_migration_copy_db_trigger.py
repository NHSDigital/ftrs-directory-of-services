import os
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture

os.environ["SQS_SSM_PATH"] = "/mocked/path"

# Mock boto3 and set up SSM mock BEFORE importing the module
mock_ssm = MagicMock()
mock_ssm.get_paginator.return_value.paginate.return_value = [
    {"Parameters": [{"Value": "https://sqs.queue.url/1"}]}
]

# Create a patcher for boto3.client
boto3_client_patcher = patch("boto3.client")
mock_boto_client = boto3_client_patcher.start()
mock_boto_client.return_value = mock_ssm

from pipeline.migration_copy_db_trigger import (  # noqa: E402
    get_dms_workspaces,
    get_message_from_event,
    lambda_handler,
)


@patch("pipeline.migration_copy_db_trigger.sqs.send_message")
@patch("pipeline.migration_copy_db_trigger.get_dms_workspaces")
@patch("pipeline.migration_copy_db_trigger.logger.exception")
def test_lambda_handler_sqs_failure(
    mock_logger_exception: MagicMock,
    mock_get_dms_workspaces: MagicMock,
    mock_send_message: MagicMock,
) -> None:
    """Test lambda_handler when SQS send_message fails"""
    mock_get_dms_workspaces.return_value = ["https://sqs.queue.url/1"]
    mock_send_message.side_effect = ClientError(
        {"Error": {"Code": "InvalidRequest", "Message": "Failed to send"}},
        "SendMessage",
    )

    event = {"key": "value"}
    context = {}

    lambda_handler(event, context)

    mock_logger_exception.assert_called_once_with(
        "Failed to send message to SQS for workspace %s", "https://sqs.queue.url/1"
    )


def test_lambda_handler_success(
    mocker: MockerFixture,
) -> None:
    """Test lambda_handler with a successful SQS message sending"""
    mock_send_message = mocker.patch(
        "pipeline.migration_copy_db_trigger.sqs.send_message",
        return_value={"MessageId": "12345"},
    )

    event = {"key": "value"}
    context = {}

    lambda_handler(event, context)

    mock_send_message.assert_called_once_with(
        QueueUrl="https://sqs.queue.url/1",
        MessageBody='{"source": "aurora_trigger", "event": {"key": "value"}}',
    )


@patch("pipeline.migration_copy_db_trigger.ssm.get_paginator")
@patch("pipeline.migration_copy_db_trigger.logger.exception")
def test_get_dms_workspaces_failure(
    mock_logger_exception: MagicMock,
    mock_get_paginator: MagicMock,
) -> None:
    """Test get_dms_workspaces when SSM parameter retrieval fails"""
    mock_paginator = MagicMock()
    mock_get_paginator.return_value = mock_paginator
    mock_paginator.paginate.side_effect = ClientError(
        {"Error": {"Code": "ParameterNotFound", "Message": "Parameter not found"}},
        "GetParametersByPath",
    )

    with pytest.raises(ClientError):
        get_dms_workspaces()

    mock_logger_exception.assert_called_once_with("Error retrieving DMS workspaces")


@patch("pipeline.migration_copy_db_trigger.ssm.get_paginator")
def test_get_dms_workspaces_multiple_pages(
    mock_get_paginator: MagicMock,
) -> None:
    """Test get_dms_workspaces with multiple pages of results"""
    mock_paginator = MagicMock()
    mock_get_paginator.return_value = mock_paginator

    mock_paginator.paginate.return_value = [
        {"Parameters": [{"Value": "workspace1"}, {"Value": "workspace2"}]},
        {"Parameters": [{"Value": "workspace3"}]},
    ]

    workspaces = get_dms_workspaces()

    assert workspaces == ["workspace1", "workspace2", "workspace3"]
    mock_paginator.paginate.assert_called_once_with(
        Path="/mocked/path", Recursive=True, WithDecryption=True
    )


def test_get_message_from_event_empty_event() -> None:
    """Test get_message_from_event with empty event"""
    event = {}
    message = get_message_from_event(event)

    assert message == {"source": "aurora_trigger", "event": {}}
