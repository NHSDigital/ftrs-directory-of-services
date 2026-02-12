import json
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from pytest_mock import MockerFixture

from common.exceptions import (
    PermanentProcessingError,
    RetryableProcessingError,
)
from consumer.consumer import (
    consumer_lambda_handler,
    process_message_and_send_request,
)


@pytest.fixture(scope="module")
def sample_sqs_record() -> dict:
    """File-scoped fixture for sample SQS record."""
    return {
        "messageId": "test-message-id",
        "attributes": {"ApproximateReceiveCount": "1"},
        "body": json.dumps(
            {
                "path": "ORG123",
                "body": {"name": "Test Organization", "status": "active"},
            }
        ),
    }


@pytest.fixture(scope="module")
def sample_event_single_record() -> dict:
    """File-scoped fixture for Lambda event with single record."""
    return {
        "Records": [
            {
                "messageId": "msg-1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"path": "ORG001", "body": {"name": "Org 1"}}),
            }
        ]
    }


@pytest.fixture(scope="module")
def sample_event_multiple_records() -> dict:
    return {
        "Records": [
            {
                "messageId": "msg-1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"path": "ORG001", "body": {"name": "Org 1"}}),
            },
            {
                "messageId": "msg-2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"path": "ORG002", "body": {"name": "Org 2"}}),
            },
        ]
    }


@pytest.fixture
def mock_consumer_dependencies(mocker: MockerFixture) -> dict[str, Any]:
    """Fixture to set up common mock dependencies for process_message_and_send_request."""
    mocks = {
        "extract_metadata": mocker.patch("consumer.consumer.extract_record_metadata"),
        "validate_fields": mocker.patch("consumer.consumer.validate_required_fields"),
        "get_url": mocker.patch("consumer.consumer.get_base_apim_api_url"),
        "make_request": mocker.patch("consumer.consumer.make_apim_request"),
        "logger": mocker.patch("consumer.consumer.ods_consumer_logger"),
    }

    # Set common default return values
    mocks["extract_metadata"].return_value = {
        "body": {"path": "ORG123", "body": {"name": "Test"}},
        "message_id": "test-message-id",
    }
    mocks["get_url"].return_value = "http://test-apim-api"
    mocks["make_request"].return_value = {"status_code": 200}

    return mocks


@pytest.fixture
def sample_record() -> dict:
    """Fixture for a standard test record."""
    return {
        "messageId": "test-message-id",
        "attributes": {"ApproximateReceiveCount": "1"},
        "body": json.dumps({"path": "ORG123", "body": {"name": "Test"}}),
    }


def create_http_error(status_code: int, message: str) -> requests.HTTPError:
    """Helper function to create HTTP errors with proper response."""
    http_error = requests.HTTPError(message)
    mock_response = MagicMock()
    mock_response.status_code = status_code
    http_error.response = mock_response
    return http_error


class TestProcessMessageAndSendRequest:
    """Test process_message_and_send_request function."""

    def test_successful_processing(
        self, mock_consumer_dependencies: dict, sample_sqs_record: dict
    ) -> None:
        """Test successful message processing and APIM request."""
        mocks = mock_consumer_dependencies
        mocks["extract_metadata"].return_value = {
            "body": {"path": "ORG123", "body": {"name": "Test Organization"}},
            "message_id": "test-message-id",
        }

        process_message_and_send_request(sample_sqs_record)

        # Verify APIM request was made correctly
        mocks["make_request"].assert_called_once_with(
            "http://test-apim-api/Organization/ORG123",
            method="PUT",
            json={"name": "Test Organization"},
        )

        # Verify success was logged
        mocks["logger"].log.assert_called_once()
        call_args = mocks["logger"].log.call_args[1]
        assert call_args["organization_id"] == "ORG123"
        assert str(call_args["status_code"]) == "200"

    @pytest.mark.parametrize(
        "missing_field,body_data",
        [
            ("body", {"path": "ORG123"}),
            ("path", {"body": {"name": "Test Organization"}}),
        ],
    )
    def test_missing_required_fields_raises_message_integrity_error(
        self, missing_field: str, body_data: dict
    ) -> None:
        """Test that missing required fields raises PermanentProcessingError."""
        record = {
            "messageId": "test-message-id",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": json.dumps(body_data),
        }

        with pytest.raises(PermanentProcessingError) as exc_info:
            process_message_and_send_request(record)

        error = exc_info.value
        assert error.message_id == "test-message-id"
        assert str(error.status_code) == "400"
        assert missing_field in error.response_text

    @pytest.mark.parametrize(
        "status_code,error_message,expected_exception",
        [
            (429, "429 Too Many Requests", RetryableProcessingError),
            (404, "404 Not Found", PermanentProcessingError),
            (400, "400 Bad Request", PermanentProcessingError),
            (500, "500 Internal Server Error", RetryableProcessingError),
            (503, "503 Service Unavailable", RetryableProcessingError),
        ],
    )
    def test_http_errors_handled_by_centralized_error_handling(
        self,
        mock_consumer_dependencies: dict,
        sample_record: dict,
        status_code: int,
        error_message: str,
        expected_exception: type,
    ) -> None:
        """Test that HTTP errors are handled by centralized error handling."""

        mocks = mock_consumer_dependencies
        http_error = create_http_error(status_code, error_message)
        mocks["make_request"].side_effect = http_error

        # HTTP errors should now be handled by centralized error handling
        with pytest.raises(expected_exception):
            process_message_and_send_request(sample_record)

    def test_successful_processing_with_different_org_id(
        self, mock_consumer_dependencies: dict
    ) -> None:
        """Test successful processing with different organization ID."""
        mocks = mock_consumer_dependencies
        record = {
            "messageId": "test-message-id",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": json.dumps({"path": "ORG789", "body": {"name": "Another Org"}}),
        }

        # Override the mock to return the correct metadata for this test
        mocks["extract_metadata"].return_value = {
            "body": {"path": "ORG789", "body": {"name": "Another Org"}},
            "message_id": "test-message-id",
        }

        process_message_and_send_request(record)

        # Verify APIM request was made correctly
        mocks["make_request"].assert_called_once_with(
            "http://test-apim-api/Organization/ORG789",
            method="PUT",
            json={"name": "Another Org"},
        )

    def test_message_integrity_error_is_reraised(
        self, mock_consumer_dependencies: dict, sample_record: dict
    ) -> None:
        """Test that PermanentProcessingError is re-raised for proper handling."""
        mocks = mock_consumer_dependencies
        mocks["validate_fields"].side_effect = PermanentProcessingError(
            message_id="test-msg",
            status_code=400,
            response_text="Test error",
        )

        with pytest.raises(PermanentProcessingError) as exc_info:
            process_message_and_send_request(sample_record)

        assert exc_info.value.message_id == "test-msg"
        assert str(exc_info.value.status_code) == "400"

    def test_permanent_processing_error_for_404(
        self, mock_consumer_dependencies: dict, sample_record: dict
    ) -> None:
        """Test that 404 HTTP errors are converted to PermanentProcessingError."""
        mocks = mock_consumer_dependencies
        http_error = create_http_error(404, "404 Not Found")
        mocks["make_request"].side_effect = http_error

        # 404 errors should be converted to PermanentProcessingError by centralized error handling
        with pytest.raises(PermanentProcessingError):
            process_message_and_send_request(sample_record)

    @pytest.mark.parametrize(
        "exception_class,init_kwargs",
        [
            (
                PermanentProcessingError,
                {
                    "message_id": "test-message-id",
                    "status_code": 422,
                    "response_text": "Unprocessable Entity",
                },
            ),
            (
                PermanentProcessingError,
                {
                    "message_id": "test-message-id",
                    "status_code": 400,
                    "response_text": "Invalid data format",
                },
            ),
        ],
    )
    def test_exceptions_from_apim_request_are_reraised(
        self,
        mock_consumer_dependencies: dict,
        sample_record: dict,
        exception_class: type,
        init_kwargs: dict,
    ) -> None:
        """Test that exceptions raised directly from make_apim_request are re-raised via except block."""
        mocks = mock_consumer_dependencies
        mocks["make_request"].side_effect = exception_class(**init_kwargs)

        with pytest.raises(exception_class) as exc_info:
            process_message_and_send_request(sample_record)

        # Verify exception details
        assert exc_info.value.message_id == "test-message-id"

    def test_constructs_correct_api_url(self, mock_consumer_dependencies: dict) -> None:
        """Test that API URL is constructed correctly with organization ID."""
        mocks = mock_consumer_dependencies
        mocks["extract_metadata"].return_value = {
            "body": {"path": "ORG-XYZ-789", "body": {"name": "Test"}},
            "message_id": "test-message-id",
        }
        mocks["get_url"].return_value = "https://api.example.com"

        record = {
            "messageId": "test-message-id",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": json.dumps({"path": "ORG-XYZ-789", "body": {"name": "Test"}}),
        }

        process_message_and_send_request(record)

        mocks["make_request"].assert_called_once_with(
            "https://api.example.com/Organization/ORG-XYZ-789",
            method="PUT",
            json={"name": "Test"},
        )


class TestConsumerLambdaHandler:
    """Test consumer_lambda_handler function."""

    @pytest.fixture(autouse=True)
    def setup_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Set up environment variables for all tests in this class."""
        monkeypatch.setenv("MAX_RECEIVE_COUNT", "3")

    @pytest.fixture
    def mock_lambda_dependencies(self, mocker: MockerFixture) -> dict[str, Any]:
        """Fixture for common lambda handler dependencies."""
        return {
            "process_sqs": mocker.patch("common.sqs_processor.process_sqs_records"),
            "extract_correlation": mocker.patch(
                "common.sqs_processor.extract_correlation_id_from_sqs_records"
            ),
            "setup_context": mocker.patch("common.sqs_processor.setup_request_context"),
        }

    def test_handler_with_empty_event(self) -> None:
        """Test handler returns empty failures for empty event."""
        response = consumer_lambda_handler({}, {})
        assert response["batchItemFailures"] == []

    def test_handler_with_no_records(self) -> None:
        """Test handler with event missing Records key."""
        response = consumer_lambda_handler({}, {})
        assert response["batchItemFailures"] == []

    def test_handler_successful_processing(
        self,
        mock_lambda_dependencies: dict,
        sample_event_single_record: dict,
    ) -> None:
        """Test successful processing of consumer messages."""
        mocks = mock_lambda_dependencies
        mocks["process_sqs"].return_value = []
        mocks["extract_correlation"].return_value = "test-correlation"

        response = consumer_lambda_handler(sample_event_single_record, {})

        assert response["batchItemFailures"] == []

    def test_handler_with_multiple_records(
        self,
        mock_lambda_dependencies: dict,
        sample_event_multiple_records: dict,
    ) -> None:
        """Test handler with multiple records."""
        mocks = mock_lambda_dependencies
        mocks["process_sqs"].return_value = []
        mocks["extract_correlation"].return_value = "test-correlation"

        response = consumer_lambda_handler(sample_event_multiple_records, {})

        assert response["batchItemFailures"] == []

    def test_handler_with_failures(
        self,
        mock_lambda_dependencies: dict,
        sample_event_multiple_records: dict,
    ) -> None:
        """Test handler with processing failures."""
        mocks = mock_lambda_dependencies
        mocks["process_sqs"].return_value = [{"itemIdentifier": "msg-2"}]
        mocks["extract_correlation"].return_value = "test-correlation"

        response = consumer_lambda_handler(sample_event_multiple_records, {})

        assert response["batchItemFailures"] == [{"itemIdentifier": "msg-2"}]

    def test_handler_integration_with_process_function(
        self,
        mocker: MockerFixture,
        sample_event_single_record: dict,
    ) -> None:
        """Test handler integration with actual process function."""
        # Mock dependencies of process_message_and_send_request
        mock_extract = mocker.patch("consumer.consumer.extract_record_metadata")
        mocker.patch("consumer.consumer.validate_required_fields")
        mock_get_url = mocker.patch("consumer.consumer.get_base_apim_api_url")
        mock_make_request = mocker.patch("consumer.consumer.make_apim_request")
        mocker.patch("consumer.consumer.ods_consumer_logger")

        mock_extract.return_value = {
            "body": {"path": "ORG001", "body": {"name": "Org 1"}},
            "message_id": "msg-1",
        }
        mock_get_url.return_value = "http://test-api"
        mock_make_request.return_value = {"status_code": 200}

        mocker.patch(
            "common.sqs_processor.extract_correlation_id_from_sqs_records",
            return_value="test-correlation",
        )
        mocker.patch("common.sqs_processor.setup_request_context")

        response = consumer_lambda_handler(sample_event_single_record, {})

        assert response["batchItemFailures"] == []
        mock_make_request.assert_called_once()

    def test_handler_with_mixed_success_and_failure(
        self, mocker: MockerFixture
    ) -> None:
        """Test handler with some records succeeding and some failing."""

        def conditional_extract(record: dict) -> dict:
            msg_id = record["messageId"]
            if msg_id == "msg-fail":
                err_msg = "Processing failed"
                raise ValueError(err_msg)
            return {
                "body": {"path": msg_id, "body": {"name": "Test"}},
                "message_id": msg_id,
            }

        mocker.patch(
            "consumer.consumer.extract_record_metadata", side_effect=conditional_extract
        )
        mocker.patch("consumer.consumer.validate_required_fields")
        mock_get_url = mocker.patch("consumer.consumer.get_base_apim_api_url")
        mock_make_request = mocker.patch("consumer.consumer.make_apim_request")
        mocker.patch("consumer.consumer.ods_consumer_logger")

        mock_get_url.return_value = "http://test-api"
        mock_make_request.return_value = {"status_code": 200}

        mocker.patch(
            "common.sqs_processor.extract_correlation_id_from_sqs_records",
            return_value="test-correlation",
        )
        mocker.patch("common.sqs_processor.setup_request_context")

        event = {
            "Records": [
                {
                    "messageId": "msg-success",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"path": "ORG001", "body": {"name": "Org 1"}}),
                },
                {
                    "messageId": "msg-fail",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"path": "ORG002", "body": {"name": "Org 2"}}),
                },
            ]
        }

        response = consumer_lambda_handler(event, {})

        # Should return failed message for retry
        assert len(response["batchItemFailures"]) == 1
        assert response["batchItemFailures"][0]["itemIdentifier"] == "msg-fail"

    def test_handler_context_setup(
        self,
        mock_lambda_dependencies: dict,
        sample_event_single_record: dict,
    ) -> None:
        """Test that handler properly sets up request context."""
        mocks = mock_lambda_dependencies
        mocks["process_sqs"].return_value = []
        mocks["extract_correlation"].return_value = "correlation-123"

        context = {"awsRequestId": "request-123"}

        consumer_lambda_handler(sample_event_single_record, context)

        # Verify correlation ID extraction
        mocks["extract_correlation"].assert_called_once()

        # Verify context setup
        mocks["setup_context"].assert_called_once()
        call_args = mocks["setup_context"].call_args[0]
        assert call_args[0] == "correlation-123"
        assert call_args[1] == context
