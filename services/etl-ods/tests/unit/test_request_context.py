from unittest.mock import MagicMock, patch

from ftrs_common.logger import Logger

from consumer.request_context import (
    extract_correlation_id_from_sqs_records,
    setup_request_context,
)


class TestExtractCorrelationIdFromSqsRecords:
    @patch("consumer.request_context._parse_message_body")
    def test_extract_correlation_id_with_valid_record(
        self, mock_parse: MagicMock
    ) -> None:
        test_correlation_id = "test-correlation-123"
        mock_parse.return_value = {
            "path": "org-uuid",
            "body": {"name": "Test Org"},
            "correlation_id": test_correlation_id,
            "request_id": "test-request-123",
        }

        records = [{"messageId": "msg-1", "body": "some-body"}]

        result = extract_correlation_id_from_sqs_records(records)

        assert result == test_correlation_id
        mock_parse.assert_called_once_with(records[0])

    def test_extract_correlation_id_with_empty_records(self) -> None:
        result = extract_correlation_id_from_sqs_records([])
        assert result is None

    def test_extract_correlation_id_with_invalid_message_body(self) -> None:
        records = [{"messageId": "msg-1", "body": "invalid-json"}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result is None

    @patch("consumer.request_context._parse_message_body")
    def test_extract_correlation_id_with_missing_correlation_id(
        self, mock_parse: MagicMock
    ) -> None:
        """Test extracting correlation ID from record missing correlation_id field."""
        mock_parse.return_value = {
            "path": "org-uuid",
            "body": {"name": "Test Org"},
            "request_id": "test-request-123",
            # No correlation_id field
        }

        records = [{"messageId": "msg-1", "body": "some-body"}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result is None

    @patch("consumer.request_context._parse_message_body")
    def test_extract_correlation_id_handles_parse_exception(
        self, mock_parse: MagicMock
    ) -> None:
        """Test extracting correlation ID when _parse_message_body raises exception."""
        mock_parse.side_effect = Exception("Parsing error")

        records = [{"messageId": "msg-1", "body": "some-body"}]

        result = extract_correlation_id_from_sqs_records(records)
        assert result is None


class TestSetupRequestContext:
    @patch("consumer.request_context.fetch_or_set_correlation_id")
    @patch("consumer.request_context.fetch_or_set_request_id")
    def test_setup_request_context_with_correlation_id(
        self, mock_fetch_request_id: MagicMock, mock_fetch_correlation_id: MagicMock
    ) -> None:
        test_correlation_id = "test-correlation-123"
        test_request_id = "test-request-456"
        mock_fetch_correlation_id.return_value = test_correlation_id
        mock_fetch_request_id.return_value = test_request_id

        mock_context = MagicMock()
        mock_context.aws_request_id = "aws-request-123"
        mock_logger = MagicMock(spec=Logger)

        setup_request_context(test_correlation_id, mock_context, mock_logger)

        mock_fetch_correlation_id.assert_called_once_with(test_correlation_id)
        mock_fetch_request_id.assert_called_once_with(
            context_id="aws-request-123", header_id=None
        )
        mock_logger.append_keys.assert_called_once_with(
            correlation_id=test_correlation_id, request_id=test_request_id
        )

    @patch("consumer.request_context.fetch_or_set_correlation_id")
    @patch("consumer.request_context.fetch_or_set_request_id")
    def test_setup_request_context_with_none_correlation_id(
        self, mock_fetch_request_id: MagicMock, mock_fetch_correlation_id: MagicMock
    ) -> None:
        test_request_id = "test-request-456"
        generated_correlation_id = "generated-correlation-789"
        mock_fetch_correlation_id.return_value = generated_correlation_id
        mock_fetch_request_id.return_value = test_request_id

        mock_context = MagicMock()
        mock_context.aws_request_id = "aws-request-123"
        mock_logger = MagicMock(spec=Logger)

        setup_request_context(None, mock_context, mock_logger)

        mock_fetch_correlation_id.assert_called_once_with(None)
        mock_fetch_request_id.assert_called_once_with(
            context_id="aws-request-123", header_id=None
        )
        mock_logger.append_keys.assert_called_once_with(
            correlation_id=generated_correlation_id, request_id=test_request_id
        )

    @patch("consumer.request_context.fetch_or_set_correlation_id")
    @patch("consumer.request_context.fetch_or_set_request_id")
    def test_setup_request_context_with_none_context(
        self, mock_fetch_request_id: MagicMock, mock_fetch_correlation_id: MagicMock
    ) -> None:
        test_correlation_id = "test-correlation-123"
        test_request_id = "test-request-456"
        mock_fetch_correlation_id.return_value = test_correlation_id
        mock_fetch_request_id.return_value = test_request_id

        mock_logger = MagicMock(spec=Logger)

        setup_request_context(test_correlation_id, None, mock_logger)

        mock_fetch_correlation_id.assert_called_once_with(test_correlation_id)
        mock_fetch_request_id.assert_called_once_with(context_id=None, header_id=None)
        mock_logger.append_keys.assert_called_once_with(
            correlation_id=test_correlation_id, request_id=test_request_id
        )
