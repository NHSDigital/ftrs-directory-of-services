import json

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from pytest_mock import MockerFixture

from common.sqs_request_context import (
    extract_correlation_id_from_sqs_records,
    setup_request_context,
)


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> MockLogger:
    """Mock logger for testing request context setup."""
    return mocker.MagicMock()


class TestExtractCorrelationIdFromSqsRecords:
    def test_extract_correlation_id_with_valid_record(self) -> None:
        """Test extracting correlation ID from valid SQS record with JSON string body."""
        test_correlation_id = "test-correlation-123"
        message_body = {
            "path": "org-uuid",
            "body": {"name": "Test Org"},
            "correlation_id": test_correlation_id,
            "request_id": "test-request-123",
        }

        records = [{"messageId": "msg-1", "body": json.dumps(message_body)}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result == test_correlation_id

    def test_extract_correlation_id_with_empty_records(self) -> None:
        """Test that function returns None when given empty records list."""
        result = extract_correlation_id_from_sqs_records([])
        assert result is None

    def test_extract_correlation_id_with_invalid_message_body(self) -> None:
        """Test that function returns None when body contains invalid JSON."""
        records = [{"messageId": "msg-1", "body": "invalid-json"}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result is None

    def test_extract_correlation_id_with_missing_correlation_id(self) -> None:
        """Test extracting correlation ID from record missing correlation_id field."""
        message_body = {
            "path": "org-uuid",
            "body": {"name": "Test Org"},
            "request_id": "test-request-123",
        }

        records = [{"messageId": "msg-1", "body": json.dumps(message_body)}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result is None

    def test_extract_correlation_id_handles_parse_exception(self) -> None:
        """Test extracting correlation ID when JSON parsing fails."""
        records = [{"messageId": "msg-1", "body": "invalid-json-string"}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result is None

    def test_extract_correlation_id_with_dict_body(self) -> None:
        """Test extracting correlation ID from record with direct dict body."""
        test_correlation_id = "test-correlation-456"
        message_body = {
            "path": "org-uuid",
            "body": {"name": "Test Org"},
            "correlation_id": test_correlation_id,
            "request_id": "test-request-456",
        }

        records = [{"messageId": "msg-1", "body": message_body}]

        result = extract_correlation_id_from_sqs_records(records)

        assert result == test_correlation_id


class TestSetupRequestContext:
    def test_setup_request_context_with_correlation_id(
        self, mocker: MockerFixture, mock_logger: MockLogger
    ) -> None:
        """Test setup_request_context with provided correlation ID."""
        test_correlation_id = "test-correlation-123"

        mock_fetch_correlation_id = mocker.patch(
            "common.sqs_request_context.fetch_or_set_correlation_id"
        )
        mock_fetch_request_id = mocker.patch(
            "common.sqs_request_context.fetch_or_set_request_id"
        )
        mock_fetch_correlation_id.return_value = test_correlation_id
        mock_fetch_request_id.return_value = "test-request-456"

        setup_request_context(test_correlation_id, None, mock_logger)

        mock_fetch_correlation_id.assert_called_once_with(test_correlation_id)
        mock_fetch_request_id.assert_called_once_with(context_id=None, header_id=None)
        mock_logger.append_keys.assert_called_once_with(
            correlation_id=test_correlation_id, request_id="test-request-456"
        )

    def test_setup_request_context_with_none_correlation_id(
        self, mocker: MockerFixture, mock_logger: MockLogger
    ) -> None:
        """Test setup_request_context generates IDs when correlation_id is None."""
        mock_fetch_correlation_id = mocker.patch(
            "common.sqs_request_context.fetch_or_set_correlation_id"
        )
        mock_fetch_request_id = mocker.patch(
            "common.sqs_request_context.fetch_or_set_request_id"
        )
        mock_fetch_correlation_id.return_value = "generated-correlation"
        mock_fetch_request_id.return_value = "generated-request"

        setup_request_context(None, None, mock_logger)

        mock_fetch_correlation_id.assert_called_once_with(None)
        mock_fetch_request_id.assert_called_once_with(context_id=None, header_id=None)
        mock_logger.append_keys.assert_called_once_with(
            correlation_id="generated-correlation", request_id="generated-request"
        )

    def test_setup_request_context_with_aws_context(
        self, mocker: MockerFixture, mock_logger: MockLogger
    ) -> None:
        """Test setup_request_context extracts aws_request_id from context object."""
        mock_fetch_correlation_id = mocker.patch(
            "common.sqs_request_context.fetch_or_set_correlation_id"
        )
        mock_fetch_request_id = mocker.patch(
            "common.sqs_request_context.fetch_or_set_request_id"
        )
        mock_fetch_correlation_id.return_value = "test-correlation"
        mock_fetch_request_id.return_value = "test-request"

        mock_context = mocker.MagicMock()
        mock_context.aws_request_id = "aws-req-789"

        setup_request_context("test-correlation", mock_context, mock_logger)

        mock_fetch_correlation_id.assert_called_once_with("test-correlation")
        mock_fetch_request_id.assert_called_once_with(
            context_id="aws-req-789", header_id=None
        )
        mock_logger.append_keys.assert_called_once_with(
            correlation_id="test-correlation", request_id="test-request"
        )
