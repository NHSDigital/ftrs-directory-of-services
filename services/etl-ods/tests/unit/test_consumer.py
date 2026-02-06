import logging
import os
from http import HTTPStatus
from typing import Callable
from unittest.mock import MagicMock, patch

import pytest
import rsa
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from common import auth
from consumer.consumer import (
    RequestProcessingError,
    _handle_records,
    consumer_lambda_handler,
    process_message_and_send_request,
)

RSA_PRIVATE_KEY = None
RSA_PUBLIC_KEY = None


def setup_rsa_keys() -> None:
    """Generate RSA key pair for testing."""
    global RSA_PRIVATE_KEY, RSA_PUBLIC_KEY  # noqa: PLW0603
    if not RSA_PRIVATE_KEY or not RSA_PUBLIC_KEY:
        key = rsa.newkeys(2048)
        RSA_PRIVATE_KEY = key[1].save_pkcs1().decode("utf-8")
        RSA_PUBLIC_KEY = key[0].save_pkcs1().decode("utf-8")


@pytest.fixture
def mock_environment() -> None:
    """Set up mock environment variables."""
    setup_rsa_keys()
    env_vars = {
        "LOCAL_API_KEY": "test-api-key",
        "LOCAL_PRIVATE_KEY": RSA_PRIVATE_KEY,
        "LOCAL_KID": "test-kid",
        "LOCAL_TOKEN_URL": "https://test-token-url.com/token",
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
@patch.dict(
    os.environ,
    {
        "ENVIRONMENT": "local",
        "AWS_REGION": "eu-west-2",
        "PROJECT_NAME": "ftrs",
    },
)
def jwt_authenticator(
    mock_environment: Callable, mocker: MockerFixture
) -> auth.JWTAuthenticator:
    """Create a JWT authenticator instance for testing."""
    auth._jwt_authenticator = None
    return auth.get_jwt_authenticator()


@patch("consumer.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_success(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    event = {
        "Records": [
            {
                "messageId": "1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test1",
                "body": {"key": "value1"},
            },
            {
                "messageId": "2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test2",
                "body": {"key": "value2"},
            },
        ]
    }

    response = consumer_lambda_handler(event, {})

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


@patch("consumer.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_no_event_data(mock_process_message: MagicMock) -> None:
    consumer_lambda_handler({}, {})

    assert str(mock_process_message.call_count) == "0"


@patch("consumer.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_failure(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    event = {
        "Records": [
            {
                "messageId": "1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test1",
                "body": {"key": "value1"},
            },
            {
                "messageId": "2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test2",
                "body": {"key": "value2"},
            },
        ]
    }

    mock_process_message.side_effect = [Exception("Test exception"), None]

    response = consumer_lambda_handler(event, {})

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
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    event = {
        "Records": [
            {
                "messageId": "1",
                "attributes": {"ApproximateReceiveCount": "1"},
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


@patch("consumer.consumer.process_message_and_send_request")
def test__records_handler(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    records = [
        {
            "messageId": "1",
            "attributes": {"ApproximateReceiveCount": "1"},
            "path": "test1",
            "body": {"key": "value1"},
        },
        {
            "messageId": "2",
            "attributes": {"ApproximateReceiveCount": "1"},
            "path": "test2",
            "body": {"key": "value2"},
        },
    ]

    batch_item_failures, successful_count, failed_count = _handle_records(records)

    assert batch_item_failures == []
    assert str(successful_count) == "2"
    assert failed_count == 0

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


@patch("consumer.consumer.process_message_and_send_request")
def test__records_handler_failure(
    mock_process_message: MagicMock,
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    records = [
        {
            "messageId": "1",
            "attributes": {"ApproximateReceiveCount": "1"},
            "path": "test1",
            "body": {"key": "value1"},
        },
        {
            "messageId": "2",
            "attributes": {"ApproximateReceiveCount": "1"},
            "path": "test2",
            "body": {"key": "value2"},
        },
    ]

    mock_process_message.side_effect = [Exception("Test exception"), None]

    batch_item_failures, successful_count, failed_count = _handle_records(records)

    assert batch_item_failures == [{"itemIdentifier": "1"}]
    assert successful_count == 1
    assert failed_count == 1
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
def test_record_handler_handle_missing_message_parameters(
    path: str,
    body: dict,
    caplog: pytest.LogCaptureFixture,
    mocker: MockerFixture,
) -> None:
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    records = [
        {
            "messageId": "1",
            "attributes": {"ApproximateReceiveCount": "1"},
            "path": path,
            "body": body,
        }
    ]

    batch_item_failures, successful_count, failed_count = _handle_records(records)

    assert batch_item_failures == [{"itemIdentifier": "1"}]
    assert successful_count == 0
    assert failed_count == 1

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
    jwt_authenticator: auth.JWTAuthenticator,
) -> None:
    """Test successful PUT request with informational OperationOutcome."""
    mock_put_response = {
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

    mock_put_call = requests_mock.put(
        "http://test-apim-api/Organization/uuid",
        json=mock_put_response,
    )
    mock_post_call = requests_mock.post(
        "https://test-token-url.com/token",
        json={"access_token": "test-bearer-token"},
    )

    record = {
        "messageId": "1",
        "body": '{"path": "uuid", "body": {"name": "Organization Name"}}',
    }

    process_message_and_send_request(record)

    expected_success_log = OdsETLPipelineLogBase.ETL_CONSUMER_007.value.message.format(
        status_code=200
    )
    assert expected_success_log in caplog.text
    assert mock_post_call.called_once
    assert mock_put_call.called_once
    assert mock_put_call.last_request.path == "/organization/uuid"
    assert mock_put_call.last_request.json() == {"name": "Organization Name"}


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

    # Simulate SQS message format with single-encoded JSON and correlation_id
    record = {
        "messageId": "msg-123",
        "body": '{"path": "test-uuid-123", "body": {"name": "Test Org"}, "correlation_id": "corr-id-456"}',
    }

    process_message_and_send_request(record)

    expected_success_log = OdsETLPipelineLogBase.ETL_CONSUMER_007.value.message.format(
        status_code=200
    )
    assert expected_success_log in caplog.text


@patch("consumer.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_logs_start_and_complete(
    mock_process_message: MagicMock,
    mocker: MockerFixture,
) -> None:
    """Test that consumer logs START and BATCH_COMPLETE events with metrics."""
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    mock_logger = mocker.patch("consumer.consumer.ods_consumer_logger")

    event = {
        "Records": [
            {
                "messageId": "1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test1",
                "body": {"key": "value1"},
            },
            {
                "messageId": "2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test2",
                "body": {"key": "value2"},
            },
        ]
    }

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == []

    # Verify START log was called
    start_call = [
        call
        for call in mock_logger.log.call_args_list
        if call[0][0].name == "ETL_CONSUMER_START"
    ]
    assert len(start_call) == 1
    assert start_call[0][1]["lambda_name"] == "etl-ods-consumer"

    # Verify BATCH_COMPLETE log was called with metrics
    complete_call = [
        call
        for call in mock_logger.log.call_args_list
        if call[0][0].name == "ETL_CONSUMER_BATCH_COMPLETE"
    ]
    assert len(complete_call) == 1
    assert complete_call[0][1]["lambda_name"] == "etl-ods-consumer"
    assert "duration_ms" in complete_call[0][1]
    assert str(complete_call[0][1]["total_records"]) == "2"
    assert str(complete_call[0][1]["successful_count"]) == "2"
    assert complete_call[0][1]["failed_count"] == 0
    assert complete_call[0][1]["batch_status"] == "completed"


@patch("consumer.consumer.process_message_and_send_request")
def test_consumer_lambda_handler_logs_partial_failure(
    mock_process_message: MagicMock,
    mocker: MockerFixture,
) -> None:
    """Test that consumer logs BATCH_COMPLETE with failures correctly."""
    mocker.patch.dict("os.environ", {"MAX_RECEIVE_COUNT": "3"})
    mock_logger = mocker.patch("consumer.consumer.ods_consumer_logger")

    # First message fails, second succeeds
    mock_process_message.side_effect = [Exception("Test exception"), None]

    event = {
        "Records": [
            {
                "messageId": "1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test1",
                "body": {"key": "value1"},
            },
            {
                "messageId": "2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "path": "test2",
                "body": {"key": "value2"},
            },
        ]
    }

    response = consumer_lambda_handler(event, {})

    assert response["batchItemFailures"] == [{"itemIdentifier": "1"}]

    # Verify BATCH_COMPLETE log shows partial failure
    complete_call = [
        call
        for call in mock_logger.log.call_args_list
        if call[0][0].name == "ETL_CONSUMER_BATCH_COMPLETE"
    ]
    assert len(complete_call) == 1
    assert str(complete_call[0][1]["total_records"]) == "2"
    assert str(complete_call[0][1]["successful_count"]) == "1"
    assert str(complete_call[0][1]["failed_count"]) == "1"
    assert complete_call[0][1]["batch_status"] == "completed_with_failures"
