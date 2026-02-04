import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture

from common.exceptions import (
    PermanentProcessingError,
    RetryableProcessingError,
)
from common.sqs_processor import (
    _add_to_batch_failures,
    _log_processing_start,
    _log_processing_success,
    create_sqs_lambda_handler,
    extract_record_metadata,
    process_sqs_records,
    validate_required_fields,
)


@pytest.fixture(scope="module")
def mock_logger() -> MagicMock:
    """File-scoped fixture for mock logger instance."""
    return MagicMock(spec=Logger)


@pytest.fixture(scope="module")
def sample_sqs_record() -> dict:
    """File-scoped fixture for a sample SQS record."""
    return {
        "messageId": "test-message-123",
        "attributes": {"ApproximateReceiveCount": "1"},
        "body": json.dumps({"test": "data"}),
    }


@pytest.fixture(scope="module")
def sample_lambda_context() -> dict:
    """File-scoped fixture for a sample Lambda context."""
    return {"awsRequestId": "test-request-id"}


class TestExtractRecordMetadata:
    """Test extract_record_metadata function."""

    def test_basic_metadata_extraction(self) -> None:
        """Test basic metadata extraction from SQS record with JSON string body."""
        record = {
            "messageId": "test-message-123",
            "attributes": {"ApproximateReceiveCount": "2"},
            "body": json.dumps({"test": "data"}),
        }

        result = extract_record_metadata(record)

        assert result["message_id"] == "test-message-123"
        assert str(result["receive_count"]) == "2"
        assert result["body"] == {"test": "data"}

    def test_already_parsed_body(self) -> None:
        """Test handling when body is already parsed (dict)."""
        record = {
            "messageId": "test-message-456",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": {"already": "parsed"},
        }

        result = extract_record_metadata(record)

        assert result["message_id"] == "test-message-456"
        assert result["receive_count"] == 1
        assert result["body"] == {"already": "parsed"}

    def test_missing_body_handling(self) -> None:
        """Test handling when body is missing."""
        record = {
            "messageId": "test-message-789",
            "attributes": {"ApproximateReceiveCount": "1"},
        }

        result = extract_record_metadata(record)

        assert result["message_id"] == "test-message-789"
        assert result["receive_count"] == 1
        assert result["body"] == {}

    def test_malformed_json_body_raises_unrecoverable_error(self) -> None:
        """Test handling when JSON body is malformed raises PermanentProcessingError."""
        record = {
            "messageId": "test-malformed",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": "{invalid json",
        }

        with pytest.raises(PermanentProcessingError) as exc_info:
            extract_record_metadata(record)

        error = exc_info.value
        assert error.message_id == "test-malformed"
        assert str(error.status_code) == "400"
        assert "Failed to parse JSON" in error.response_text

    def test_none_body_handling(self) -> None:
        """Test handling when body is None."""
        record = {
            "messageId": "test-message-123",
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": None,
        }

        result = extract_record_metadata(record)

        assert result["message_id"] == "test-message-123"
        assert result["receive_count"] == 1
        assert result["body"] == {}

    def test_default_message_id_when_missing(self) -> None:
        """Test default message ID when not present in record."""
        record = {
            "attributes": {"ApproximateReceiveCount": "1"},
            "body": json.dumps({"test": "data"}),
        }

        result = extract_record_metadata(record)

        assert result["message_id"] == "unknown"
        assert result["receive_count"] == 1

    def test_various_receive_counts(self) -> None:
        """Test extraction with various receive count values."""
        test_cases = [0, 1, 5, 10]

        for receive_count in test_cases:
            record = {
                "messageId": f"test-{receive_count}",
                "attributes": {"ApproximateReceiveCount": str(receive_count)},
                "body": json.dumps({"test": "data"}),
            }

            result = extract_record_metadata(record)
            assert result["receive_count"] == receive_count


class TestLogProcessingStart:
    """Test _log_processing_start function."""

    def test_logs_processing_start(self, mock_logger: MagicMock) -> None:
        """Test that processing start is logged correctly."""
        mock_logger.reset_mock()
        message_id = "test-msg-123"
        total_records = 5

        _log_processing_start(mock_logger, message_id, total_records)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_003,
            message_id=message_id,
            total_records=total_records,
        )

    def test_logs_with_different_record_counts(self, mock_logger: MagicMock) -> None:
        """Test logging with various record counts."""
        test_cases = [1, 10, 100]

        for count in test_cases:
            mock_logger.reset_mock()
            _log_processing_start(mock_logger, f"msg-{count}", count)

            mock_logger.log.assert_called_once()
            call_args = mock_logger.log.call_args[1]
            assert call_args["total_records"] == count


class TestLogProcessingSuccess:
    """Test _log_processing_success function."""

    def test_logs_processing_success(self, mock_logger: MagicMock) -> None:
        """Test that processing success is logged correctly."""
        mock_logger.reset_mock()
        message_id = "test-msg-456"

        _log_processing_success(mock_logger, message_id)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_004,
            message_id=message_id,
        )


class TestAddToBatchFailures:
    """Test _add_to_batch_failures function."""

    def test_adds_message_to_failures(self, mock_logger: MagicMock) -> None:
        """Test that message is added to batch failures list."""
        mock_logger.reset_mock()
        batch_item_failures = []
        message_id = "test-msg"

        _add_to_batch_failures(message_id, batch_item_failures)

        assert len(batch_item_failures) == 1
        assert batch_item_failures[0]["itemIdentifier"] == message_id

    def test_adds_multiple_messages(self, mock_logger: MagicMock) -> None:
        """Test that multiple messages can be added to failures list."""
        mock_logger.reset_mock()
        batch_item_failures = []
        message_id_1 = "test-msg-1"
        message_id_2 = "test-msg-2"

        _add_to_batch_failures(message_id_1, batch_item_failures)
        _add_to_batch_failures(message_id_2, batch_item_failures)

        assert str(len(batch_item_failures)) == "2"
        assert batch_item_failures[0]["itemIdentifier"] == message_id_1
        assert batch_item_failures[1]["itemIdentifier"] == message_id_2


class TestValidateRequiredFields:
    """Test validate_required_fields function."""

    def test_valid_data_with_all_fields(self, mock_logger: MagicMock) -> None:
        """Test validation with all required fields present."""
        mock_logger.reset_mock()
        data = {
            "path": "test-path",
            "body": {"name": "Test"},
            "optional_field": "value",
        }
        required_fields = ["path", "body"]

        validate_required_fields(data, required_fields, "test-msg", mock_logger)

        # Should not log or raise exception
        mock_logger.log.assert_not_called()

    def test_validation_with_empty_required_fields_list(
        self, mock_logger: MagicMock
    ) -> None:
        """Test validation with no required fields."""
        mock_logger.reset_mock()
        data = {"any": "data"}
        required_fields = []

        validate_required_fields(data, required_fields, "test-msg", mock_logger)

        mock_logger.log.assert_not_called()

    def test_validation_logs_and_raises_for_missing_field(
        self, mock_logger: MagicMock
    ) -> None:
        """Test validation logs error and raises PermanentProcessingError for missing field."""
        mock_logger.reset_mock()
        data = {"path": "test-path"}
        required_fields = ["path", "body"]

        with pytest.raises(PermanentProcessingError) as exc_info:
            validate_required_fields(data, required_fields, "test-msg", mock_logger)

        # Verify error was logged
        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_007,
            message_id="test-msg",
        )

        # Verify correct exception details
        error = exc_info.value
        assert error.message_id == "test-msg"
        assert str(error.status_code) == "400"
        assert "body" in error.response_text

    def test_multiple_missing_fields(self, mock_logger: MagicMock) -> None:
        """Test validation with multiple missing fields."""
        mock_logger.reset_mock()
        data = {"other_field": "value"}
        required_fields = ["path", "body", "method"]

        with pytest.raises(PermanentProcessingError) as exc_info:
            validate_required_fields(data, required_fields, "test-msg", mock_logger)

        error = exc_info.value
        assert "path" in error.response_text
        assert "body" in error.response_text
        assert "method" in error.response_text

    def test_none_value_field(self, mock_logger: MagicMock) -> None:
        """Test validation when required field is None."""
        mock_logger.reset_mock()
        data = {"path": "test-path", "body": None}
        required_fields = ["path", "body"]

        with pytest.raises(PermanentProcessingError):
            validate_required_fields(data, required_fields, "test-msg", mock_logger)

    def test_empty_string_field(self, mock_logger: MagicMock) -> None:
        """Test validation fails for empty string field."""
        mock_logger.reset_mock()
        data = {"path": "", "body": {"test": "data"}}
        required_fields = ["path", "body"]

        with pytest.raises(PermanentProcessingError):
            validate_required_fields(data, required_fields, "test-message", mock_logger)

    def test_zero_value_is_valid(self, mock_logger: MagicMock) -> None:
        """Test that zero value is considered valid for required field."""
        mock_logger.reset_mock()
        data = {"count": 0, "body": {"test": "data"}}
        required_fields = ["count", "body"]

        # Should not raise - 0 is a valid value
        validate_required_fields(data, required_fields, "test-msg", mock_logger)


class TestProcessSqsRecords:
    """Test process_sqs_records function."""

    @staticmethod
    def success_processor(record: dict) -> str:
        """Standard success processor that processes any record."""
        return f"processed_{record['messageId']}"

    @staticmethod
    def failure_processor(record: dict) -> str:
        """Standard failure processor that always raises ValueError."""
        err_msg = "Processing failed"
        raise ValueError(err_msg)

    def test_successful_processing(
        self, mock_logger: MagicMock, sample_sqs_record: dict
    ) -> None:
        """Test successful processing of all records."""
        mock_logger.reset_mock()

        records = [
            sample_sqs_record,
            {
                "messageId": "msg2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"data": "test2"}),
            },
        ]

        failures = process_sqs_records(records, self.success_processor, mock_logger)

        assert failures == []
        # Should log: 2 start + 2 success = 4 calls
        assert str(mock_logger.log.call_count) == "4"

    def test_message_integrity_error_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test handling of PermanentProcessingError."""
        mock_logger.reset_mock()
        mock_handle_permanent = mocker.patch(
            "common.sqs_processor.handle_permanent_error"
        )

        def raise_integrity_error(record: dict) -> None:
            raise PermanentProcessingError(
                message_id=record["messageId"],
                status_code=400,
                response_text="Test integrity error",
            )

        records = [
            {
                "messageId": "poison-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"test": "data"}),
            }
        ]

        failures = process_sqs_records(records, raise_integrity_error, mock_logger)

        # Should consume permanent errors without retrying
        assert len(failures) == 0
        mock_handle_permanent.assert_called_once()

    def test_permanent_processing_error_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test handling of PermanentProcessingError with 404 does not retry or send to DLQ."""
        mock_logger.reset_mock()
        mock_handle_permanent = mocker.patch(
            "common.sqs_processor.handle_permanent_error"
        )

        def raise_permanent_error(record: dict) -> None:
            raise PermanentProcessingError(
                message_id=record["messageId"],
                status_code=404,
                response_text="Not found",
            )

        records = [
            {
                "messageId": "permanent-error-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"test": "data"}),
            }
        ]

        failures = process_sqs_records(records, raise_permanent_error, mock_logger)

        # Should not retry permanent errors
        assert failures == []
        mock_handle_permanent.assert_called_once()

    def test_unrecoverable_error_400_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test handling of PermanentProcessingError from 400 Bad Request."""
        mock_logger.reset_mock()
        mock_handle_permanent = mocker.patch(
            "common.sqs_processor.handle_permanent_error"
        )

        def raise_unrecoverable_error(record: dict) -> None:
            raise PermanentProcessingError(
                message_id=record["messageId"],
                status_code=400,
                response_text="Bad Request",
            )

        records = [
            {
                "messageId": "unrecoverable-400-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"test": "data"}),
            }
        ]

        failures = process_sqs_records(records, raise_unrecoverable_error, mock_logger)

        # Should consume permanent errors without retrying
        assert len(failures) == 0
        mock_handle_permanent.assert_called_once()

    def test_unrecoverable_error_401_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test handling of PermanentProcessingError with 401."""
        mock_logger.reset_mock()
        mock_handle_permanent = mocker.patch(
            "common.sqs_processor.handle_permanent_error"
        )

        def raise_unrecoverable_error(record: dict) -> None:
            raise PermanentProcessingError(
                message_id=record["messageId"],
                status_code=401,
                response_text="Unauthorized",
            )

        records = [
            {
                "messageId": "unrecoverable-401-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"test": "data"}),
            }
        ]

        failures = process_sqs_records(records, raise_unrecoverable_error, mock_logger)

        # Should consume permanent errors without retrying
        assert len(failures) == 0
        mock_handle_permanent.assert_called_once()

    def test_rate_limit_exception_handling(self, mock_logger: MagicMock) -> None:
        """Test handling of RetryableProcessingError."""
        mock_logger.reset_mock()

        def raise_rate_limit(record: dict) -> None:
            err_msg = "Rate limit exceeded"
            raise RetryableProcessingError(err_msg, status_code=429)

        records = [
            {
                "messageId": "rate_limit_msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"data": "test"}),
            }
        ]

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            failures = process_sqs_records(records, raise_rate_limit, mock_logger)

        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "rate_limit_msg"

    def test_retryable_processing_error_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test handling of RetryableProcessingError retries the message."""
        mock_logger.reset_mock()
        mock_handle_retryable = mocker.patch(
            "common.sqs_processor.handle_retryable_error"
        )

        def raise_retryable_error(record: dict) -> None:
            raise RetryableProcessingError(
                message_id=record["messageId"],
                status_code=503,
                response_text="Service Unavailable",
            )

        records = [
            {
                "messageId": "retryable-error-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"test": "data"}),
            }
        ]

        failures = process_sqs_records(records, raise_retryable_error, mock_logger)

        # Should retry
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "retryable-error-msg"
        mock_handle_retryable.assert_called_once()

    def test_retryable_processing_error_max_receive_count_reached(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test RetryableProcessingError is added to failures even when max receive count reached."""
        mock_logger.reset_mock()
        mock_handle_retryable = mocker.patch(
            "common.sqs_processor.handle_retryable_error"
        )

        def raise_retryable_error(record: dict) -> None:
            raise RetryableProcessingError(
                message_id=record["messageId"],
                status_code=500,
                response_text="Internal Server Error",
            )

        records = [
            {
                "messageId": "retryable-max-msg",
                "attributes": {"ApproximateReceiveCount": "3"},
                "body": json.dumps({"test": "data"}),
            }
        ]

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            failures = process_sqs_records(records, raise_retryable_error, mock_logger)

        # Message is always added to failures; SQS will handle DLQ routing based on maxReceiveCount
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "retryable-max-msg"
        mock_handle_retryable.assert_called_once()

    def test_rate_limit_exception_max_receive_count_reached(
        self, mock_logger: MagicMock
    ) -> None:
        """Test rate limit error is added to failures even when max receive count reached."""
        mock_logger.reset_mock()

        def raise_rate_limit(record: dict) -> None:
            err_msg = "Rate limit exceeded"
            raise RetryableProcessingError(err_msg, status_code=429)

        records = [
            {
                "messageId": "rate_limit_max_msg",
                "attributes": {"ApproximateReceiveCount": "3"},
                "body": json.dumps({"data": "test"}),
            }
        ]

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            failures = process_sqs_records(records, raise_rate_limit, mock_logger)

        # Message is added to failures; SQS will handle DLQ routing
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "rate_limit_max_msg"

    def test_general_exception_handling(self, mock_logger: MagicMock) -> None:
        """Test handling of general exceptions."""
        mock_logger.reset_mock()

        records = [
            {
                "messageId": "error_msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"data": "test"}),
            }
        ]

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            failures = process_sqs_records(records, self.failure_processor, mock_logger)

        # Should return the message as a failure for retry
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "error_msg"

    def test_general_exception_max_receive_count_reached(
        self, mock_logger: MagicMock
    ) -> None:
        """Test general exception is added to failures even when max receive count reached."""
        mock_logger.reset_mock()

        records = [
            {
                "messageId": "persistent_error",
                "attributes": {"ApproximateReceiveCount": "3"},
                "body": json.dumps({"data": "test"}),
            }
        ]

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            failures = process_sqs_records(records, self.failure_processor, mock_logger)

        # Message is added to failures; SQS will handle DLQ routing based on maxReceiveCount
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "persistent_error"

    def test_mixed_success_and_failure(self, mock_logger: MagicMock) -> None:
        """Test processing with mix of successes and failures."""
        mock_logger.reset_mock()

        def conditional_processor(record: dict) -> str:
            if record["messageId"] == "error-msg":
                raise ValueError("Error")
            return f"processed_{record['messageId']}"

        records = [
            {
                "messageId": "success1",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"data": "test1"}),
            },
            {
                "messageId": "error-msg",
                "attributes": {"ApproximateReceiveCount": "2"},
                "body": json.dumps({"data": "test2"}),
            },
            {
                "messageId": "success2",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"data": "test3"}),
            },
        ]

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            failures = process_sqs_records(records, conditional_processor, mock_logger)

        # Should have 1 failure
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "error-msg"

    def test_http_error_404_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test HTTPError with 404 status is handled as permanent error."""
        mock_logger.reset_mock()
        mock_handle_http_error = mocker.patch("common.sqs_processor.handle_http_error")

        def raise_http_404_error(record: dict) -> None:
            response = MagicMock()
            response.status_code = 404
            response.text = "Not Found"
            response.url = "https://api.example.com/resource"

            http_error = requests.exceptions.HTTPError(
                "404 Client Error", response=response
            )
            raise http_error

        records = [
            {
                "messageId": "http-404-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"path": "/test/resource", "data": "test"}),
            }
        ]

        failures = process_sqs_records(records, raise_http_404_error, mock_logger)

        # Should add to batch failures for retry
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "http-404-msg"
        mock_handle_http_error.assert_called_once()

        # Verify handle_http_error was called with correct parameters
        _, call_kwargs = mock_handle_http_error.call_args
        assert call_kwargs["message_id"] == "http-404-msg"
        assert call_kwargs["error_context"] == "/test/resource"

    def test_http_error_422_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test HTTPError with 422 status is handled as unrecoverable error."""
        mock_logger.reset_mock()
        mock_handle_http_error = mocker.patch("common.sqs_processor.handle_http_error")

        def raise_http_422_error(record: dict) -> None:
            response = MagicMock()
            response.status_code = 422
            response.text = "Unprocessable Entity"
            response.url = "https://api.example.com/resource"

            http_error = requests.exceptions.HTTPError(
                "422 Client Error", response=response
            )
            raise http_error

        records = [
            {
                "messageId": "http-422-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"path": "/test/validation", "data": "test"}),
            }
        ]

        failures = process_sqs_records(records, raise_http_422_error, mock_logger)

        # Should add to batch failures for retry
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "http-422-msg"
        mock_handle_http_error.assert_called_once()

        # Verify handle_http_error was called with correct parameters
        _, call_kwargs = mock_handle_http_error.call_args
        assert call_kwargs["message_id"] == "http-422-msg"
        assert call_kwargs["error_context"] == "/test/validation"

    def test_http_error_500_handling(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test HTTPError with 500 status is handled as retryable error."""
        mock_logger.reset_mock()
        mock_handle_http_error = mocker.patch("common.sqs_processor.handle_http_error")

        def raise_http_500_error(record: dict) -> None:
            response = MagicMock()
            response.status_code = 500
            response.text = "Internal Server Error"
            response.url = "https://api.example.com/resource"

            http_error = requests.exceptions.HTTPError(
                "500 Server Error", response=response
            )
            raise http_error

        records = [
            {
                "messageId": "http-500-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps({"path": "/test/server", "data": "test"}),
            }
        ]

        failures = process_sqs_records(records, raise_http_500_error, mock_logger)

        # Should add to batch failures for retry
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "http-500-msg"
        mock_handle_http_error.assert_called_once()

        # Verify handle_http_error was called with correct parameters
        _, call_kwargs = mock_handle_http_error.call_args
        assert call_kwargs["message_id"] == "http-500-msg"
        assert call_kwargs["error_context"] == "/test/server"

    def test_http_error_with_invalid_json_body(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test HTTPError handling with invalid JSON in record body."""
        mock_logger.reset_mock()
        mock_handle_http_error = mocker.patch("common.sqs_processor.handle_http_error")

        def raise_http_error(record: dict) -> None:
            response = MagicMock()
            response.status_code = 400
            response.text = "Bad Request"
            response.url = "https://api.example.com/resource"

            http_error = requests.exceptions.HTTPError(
                "400 Client Error", response=response
            )
            raise http_error

        records = [
            {
                "messageId": "http-invalid-json-msg",
                "attributes": {"ApproximateReceiveCount": "1"},
                "body": json.dumps(
                    {"no_path_field": "value"}
                ),  # Valid JSON but no 'path' field
            }
        ]

        failures = process_sqs_records(records, raise_http_error, mock_logger)

        # Should add to batch failures for retry
        assert len(failures) == 1
        assert failures[0]["itemIdentifier"] == "http-invalid-json-msg"
        mock_handle_http_error.assert_called_once()

        # Verify handle_http_error was called with "unknown" context due to missing path field
        _, call_kwargs = mock_handle_http_error.call_args
        assert call_kwargs["message_id"] == "http-invalid-json-msg"
        assert call_kwargs["error_context"] == "unknown"
        assert call_kwargs["error_context"] == "unknown"


class TestCreateSqsLambdaHandler:
    """Test create_sqs_lambda_handler function."""

    def test_handler_with_empty_event(self, mock_logger: MagicMock) -> None:
        """Test handler returns empty failures for empty event."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        result = handler(None, {})

        assert result["batchItemFailures"] == []

    def test_handler_with_no_records_key(self, mock_logger: MagicMock) -> None:
        """Test handler with event missing Records key."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        event = {}
        context = {}

        result = handler(event, context)

        assert result["batchItemFailures"] == []

    def test_handler_with_empty_records(self, mock_logger: MagicMock) -> None:
        """Test handler with empty records list."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        event = {"Records": []}
        context = {}

        result = handler(event, context)

        assert result["batchItemFailures"] == []

    def test_handler_creation_and_execution(
        self, mock_logger: MagicMock, sample_sqs_record: dict
    ) -> None:
        """Test handler creation and successful execution."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        event = {"Records": [sample_sqs_record]}
        context = {}

        result = handler(event, context)

        assert result["batchItemFailures"] == []

    def test_handler_with_context_setup(
        self, mock_logger: MagicMock, sample_sqs_record: dict, mocker: MockerFixture
    ) -> None:
        """Test handler with proper context setup."""
        mock_logger.reset_mock()
        mock_setup_context = mocker.patch("common.sqs_processor.setup_request_context")
        mock_extract_correlation = mocker.patch(
            "common.sqs_processor.extract_correlation_id_from_sqs_records",
            return_value="test-correlation-id",
        )

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        event = {"Records": [sample_sqs_record]}
        context = {"awsRequestId": "test-request-id"}

        handler(event, context)

        # Verify context setup was called
        mock_extract_correlation.assert_called_once_with([sample_sqs_record])
        mock_setup_context.assert_called_once_with(
            "test-correlation-id", context, mock_logger
        )

    def test_handler_logs_batch_processing_start(
        self, mock_logger: MagicMock, sample_sqs_record: dict
    ) -> None:
        """Test handler logs batch processing start."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        event = {"Records": [sample_sqs_record]}
        context = {}

        handler(event, context)

        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_005,
        )
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_006,
            total_records=1,
        )

    def test_handler_error_propagation(self, mock_logger: MagicMock) -> None:
        """Test that handler properly handles and returns batch failures."""
        mock_logger.reset_mock()

        def conditional_processor(record: dict) -> str:
            if record["messageId"] == "error-msg":
                raise ValueError("Error")
            return f"processed_{record['messageId']}"

        handler = create_sqs_lambda_handler(conditional_processor, mock_logger)

        event = {
            "Records": [
                {
                    "messageId": "success-msg",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data1"}),
                },
                {
                    "messageId": "error-msg",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data2"}),
                },
            ]
        }
        context = {}

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            result = handler(event, context)

        # Should return the failed message for retry
        assert len(result["batchItemFailures"]) == 1
        assert result["batchItemFailures"][0]["itemIdentifier"] == "error-msg"

    def test_handler_logs_retry_count_when_failures_exist(
        self, mock_logger: MagicMock
    ) -> None:
        """Test handler logs retry count when batch failures exist."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.failure_processor, mock_logger
        )

        event = {
            "Records": [
                {
                    "messageId": "error-msg-1",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data1"}),
                },
                {
                    "messageId": "error-msg-2",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data2"}),
                },
            ]
        }
        context = {}

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            result = handler(event, context)

        assert str(len(result["batchItemFailures"])) == "2"

        # Verify retry logging was called
        mock_logger.log.assert_any_call(
            OdsETLPipelineLogBase.ETL_COMMON_010,
            retry_count=2,
            total_records=2,
        )

    def test_handler_does_not_log_retry_count_when_no_failures(
        self, mock_logger: MagicMock, sample_sqs_record: dict
    ) -> None:
        """Test handler does not log retry count when all records succeed."""
        mock_logger.reset_mock()

        handler = create_sqs_lambda_handler(
            TestProcessSqsRecords.success_processor, mock_logger
        )

        event = {"Records": [sample_sqs_record]}
        context = {}

        handler(event, context)

        # Verify retry logging was not called
        log_calls = [call[0][0] for call in mock_logger.log.call_args_list]
        assert OdsETLPipelineLogBase.ETL_COMMON_010 not in log_calls

    def test_handler_with_multiple_record_types(
        self, mock_logger: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test handler with different error types in batch."""
        mock_logger.reset_mock()
        mocker.patch("common.sqs_processor.handle_permanent_error")

        call_count = {"value": 0}

        def mixed_processor(record: dict) -> str:
            call_count["value"] += 1
            msg_id = record["messageId"]

            if msg_id == "integrity-error":
                raise PermanentProcessingError(msg_id, 400, "Invalid data")
            elif msg_id == "permanent-error":
                raise PermanentProcessingError(msg_id, 404, "Not found")
            elif msg_id == "rate-limit":
                err_msg = "Rate limit exceeded"
                raise RetryableProcessingError(err_msg, status_code=429)
            elif msg_id == "general-error":
                err_msg = "General error occurred"
                raise ValueError(err_msg)
            return f"processed_{msg_id}"

        handler = create_sqs_lambda_handler(mixed_processor, mock_logger)

        event = {
            "Records": [
                {
                    "messageId": "success",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data"}),
                },
                {
                    "messageId": "integrity-error",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data"}),
                },
                {
                    "messageId": "permanent-error",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data"}),
                },
                {
                    "messageId": "rate-limit",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data"}),
                },
                {
                    "messageId": "general-error",
                    "attributes": {"ApproximateReceiveCount": "1"},
                    "body": json.dumps({"test": "data"}),
                },
            ]
        }
        context = {}

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            result = handler(event, context)

        # Only rate-limit and general-error should be in batch failures (retryable)
        # permanent-error and integrity-error are consumed, success is processed
        assert str(len(result["batchItemFailures"])) == "2"
        failure_ids = [f["itemIdentifier"] for f in result["batchItemFailures"]]
        assert "rate-limit" in failure_ids
        assert "general-error" in failure_ids
