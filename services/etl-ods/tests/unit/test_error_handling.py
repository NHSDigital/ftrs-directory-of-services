import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.error_handling import (
    _build_error_message,
    handle_general_error,
    handle_general_exception,
    handle_http_error,
    handle_permanent_error,
    handle_rate_limit_error,
    handle_retryable_error,
    handle_unrecoverable_error,
)
from common.exceptions import (
    PermanentProcessingError,
    RateLimitError,
    RetryableProcessingError,
    UnrecoverableError,
)


@pytest.fixture(scope="module")
def mock_logger() -> MagicMock:
    """File-scoped fixture for mock logger instance."""
    return MagicMock(spec=Logger)


class TestRateLimitError:
    """Test RateLimitError exception class."""

    def test_default_message(self) -> None:
        """Test exception with default message."""
        exception = RateLimitError()
        assert str(exception) == "Rate limit exceeded"
        assert exception.message == "Rate limit exceeded"

    def test_custom_message(self) -> None:
        """Test exception with custom message."""
        custom_message = "Custom rate limit message"
        exception = RateLimitError(custom_message)
        assert str(exception) == custom_message
        assert exception.message == custom_message

    def test_inheritance(self) -> None:
        """Test that RateLimitError inherits from Exception."""
        exception = RateLimitError()
        assert isinstance(exception, Exception)


class TestPermanentProcessingError:
    """Test PermanentProcessingError exception class."""

    def test_initialization(self) -> None:
        """Test PermanentProcessingError initialization with all attributes."""
        message_id = "test-message-123"
        status_code = 404
        response_text = "Not Found"

        error = PermanentProcessingError(message_id, status_code, response_text)

        assert error.message_id == message_id
        assert error.status_code == status_code
        assert error.response_text == response_text
        assert (
            str(error)
            == f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )

    def test_inheritance(self) -> None:
        """Test that PermanentProcessingError inherits from Exception."""
        error = PermanentProcessingError("test", 400, "test")
        assert isinstance(error, Exception)


class TestRetryableProcessingError:
    """Test RetryableProcessingError exception class."""

    def test_initialization(self) -> None:
        """Test RetryableProcessingError initialization with all attributes."""
        message_id = "test-retryable-123"
        status_code = 503
        response_text = "Service Unavailable"

        error = RetryableProcessingError(message_id, status_code, response_text)

        assert error.message_id == message_id
        assert error.status_code == status_code
        assert error.response_text == response_text
        assert (
            str(error)
            == f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )

    def test_inheritance(self) -> None:
        """Test that RetryableProcessingError inherits from Exception."""
        error = RetryableProcessingError("test", 503, "test")
        assert isinstance(error, Exception)


class TestUnrecoverableError:
    """Test UnrecoverableError exception class."""

    def test_initialization(self) -> None:
        """Test UnrecoverableError initialization with all attributes."""
        message_id = "poison-msg-123"
        error_type = "INVALID_JSON"
        details = "Unable to parse JSON body"

        error = UnrecoverableError(message_id, error_type, details)

        assert error.message_id == message_id
        assert error.error_type == error_type
        assert error.details == details
        assert (
            str(error)
            == f"Message id: {message_id}, Error Type: {error_type}, Details: {details}"
        )

    def test_inheritance(self) -> None:
        """Test that UnrecoverableError inherits from Exception."""
        error = UnrecoverableError("test", "TEST_TYPE", "test details")
        assert isinstance(error, Exception)


class TestHandleRateLimitError:
    """Test handle_rate_limit_error function."""

    def test_final_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for final attempt (DLQ)."""
        mock_logger.reset_mock()
        error = RateLimitError("Rate limit exceeded")
        message_id = "test-message-123"
        receive_count = 3

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_rate_limit_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_001,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Rate limit exceeded - final attempt, message will be sent to DLQ",
            exception=error,
        )

    def test_retry_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for retry attempt."""
        mock_logger.reset_mock()
        error = RateLimitError("Rate limit exceeded")
        message_id = "test-message-456"
        receive_count = 1

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_rate_limit_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_001,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Rate limit exceeded - message will be retried (attempt 1/3)",
        )

    def test_default_max_receive_count(self, mock_logger: MagicMock) -> None:
        """Test default MAX_RECEIVE_COUNT value when environment variable is not set."""
        mock_logger.reset_mock()
        error = RateLimitError("Rate limit exceeded")
        message_id = "test-message-789"
        receive_count = 3

        with patch.dict(os.environ, {}, clear=True):
            handle_rate_limit_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_001,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Rate limit exceeded - final attempt, message will be sent to DLQ",
            exception=error,
        )

    def test_custom_max_receive_count(self, mock_logger: MagicMock) -> None:
        """Test custom MAX_RECEIVE_COUNT value."""
        mock_logger.reset_mock()
        error = RateLimitError("Rate limit exceeded")
        message_id = "test-message-custom"
        receive_count = 5

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "5"}):
            handle_rate_limit_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_001,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=5,
            error_message="Rate limit exceeded - final attempt, message will be sent to DLQ",
            exception=error,
        )


class TestHandleRetryableError:
    """Test handle_retryable_error function."""

    def test_final_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for final attempt (DLQ)."""
        mock_logger.reset_mock()
        message_id = "test-retryable-final"
        error = RetryableProcessingError(message_id, 503, "Service Unavailable")
        receive_count = 3

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_retryable_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Retryable failure (status 503): Service Unavailable. Final attempt, message will be sent to DLQ",
        )

    def test_retry_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for retry attempt."""
        mock_logger.reset_mock()
        message_id = "test-retryable-retry"
        error = RetryableProcessingError(message_id, 500, "Internal Server Error")
        receive_count = 1

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_retryable_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Retryable failure (status 500): Internal Server Error. Message will be retried (attempt 1/3)",
        )

    def test_different_retryable_status_codes(self, mock_logger: MagicMock) -> None:
        """Test different retryable status codes."""
        test_cases = [
            (408, "Request Timeout"),
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
        ]

        for status_code, response_text in test_cases:
            mock_logger.reset_mock()
            message_id = f"test-{status_code}"
            error = RetryableProcessingError(message_id, status_code, response_text)

            with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
                handle_retryable_error(message_id, 1, error, mock_logger)

            mock_logger.log.assert_called_once()
            call_args = mock_logger.log.call_args[1]
            assert f"status {status_code}" in call_args["error_message"]
            assert response_text in call_args["error_message"]
            assert "will be retried" in call_args["error_message"]


class TestHandlePermanentError:
    """Test handle_permanent_error function."""

    def test_permanent_error_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for permanent processing errors."""
        mock_logger.reset_mock()
        message_id = "test-permanent-123"
        error = PermanentProcessingError(message_id, 404, "Resource not found")

        handle_permanent_error(message_id, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=1,
            max_receive_count=1,
            error_message="Permanent failure (status 404): Resource not found. Message will be consumed immediately.",
        )


class TestHandleUnrecoverableError:
    """Test handle_unrecoverable_error function."""

    def test_unrecoverable_error_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for unrecoverable errors."""
        mock_logger.reset_mock()
        message_id = "poison-msg-123"
        error = UnrecoverableError(
            message_id, "INVALID_JSON", "Unable to parse JSON body"
        )

        handle_unrecoverable_error(message_id, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=1,
            max_receive_count=1,
            error_message="Unrecoverable failure (INVALID_JSON): Unable to parse JSON body. Sending to DLQ immediately.",
        )

    def test_different_unrecoverable_error_types(self, mock_logger: MagicMock) -> None:
        """Test different types of unrecoverable errors."""
        test_cases = [
            ("MISSING_REQUIRED_FIELD", "ODS code is missing"),
            ("INVALID_FORMAT", "Date format is incorrect"),
            ("SCHEMA_VIOLATION", "Message does not match expected schema"),
        ]

        for error_type, details in test_cases:
            mock_logger.reset_mock()
            message_id = f"test-{error_type}"
            error = UnrecoverableError(message_id, error_type, details)

            handle_unrecoverable_error(message_id, error, mock_logger)

            mock_logger.log.assert_called_once_with(
                OdsETLPipelineLogBase.ETL_COMMON_002,
                message_id=message_id,
                receive_count=1,
                max_receive_count=1,
                error_message=f"Unrecoverable failure ({error_type}): {details}. Sending to DLQ immediately.",
            )


class TestHandleGeneralError:
    """Test handle_general_error function."""

    def test_final_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for final attempt (DLQ)."""
        mock_logger.reset_mock()
        message_id = "test-message-general"
        receive_count = 3
        error = ValueError("Test error message")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_general_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Processing failed - final attempt, message will be sent to DLQ. Error: ValueError: Test error message",
        )

    def test_retry_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for retry attempt."""
        mock_logger.reset_mock()
        message_id = "test-message-retry"
        receive_count = 2
        error = KeyError("missing_key")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "5"}):
            handle_general_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=5,
            error_message="Processing failed - message will be retried (attempt 2/5). Error: KeyError: 'missing_key'",
        )

    def test_default_max_receive_count(self, mock_logger: MagicMock) -> None:
        """Test default MAX_RECEIVE_COUNT when environment variable not set."""
        mock_logger.reset_mock()
        message_id = "test-message-default"
        receive_count = 3
        error = RuntimeError("Runtime issue")

        with patch.dict(os.environ, {}, clear=True):
            handle_general_error(message_id, receive_count, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=3,
            error_message="Processing failed - final attempt, message will be sent to DLQ. Error: RuntimeError: Runtime issue",
        )


class TestBuildErrorMessage:
    """Test _build_error_message helper function."""

    def test_error_message_without_context(self) -> None:
        """Test building error message without context."""
        error = ValueError("Invalid value")
        result = _build_error_message("Validation error", 400, error)

        assert result == "Validation error (status 400): Invalid value"

    def test_error_message_with_context(self) -> None:
        """Test building error message with context."""
        error = ValueError("Invalid ODS code")
        result = _build_error_message("Validation error", 400, error, "ODS123")

        assert result == "Validation error for ODS123 (status 400): Invalid ODS code"

    def test_error_message_with_empty_context(self) -> None:
        """Test building error message with empty context."""
        error = RuntimeError("Timeout")
        result = _build_error_message("Connection error", 504, error, "")

        assert result == "Connection error (status 504): Timeout"

    def test_error_message_formatting(self) -> None:
        """Test error message includes all components correctly."""
        error = Exception("Test exception message")
        result = _build_error_message("Test Type", 500, error, "Context Info")

        assert "Test Type" in result
        assert "Context Info" in result
        assert "500" in result
        assert "Test exception message" in result


class TestHandleHttpError:
    """Test handle_http_error function."""

    def test_bad_request_400_raises_unrecoverable_error(
        self, mock_logger: MagicMock
    ) -> None:
        """Test 400 Bad Request raises UnrecoverableError."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = 400

        http_error = requests.exceptions.HTTPError("Bad Request")
        http_error.response = mock_response

        message_id = "test-400"

        with pytest.raises(UnrecoverableError) as exc_info:
            handle_http_error(http_error, message_id, mock_logger)

        error = exc_info.value
        assert error.message_id == message_id
        assert error.error_type == "HTTP_400_BAD_REQUEST"
        assert error.details == str(http_error)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=400,
            error_message="Bad Request - invalid payload (status 400): Bad Request",
        )

    def test_rate_limit_error_429(self, mock_logger: MagicMock) -> None:
        """Test handling of 429 (Too Many Requests) status code raises RateLimitError."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.TOO_MANY_REQUESTS

        http_error = requests.exceptions.HTTPError("Too many requests")
        http_error.response = mock_response

        message_id = "test-429"

        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            handle_http_error(http_error, message_id, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            error_message=f"Rate limit exceeded (status 429): {str(http_error)}",
        )

    def test_rate_limit_error_429_with_context(self, mock_logger: MagicMock) -> None:
        """Test 429 error with context includes context in error message."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.TOO_MANY_REQUESTS

        http_error = requests.exceptions.HTTPError("Too many requests")
        http_error.response = mock_response

        message_id = "test-429-context"
        error_context = "ODS_CODE_XYZ"

        with pytest.raises(RateLimitError):
            handle_http_error(http_error, message_id, mock_logger, error_context)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args[1]
        assert "ODS_CODE_XYZ" in call_args["error_message"]
        assert "Rate limit exceeded" in call_args["error_message"]

    def test_retryable_status_codes(self, mock_logger: MagicMock) -> None:
        """Test retryable status codes raise RetryableProcessingError."""
        retryable_codes = [408, 409, 410, 412, 500, 502, 503, 504]

        for status_code in retryable_codes:
            mock_logger.reset_mock()
            mock_response = MagicMock()
            mock_response.status_code = status_code

            http_error = requests.exceptions.HTTPError(f"Error {status_code}")
            http_error.response = mock_response

            message_id = f"test-{status_code}"

            with pytest.raises(RetryableProcessingError) as exc_info:
                handle_http_error(http_error, message_id, mock_logger)

            error = exc_info.value
            assert error.message_id == message_id
            assert error.status_code == status_code
            assert error.response_text == str(http_error)

            mock_logger.log.assert_called_once_with(
                OdsETLPipelineLogBase.ETL_COMMON_009,
                message_id=message_id,
                status_code=status_code,
                error_message=f"Retryable HTTP error (status {status_code}): Error {status_code}",
            )

    def test_permanent_status_codes(self, mock_logger: MagicMock) -> None:
        """Test permanent status code (404 only) raises PermanentProcessingError."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = 404

        http_error = requests.exceptions.HTTPError("Not found")
        http_error.response = mock_response

        message_id = "test-404"

        with pytest.raises(PermanentProcessingError) as exc_info:
            handle_http_error(http_error, message_id, mock_logger)

        error = exc_info.value
        assert error.message_id == message_id
        assert str(error.status_code) == "404"
        assert error.response_text == str(http_error)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=404,
            error_message="Permanent HTTP error (status 404): Not found",
        )

    def test_unrecoverable_status_codes(self, mock_logger: MagicMock) -> None:
        """Test unrecoverable status codes raise UnrecoverableError."""
        unrecoverable_codes = [401, 403, 405, 406, 422]

        for status_code in unrecoverable_codes:
            mock_logger.reset_mock()
            mock_response = MagicMock()
            mock_response.status_code = status_code

            http_error = requests.exceptions.HTTPError(f"Error {status_code}")
            http_error.response = mock_response

            message_id = f"test-{status_code}"

            with pytest.raises(UnrecoverableError) as exc_info:
                handle_http_error(http_error, message_id, mock_logger)

            error = exc_info.value
            assert error.message_id == message_id
            assert error.error_type == f"HTTP_{status_code}"
            assert error.details == str(http_error)

            mock_logger.log.assert_called_once_with(
                OdsETLPipelineLogBase.ETL_COMMON_009,
                message_id=message_id,
                status_code=status_code,
                error_message=f"Unrecoverable HTTP error (status {status_code}): Error {status_code}",
            )

    def test_permanent_status_code_with_context(self, mock_logger: MagicMock) -> None:
        """Test permanent error with context includes context in error message."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = 404

        http_error = requests.exceptions.HTTPError("Not found")
        http_error.response = mock_response

        message_id = "test-404-context"
        error_context = "ODS_ABC123"

        with pytest.raises(PermanentProcessingError):
            handle_http_error(http_error, message_id, mock_logger, error_context)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args[1]
        assert "ODS_ABC123" in call_args["error_message"]
        assert "Permanent HTTP error" in call_args["error_message"]

    def test_unknown_status_code(self, mock_logger: MagicMock) -> None:
        """Test unknown/unmapped status codes raise UnrecoverableError."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = 418  # I'm a teapot - not in any category

        http_error = requests.exceptions.HTTPError("I'm a teapot")
        http_error.response = mock_response

        message_id = "test-418"

        with pytest.raises(UnrecoverableError) as exc_info:
            handle_http_error(http_error, message_id, mock_logger)

        error = exc_info.value
        assert error.message_id == message_id
        assert error.error_type == "HTTP_418_UNKNOWN"
        assert error.details == str(http_error)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=418,
            error_message="Unknown HTTP error (status 418): I'm a teapot",
        )

    def test_http_error_without_response(self, mock_logger: MagicMock) -> None:
        """Test handling HTTP error without response object defaults to UnrecoverableError."""
        mock_logger.reset_mock()

        http_error = requests.exceptions.HTTPError("Connection error")
        http_error.response = None

        message_id = "test-no-response"

        with pytest.raises(UnrecoverableError) as exc_info:
            handle_http_error(http_error, message_id, mock_logger)

        error = exc_info.value
        assert error.message_id == message_id
        assert error.error_type == "HTTP_0_UNKNOWN"
        assert error.details == str(http_error)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_014,
            method="HTTP",
            url="unknown",
            error_message="Unknown HTTP error: Connection error",
        )

    def test_retryable_error_with_context(self, mock_logger: MagicMock) -> None:
        """Test retryable error with context includes context in error message."""
        mock_logger.reset_mock()
        mock_response = MagicMock()
        mock_response.status_code = 503

        http_error = requests.exceptions.HTTPError("Service unavailable")
        http_error.response = mock_response

        message_id = "test-503-context"
        error_context = "SERVICE_XYZ"

        with pytest.raises(RetryableProcessingError) as exc_info:
            handle_http_error(http_error, message_id, mock_logger, error_context)

        error = exc_info.value
        assert error.message_id == message_id
        assert str(error.status_code) == "503"
        assert error.response_text == str(http_error)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args[1]
        assert "SERVICE_XYZ" in call_args["error_message"]
        assert "Retryable HTTP error" in call_args["error_message"]


class TestHandleGeneralException:
    """Test handle_general_exception function."""

    def test_basic_exception_handling(self, mock_logger: MagicMock) -> None:
        """Test basic exception handling with logging."""
        mock_logger.reset_mock()
        exception = ValueError("Test value error")
        message_id = "test-exception"
        error_context = "test_function"

        handle_general_exception(exception, message_id, mock_logger, error_context)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=0,
            error_message=f"Error in {error_context}: {str(exception)}",
        )

    def test_default_error_context(self, mock_logger: MagicMock) -> None:
        """Test handling with default error context."""
        mock_logger.reset_mock()
        exception = RuntimeError("Test runtime error")
        message_id = "test-default-context"

        handle_general_exception(exception, message_id, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=0,
            error_message=f"Error in unknown: {str(exception)}",
        )

    def test_exception_with_empty_message(self, mock_logger: MagicMock) -> None:
        """Test handling exception with empty message."""
        mock_logger.reset_mock()
        exception = ValueError("")  # Empty message
        message_id = "test-empty-message"
        error_context = "validation"

        handle_general_exception(exception, message_id, mock_logger, error_context)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=0,
            error_message="Error in validation: ",
        )

    def test_different_exception_types(self, mock_logger: MagicMock) -> None:
        """Test handling different exception types."""
        test_cases = [
            (ValueError("Invalid value"), "value_validation"),
            (TypeError("Wrong type"), "type_check"),
            (KeyError("Missing key"), "key_lookup"),
            (RuntimeError("Runtime issue"), "runtime_operation"),
        ]

        for exception, context in test_cases:
            mock_logger.reset_mock()
            message_id = f"test-{context}"

            handle_general_exception(exception, message_id, mock_logger, context)

            mock_logger.log.assert_called_once_with(
                OdsETLPipelineLogBase.ETL_COMMON_009,
                message_id=message_id,
                status_code=0,
                error_message=f"Error in {context}: {str(exception)}",
            )


class TestErrorHandlingEdgeCases:
    """Test edge cases and error combinations."""

    def test_rate_limit_with_zero_receive_count(self, mock_logger: MagicMock) -> None:
        """Test rate limit handling with zero receive count."""
        mock_logger.reset_mock()
        error = RateLimitError("Rate limit exceeded")
        message_id = "test-zero-count"

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_rate_limit_error(message_id, 0, error, mock_logger)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args[1]
        assert "will be retried" in call_args["error_message"]
        assert "(attempt 0/3)" in call_args["error_message"]

    def test_general_error_with_zero_receive_count(
        self, mock_logger: MagicMock
    ) -> None:
        """Test general error handling with zero receive count."""
        mock_logger.reset_mock()
        message_id = "test-general-zero"
        error = Exception("Zero count error")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "5"}):
            handle_general_error(message_id, 0, error, mock_logger)

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args[1]
        assert "will be retried" in call_args["error_message"]
        assert "(attempt 0/5)" in call_args["error_message"]
        assert "Exception: Zero count error" in call_args["error_message"]

    def test_environment_variable_edge_cases(self, mock_logger: MagicMock) -> None:
        """Test handling of invalid or edge case environment variables."""
        mock_logger.reset_mock()
        error = RateLimitError("Rate limit")
        message_id = "test-env-edge"

        # Test with non-numeric MAX_RECEIVE_COUNT (should raise ValueError)
        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "invalid"}):
            with pytest.raises(ValueError):
                handle_rate_limit_error(message_id, 3, error, mock_logger)

        # Test with zero MAX_RECEIVE_COUNT
        mock_logger.reset_mock()
        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "0"}):
            handle_rate_limit_error(message_id, 1, error, mock_logger)
            call_args = mock_logger.log.call_args[1]
            assert call_args["receive_count"] == 1
            assert call_args["max_receive_count"] == 0

    def test_receive_count_exceeds_max(self, mock_logger: MagicMock) -> None:
        """Test behavior when receive count exceeds max receive count."""
        mock_logger.reset_mock()
        message_id = "test-exceed-max"
        error = Exception("Exceed max error")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            # Receive count 5 > max 3
            handle_general_error(message_id, 5, error, mock_logger)

        call_args = mock_logger.log.call_args[1]
        assert "final attempt" in call_args["error_message"]
        assert "Exception: Exceed max error" in call_args["error_message"]
        assert str(call_args["receive_count"]) == "5"
        assert str(call_args["max_receive_count"]) == "3"
