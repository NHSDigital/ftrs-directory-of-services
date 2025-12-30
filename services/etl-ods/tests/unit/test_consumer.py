import logging
from http import HTTPStatus

import pytest
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from requests_mock import Mocker as RequestsMock

from consumer.consumer import (
    RequestProcessingError,
    process_message_and_send_request,
)


def test_process_message_and_send_request_success(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful PUT request with informational OperationOutcome."""
    mock_response = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "information",
                "code": "informational",
                "diagnostics": "Organization updated successfully",
            }
        ],
        "status_code": 200,
    }

    mock_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json=mock_response,
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
    """Test handling of 422 UNPROCESSABLE_ENTITY response (logged but not raised)."""
    mock_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "diagnostics": "Validation failed",
                }
            ],
        },
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
    """Test handling of HTTP errors (500 Internal Server Error)."""
    mock_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json={
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "exception",
                    "diagnostics": "Internal server error",
                }
            ],
        },
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    record = {
        "messageId": "1",
        "path": "uuid",
        "body": {"name": "Organization Name"},
    }
    caplog.set_level(logging.ERROR)

    with pytest.raises(RequestProcessingError) as excinfo:
        process_message_and_send_request(record)

    assert excinfo.value.message_id == "1"
    assert excinfo.value.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    expected_failure_log = OdsETLPipelineLogBase.ETL_CONSUMER_009.value.message.format(
        message_id="1"
    )
    assert expected_failure_log in caplog.text
    assert mock_call.called_once
    assert mock_call.last_request.path == "/organization/uuid"


def test_process_message_and_send_request_with_non_operation_outcome(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test successful PUT request with non-OperationOutcome response."""
    mock_response = {
        "resourceType": "Organization",
        "id": "uuid",
        "name": "Organization Name",
        "status_code": 200,
    }

    mock_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json=mock_response,
    )

    record = {
        "messageId": "1",
        "path": "uuid",
        "body": {"name": "Organization Name"},
    }

    process_message_and_send_request(record)

    expected_success_log = OdsETLPipelineLogBase.ETL_CONSUMER_007.value.message.format(
        status_code=200
    )
    assert expected_success_log in caplog.text
    assert mock_call.called_once


def test_process_message_and_send_request_with_string_body_and_correlation_id(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test processing message with string body format (from SQS) and correlation ID."""
    mock_response = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "information",
                "code": "informational",
                "diagnostics": "Success",
            }
        ],
        "status_code": 200,
    }

    requests_mock.put(
        "http://test-apim-api/Organization/test-uuid-123",
        json=mock_response,
    )

    # Simulate SQS message format with double-encoded JSON and correlation_id
    record = {
        "messageId": "msg-123",
        "body": '"{\\"path\\": \\"test-uuid-123\\", \\"body\\": {\\"name\\": \\"Test Org\\"}, \\"correlation_id\\": \\"corr-id-456\\"}"',
    }

    process_message_and_send_request(record)

    expected_success_log = OdsETLPipelineLogBase.ETL_CONSUMER_007.value.message.format(
        status_code=200
    )
    assert expected_success_log in caplog.text
