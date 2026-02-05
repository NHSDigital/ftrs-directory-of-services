import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.error_handling import (
    _build_troubleshooting_info,
    extract_operation_outcome,
    handle_general_error,
    handle_http_error,
    handle_permanent_error,
    handle_retryable_error,
)
from common.exceptions import (
    PermanentProcessingError,
    RetryableProcessingError,
)


@pytest.fixture(scope="module")
def mock_logger() -> MagicMock:
    """File-scoped fixture for mock logger instance."""
    return MagicMock(spec=Logger)


class TestPermanentProcessingError:
    """Test PermanentProcessingError exception class."""

    def test_initialization(self) -> None:
        """Test PermanentProcessingError initialization with all attributes."""
        message_id = "poison-msg-123"
        status_code = 400
        response_text = "Unable to parse JSON body"

        error = PermanentProcessingError(message_id, status_code, response_text)

        assert error.message_id == message_id
        assert error.status_code == status_code
        assert error.response_text == response_text
        assert "poison-msg-123" in str(error)
        assert "400" in str(error)
        assert "Unable to parse JSON body" in str(error)

    def test_inheritance(self) -> None:
        """Test that PermanentProcessingError inherits from Exception."""
        error = PermanentProcessingError("test", 400, "test details")
        assert isinstance(error, Exception)


class TestRetryableProcessingError:
    """Test RetryableProcessingError exception class."""

    def test_initialization(self) -> None:
        """Test RetryableProcessingError initialization with all attributes."""
        message = "Rate limit exceeded"
        status_code = 429

        error = RetryableProcessingError(message, status_code, "Response text")

        assert error.status_code == status_code
        assert message in str(error)
        assert "429" in str(error)

    def test_inheritance(self) -> None:
        """Test that RetryableProcessingError inherits from Exception."""
        error = RetryableProcessingError("Test error", 500, "Server error")
        assert isinstance(error, Exception)


class TestExtractOperationOutcome:
    """Test extract_operation_outcome function."""

    def test_valid_operation_outcome(self) -> None:
        """Test extraction of valid FHIR OperationOutcome."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/fhir+json"}
        mock_response.json.return_value = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "details": {"text": "Organization code ABC123 not found"},
                }
            ],
        }

        result = extract_operation_outcome(mock_response)

        assert result["resource_type"] == "OperationOutcome"
        assert result["issues_count"] == 1
        assert "error" in result["severity_levels"]
        assert "invalid" in result["issue_codes"]
        assert "Organization code ABC123 not found" in result["issue_details"]

    def test_empty_response(self) -> None:
        """Test extraction with response that causes exception."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.side_effect = json.JSONDecodeError("Not JSON", "", 0)

        result = extract_operation_outcome(mock_response)

        assert result["resource_type"] == "Invalid JSON or Non-JSON response"
        assert result["issues_count"] == 0

    def test_non_json_response(self) -> None:
        """Test extraction with non-JSON response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "text/html"}
        mock_response.json.side_effect = json.JSONDecodeError("Not JSON", "", 0)

        result = extract_operation_outcome(mock_response)

        assert result["resource_type"] == "Unknown"
        assert result["issues_count"] == 0

    def test_non_fhir_response(self) -> None:
        """Test extraction with non-FHIR application response."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {
            "resourceType": "Bundle",
            "type": "searchset",
        }

        result = extract_operation_outcome(mock_response)

        assert result["resource_type"] == "Bundle"
        assert result["issues_count"] == 0

    def test_missing_resource_type(self) -> None:
        """Test extraction with missing resourceType."""
        mock_response = MagicMock()
        mock_response.headers = {"content-type": "application/json"}
        mock_response.json.return_value = {"status": "error"}

        result = extract_operation_outcome(mock_response)

        assert result["resource_type"] == "Non-FHIR"
        assert result["issues_count"] == 0


class TestHandleHttpError:
    def test_permanent_status_codes(self) -> None:
        """Test permanent status codes raise PermanentProcessingError."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.json.side_effect = Exception("Not JSON")

        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = mock_response

        with pytest.raises(PermanentProcessingError) as exc_info:
            handle_http_error(mock_http_error, "test-msg-123")

        assert str(exc_info.value.status_code) == "404"
        assert "HTTP 404 in unknown" in exc_info.value.response_text

    def test_retryable_status_codes(self) -> None:
        """Test retryable status codes raise RetryableProcessingError."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.json.side_effect = Exception("Not JSON")

        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = mock_response

        with pytest.raises(RetryableProcessingError) as exc_info:
            handle_http_error(mock_http_error, "test-msg-123")

        assert str(exc_info.value.status_code) == "500"
        assert "HTTP 500 in unknown" in exc_info.value.response_text

    def test_unknown_status_codes(self) -> None:
        """Test unknown status codes raise PermanentProcessingError."""
        mock_response = MagicMock()
        mock_response.status_code = 418  # I'm a teapot - unknown status
        mock_response.text = "I'm a teapot"
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.json.side_effect = Exception("Not JSON")

        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = mock_response

        with pytest.raises(PermanentProcessingError) as exc_info:
            handle_http_error(mock_http_error, "test-msg-123")

        assert str(exc_info.value.status_code) == "418"
        assert "Unknown HTTP 418 in unknown" in exc_info.value.response_text

    def test_operation_outcome_summary_fhir(self) -> None:
        """Test operation outcome summary for FHIR response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.headers = {"content-type": "application/fhir+json"}
        mock_response.json.return_value = {
            "resourceType": "OperationOutcome",
            "issue": [
                {"severity": "error", "code": "invalid"},
                {"severity": "warning", "code": "business-rule"},
            ],
        }

        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = mock_response

        with pytest.raises(PermanentProcessingError) as exc_info:
            handle_http_error(mock_http_error, "test-msg-123")

        assert "OperationOutcome: 2 issues" in exc_info.value.response_text

    def test_custom_error_context(self) -> None:
        """Test handle_http_error with custom error context."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.json.side_effect = Exception("Not JSON")

        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = mock_response

        with pytest.raises(PermanentProcessingError) as exc_info:
            handle_http_error(mock_http_error, "test-msg-123", "organization lookup")

        assert "HTTP 404 in organization lookup" in exc_info.value.response_text

    def test_http_error_without_response(self) -> None:
        """Test handle_http_error when HTTPError has no response."""
        mock_http_error = MagicMock(spec=requests.exceptions.HTTPError)
        mock_http_error.response = None

        with pytest.raises(RetryableProcessingError) as exc_info:
            handle_http_error(mock_http_error, "test-msg-123")

        # Should default to 500 when no response available
        assert str(exc_info.value.status_code) == "500"
        assert "HTTP 500 in unknown" in exc_info.value.response_text


class TestHandlePermanentError:
    """Test handle_permanent_error function."""

    def test_permanent_error_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for permanent errors."""
        mock_logger.reset_mock()
        error = PermanentProcessingError("test-msg-123", 404, "Organization not found")

        handle_permanent_error("test-msg-123", error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id="test-msg-123",
            receive_count=1,
            max_receive_count=1,
            error_message="Permanent failure (status 404) - consumed immediately",
            error_category="UNKNOWN",
            troubleshooting_info="Status: 404",
        )

    def test_permanent_error_with_category(self, mock_logger: MagicMock) -> None:
        """Test permanent error with error category."""
        mock_logger.reset_mock()
        error = PermanentProcessingError("test-msg-123", 400, "Invalid data")
        error.error_category = "VALIDATION"

        handle_permanent_error("test-msg-123", error, mock_logger)

        # Check that Category: VALIDATION is in troubleshooting_info
        call_args = mock_logger.log.call_args[1]
        assert "Category: VALIDATION" in call_args["troubleshooting_info"]

    def test_permanent_error_with_operation_outcome(
        self, mock_logger: MagicMock
    ) -> None:
        """Test permanent error with OperationOutcome in response."""
        mock_logger.reset_mock()
        error = PermanentProcessingError(
            "test-msg-123", 422, "OperationOutcome: validation failed"
        )

        handle_permanent_error("test-msg-123", error, mock_logger)

        # Check that FHIR info is in troubleshooting_info
        call_args = mock_logger.log.call_args[1]
        assert (
            "FHIR: OperationOutcome: validation failed"
            in call_args["troubleshooting_info"]
        )

    def test_permanent_error_with_custom_info_dict(
        self, mock_logger: MagicMock
    ) -> None:
        """Test permanent error with custom troubleshooting info as dict."""
        mock_logger.reset_mock()
        error = PermanentProcessingError("test-msg-123", 400, "Invalid data")
        error.troubleshooting_info = {"field": "organization_code", "value": "ABC123"}

        handle_permanent_error("test-msg-123", error, mock_logger)

        # Check that custom info is formatted properly
        call_args = mock_logger.log.call_args[1]
        troubleshooting_info = call_args["troubleshooting_info"]
        assert "field: organization_code" in troubleshooting_info
        assert "value: ABC123" in troubleshooting_info

    def test_permanent_error_with_custom_info_string(
        self, mock_logger: MagicMock
    ) -> None:
        """Test permanent error with custom troubleshooting info as string."""
        mock_logger.reset_mock()
        error = PermanentProcessingError("test-msg-123", 400, "Invalid data")
        error.troubleshooting_info = "Custom troubleshooting details"

        handle_permanent_error("test-msg-123", error, mock_logger)

        # Check that custom info is included
        call_args = mock_logger.log.call_args[1]
        assert "Custom troubleshooting details" in call_args["troubleshooting_info"]

    def test_permanent_error_with_no_additional_info(
        self, mock_logger: MagicMock
    ) -> None:
        """Test permanent error with 'No additional troubleshooting info'."""
        mock_logger.reset_mock()
        error = PermanentProcessingError("test-msg-123", 400, "Invalid data")
        error.troubleshooting_info = "No additional troubleshooting info"

        handle_permanent_error("test-msg-123", error, mock_logger)

        # Should only contain status info, not the 'No additional' message
        call_args = mock_logger.log.call_args[1]
        troubleshooting_info = call_args["troubleshooting_info"]
        assert "Status: 400" in troubleshooting_info
        assert "No additional troubleshooting info" not in troubleshooting_info


class TestHandleRetryableError:
    """Test handle_retryable_error function."""

    def test_final_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for final attempt (DLQ)."""
        mock_logger.reset_mock()
        error = RetryableProcessingError("test-msg-123", 429, "Too many requests")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_retryable_error("test-msg-123", 3, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id="test-msg-123",
            receive_count=3,
            max_receive_count=3,
            error_message="Retryable failure (status 429) - final attempt, sending to DLQ",
        )

    def test_retry_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for retry attempt."""
        mock_logger.reset_mock()
        error = RetryableProcessingError("test-msg-123", 500, "Server error")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_retryable_error("test-msg-123", 1, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id="test-msg-123",
            receive_count=1,
            max_receive_count=3,
            error_message="Retryable failure (status 500) - retry 1/3",
        )


class TestHandleGeneralError:
    """Test handle_general_error function."""

    def test_final_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for final attempt (DLQ)."""
        mock_logger.reset_mock()
        error = ValueError("Test error")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "3"}):
            handle_general_error("test-msg-123", 3, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id="test-msg-123",
            receive_count=3,
            max_receive_count=3,
            error_message="General failure (ValueError) - final attempt, sending to DLQ",
            troubleshooting_info="Exception: ValueError | Details: Test error | Attempt: 3/3",
        )

    def test_retry_attempt_logging(self, mock_logger: MagicMock) -> None:
        """Test logging for retry attempt."""
        mock_logger.reset_mock()
        error = Exception("General error")

        with patch.dict(os.environ, {"MAX_RECEIVE_COUNT": "5"}):
            handle_general_error("test-msg-123", 2, error, mock_logger)

        mock_logger.log.assert_called_once_with(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id="test-msg-123",
            receive_count=2,
            max_receive_count=5,
            error_message="General failure (Exception) - retry 2/5",
            troubleshooting_info="Exception: Exception | Details: General error | Attempt: 2/5",
        )


class TestBuildTroubleshootingInfo:
    """Test _build_troubleshooting_info function."""

    def test_permanent_error_info(self) -> None:
        """Test troubleshooting info for permanent errors."""
        error = PermanentProcessingError("test-msg", 404, "Not found")

        result = _build_troubleshooting_info(error)

        assert "Status: 404" in result

    def test_general_error_info(self) -> None:
        """Test troubleshooting info for general errors."""
        error = ValueError("Test error message")

        result = _build_troubleshooting_info(error, 2, 3)

        assert "Exception: ValueError" in result
        assert "Details: Test error message" in result
        assert "Attempt: 2/3" in result

    def test_general_error_info_without_counts(self) -> None:
        """Test troubleshooting info for general errors without retry counts."""
        error = ValueError("Test error message")

        result = _build_troubleshooting_info(error, None, None)

        assert "Exception: ValueError" in result
        assert "Details: Test error message" in result
        assert "Attempt:" not in result
        assert "Attempt:" not in result
