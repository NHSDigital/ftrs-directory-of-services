import os

os.environ["SQS_SSM_PATH"] = "/mocked/path"

import json
from unittest.mock import MagicMock, Mock, patch

from pipeline.migration_copy_db_trigger import (
    get_dms_workspaces,
    get_message_from_event,
    lambda_handler,
)


@patch("pipeline.migration_copy_db_trigger.sqs.send_message")
@patch("pipeline.migration_copy_db_trigger.get_dms_workspaces")
def test_lambda_handler(
    mock_get_dms_workspaces: MagicMock,
    mock_send_message: MagicMock,
) -> None:
    mock_get_dms_workspaces.return_value = [
        "https://sqs.queue.url/1",
        "https://sqs.queue.url/2",
    ]
    mock_send_message.return_value = {"MessageId": "12345"}

    event = {"key": "value"}
    context = {}

    lambda_handler(event, context)

    EXPECTED_CALL_COUNT = 2
    assert mock_send_message.call_count == EXPECTED_CALL_COUNT
    mock_send_message.assert_any_call(
        QueueUrl="https://sqs.queue.url/1",
        MessageBody=json.dumps({"source": "aurora_trigger", "event": event}),
    )
    mock_send_message.assert_any_call(
        QueueUrl="https://sqs.queue.url/2",
        MessageBody=json.dumps({"source": "aurora_trigger", "event": event}),
    )


@patch("pipeline.migration_copy_db_trigger.logger.info")
def test_get_message_from_event(mock_logger_info: MagicMock) -> None:
    event = {"key": "value"}
    message = get_message_from_event(event)

    assert message == {"source": "aurora_trigger", "event": event}
    mock_logger_info.assert_called_once_with("Received event: %s", json.dumps(event))


@patch("pipeline.migration_copy_db_trigger.ssm.get_paginator")
@patch("pipeline.migration_copy_db_trigger.logger.info")
def test_get_dms_workspaces(
    mock_logger_info: MagicMock,
    mock_get_paginator: MagicMock,
) -> None:
    mock_paginator = Mock()
    mock_get_paginator.return_value = mock_paginator

    mock_paginator.paginate.return_value = [
        {"Parameters": [{"Value": "workspace1"}, {"Value": "workspace2"}]}
    ]

    workspaces = get_dms_workspaces()

    assert workspaces == ["workspace1", "workspace2"]
    mock_logger_info.assert_called_with(
        "Retrieved DMS workspaces: %s", ["workspace1", "workspace2"]
    )
    mock_get_paginator.assert_called_once_with("get_parameters_by_path")
