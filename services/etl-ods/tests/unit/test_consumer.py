import logging
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from requests_mock import Mocker as RequestsMock

from pipeline.consumer import (
    RequestProcessingError,
    consumer_lambda_handler,
    process_message_and_send_request,
)


@patch("pipeline.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_success(
    mock_process_message: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "/test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "/test2", "body": {"key": "value2"}},
        ]
    }

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == []
    assert str(mock_process_message.call_count) == "2"
    assert "Processing message id: 1 of 2 from ODS ETL queue." in caplog.text
    assert "Message id: 1 processed successfully." in caplog.text
    assert "Processing message id: 1 of 2 from ODS ETL queue." in caplog.text
    assert "Message id: 2 processed successfully." in caplog.text


@patch("pipeline.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_no_event_data(mock_process_message: MagicMock) -> None:
    consumer_lambda_handler({}, {})

    assert str(mock_process_message.call_count) == "0"


@patch("pipeline.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_failure(
    mock_process_message: MagicMock, caplog: pytest.LogCaptureFixture
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "/test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "/test2", "body": {"key": "value2"}},
        ]
    }

    mock_process_message.side_effect = [Exception("Test exception"), None]

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == [{"itemIdentifier": "1"}]
    assert str(mock_process_message.call_count) == "2"

    assert any(
        record.levelname == "INFO"
        and "Processing message id: 1 of 2 from ODS ETL queue." in record.message
        for record in caplog.records
    )
    assert any(
        record.levelname == "INFO"
        and "Message id: 2 processed successfully." in record.message
        for record in caplog.records
    )
    assert any(
        record.levelname == "ERROR"
        and "Failed to process message id: 1." in record.message
        for record in caplog.records
    )


@pytest.mark.parametrize(
    ("path", "body"),
    [
        (None, {"name": "Organisation Name"}),
        ("uuid", None),
        ("", {"name": "Organisation Name"}),
        ("uuid", {}),
    ],
)
def test_consumer_lambda_handler_handle_missing_message_parameters(
    path: str, body: dict, caplog: pytest.LogCaptureFixture
) -> None:
    event = {
        "Records": [
            {
                "messageId": "1",
                "path": path,
                "body": body,
            }
        ]
    }

    consumer_lambda_handler(event, {})

    assert any(
        record.levelname == "WARNING"
        and "Message id: 1 is missing 'path' or 'body' fields." in record.message
        for record in caplog.records
    )
    assert any(
        record.levelname == "ERROR"
        and "Failed to process message id: 1." in record.message
        for record in caplog.records
    )


def test_process_message_and_send_request_success(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_call = requests_mock.put(
        "http://test-crud-api/organisation/uuid",
        json={"status": "success"},
        status_code=HTTPStatus.OK,
    )

    record = {
        "messageId": "1",
        "body": '"{\\"path\\": \\"/uuid\\", \\"body\\": {\\"name\\": \\"Organisation Name\\"}}"',
    }

    process_message_and_send_request(record)

    assert "Successfully sent request. Response status code: 200" in caplog.text

    assert mock_call.called_once
    assert mock_call.last_request.path == "/organisation/uuid"
    assert mock_call.last_request.json() == {"name": "Organisation Name"}


def test_process_message_and_send_request_unprocessable(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_call = requests_mock.put(
        "http://test-crud-api/organisation/uuid",
        json={"error": "Unprocessable Entity"},
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )

    record = {
        "messageId": "1",
        "path": "/uuid",
        "body": {"name": "Organisation Name"},
    }

    process_message_and_send_request(record)

    assert "Bad request returned for message id: 1. Not re-processing." in caplog.text

    assert mock_call.called_once
    assert mock_call.last_request.path == "/organisation/uuid"


def test_process_message_and_send_request_failure(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_call = requests_mock.put(
        "http://test-crud-api/organisation/uuid",
        json={"error": "Internal Server Error"},
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    record = {
        "messageId": "1",
        "path": "/uuid",
        "body": {"name": "Organisation Name"},
    }
    caplog.set_level(logging.ERROR)

    with pytest.raises(RequestProcessingError):
        process_message_and_send_request(record)

    assert "Request failed for message id: 1" in caplog.text
    assert mock_call.called_once
    assert mock_call.last_request.path == "/organisation/uuid"
