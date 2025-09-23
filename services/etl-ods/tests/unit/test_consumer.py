import logging
from http import HTTPStatus
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests_mock import Mocker as RequestsMock

from pipeline.consumer import (
    RequestProcessingError,
    consumer_lambda_handler,
    process_message_and_send_request,
)


@pytest.fixture
def mock_lambda_context() -> LambdaContext:
    """Mock Lambda context for testing."""
    context = LambdaContext()
    context._function_name = "test-function"
    context._function_version = "LATEST"
    context._invoked_function_arn = "test-function"
    context._memory_limit_in_mb = 1
    context._aws_request_id = "test-request-id"
    context._log_group_name = "/aws/lambda/test-function"
    context._log_stream_name = "test-stream"
    return context


@pytest.fixture(autouse=True)
def mock_tracer() -> Generator[MagicMock, None, None]:
    with patch("pipeline.consumer.tracer") as mock_tracer:
        mock_tracer.capture_lambda_handler.return_value = lambda f: f
        yield mock_tracer


@patch("pipeline.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_success(
    mock_process_message: MagicMock,
    mock_lambda_context: LambdaContext,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "test2", "body": {"key": "value2"}},
        ]
    }

    response = consumer_lambda_handler(event, mock_lambda_context)

    assert response["batchItemFailures"] == []
    assert str(mock_process_message.call_count) == "2"

    expected_processing_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="1", total_records=2
        )
    )
    expected_success_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_004.value.message.format(message_id="1")
    )
    expected_processing_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="2", total_records=2
        )
    )
    expected_success_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_004.value.message.format(message_id="2")
    )
    assert expected_processing_log_1 in caplog.text
    assert expected_success_log_1 in caplog.text
    assert expected_processing_log_2 in caplog.text
    assert expected_success_log_2 in caplog.text


@patch("pipeline.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_no_event_data(
    mock_process_message: MagicMock, mock_lambda_context: LambdaContext
) -> None:
    consumer_lambda_handler({}, mock_lambda_context)

    assert str(mock_process_message.call_count) == "0"


@patch("pipeline.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_failure(
    mock_process_message: MagicMock,
    mock_lambda_context: LambdaContext,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = {
        "Records": [
            {"messageId": "1", "path": "test1", "body": {"key": "value1"}},
            {"messageId": "2", "path": "test2", "body": {"key": "value2"}},
        ]
    }

    mock_process_message.side_effect = [Exception("Test exception"), None]

    response = consumer_lambda_handler(event, mock_lambda_context)

    assert response["batchItemFailures"] == [{"itemIdentifier": "1"}]
    assert str(mock_process_message.call_count) == "2"

    expected_processing_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="1", total_records=2
        )
    )
    expected_failure_log_1 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_005.value.message.format(message_id="1")
    )
    expected_processing_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_003.value.message.format(
            message_id="2", total_records=2
        )
    )
    expected_success_log_2 = (
        OdsETLPipelineLogBase.ETL_CONSUMER_004.value.message.format(message_id="2")
    )

    assert expected_processing_log_1 in caplog.text
    assert expected_failure_log_1 in caplog.text
    assert expected_processing_log_2 in caplog.text
    assert expected_success_log_2 in caplog.text


@pytest.mark.parametrize(
    ("path", "body"),
    [
        (None, {"name": "Organization Name"}),
        ("uuid", None),
        ("", {"name": "Organization Name"}),
        ("uuid", {}),
    ],
)
def test_consumer_lambda_handler_handle_missing_message_parameters(
    path: str,
    body: dict,
    mock_lambda_context: LambdaContext,
    caplog: pytest.LogCaptureFixture,
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

    consumer_lambda_handler(event, mock_lambda_context)

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
        "http://test-apim-api/Organization/uuid",
        json={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "information",
                    "code": "success",
                    "diagnostics": "Organization updated successfully",
                }
            ],
            "status_code": 200,
        },
    )

    record = {
        "messageId": "1",
        "body": '"{\\"path\\": \\"uuid\\", \\"body\\": {\\"name\\": \\"Organization Name\\"}}"',
    }

    process_message_and_send_request(record)

    expected_success_log = OdsETLPipelineLogBase.ETL_CONSUMER_007.value.message.format(
        status_code=200
    )
    assert expected_success_log in caplog.text
    assert mock_call.called_once
    assert mock_call.last_request.path == "/organization/uuid"
    assert mock_call.last_request.json() == {"name": "Organization Name"}


def test_process_message_and_send_request_unprocessable(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json={"error": "Unprocessable Entity"},
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
    )

    record = {
        "messageId": "1",
        "path": "uuid",
        "body": {"name": "Organization Name"},
    }

    process_message_and_send_request(record)

    expected_bad_request_log = (
        OdsETLPipelineLogBase.ETL_CONSUMER_008.value.message.format(message_id="1")
    )
    assert expected_bad_request_log in caplog.text

    assert mock_call.called_once
    assert mock_call.last_request.path == "/organization/uuid"


def test_process_message_and_send_request_failure(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mock_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json={"error": "Internal Server Error"},
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    record = {
        "messageId": "1",
        "path": "uuid",
        "body": {"name": "Organization Name"},
    }
    caplog.set_level(logging.ERROR)

    with pytest.raises(RequestProcessingError):
        process_message_and_send_request(record)

    expected_failure_log = OdsETLPipelineLogBase.ETL_CONSUMER_009.value.message.format(
        message_id="1"
    )
    assert expected_failure_log in caplog.text
    assert mock_call.called_once
    assert mock_call.last_request.path == "/organization/uuid"
