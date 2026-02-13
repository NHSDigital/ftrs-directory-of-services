"""Unit tests for stream processor."""

from unittest.mock import MagicMock, patch

import pytest
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from version_history.stream_processor import (
    _deserialize_document,
    _deserialize_value,
    _extract_table_name,
    process_stream_records,
)


class TestExtractTableName:
    """Test suite for _extract_table_name function."""

    def test_valid_arn(self) -> None:
        """Test extraction from valid ARN."""
        arn = "arn:aws:dynamodb:eu-west-2:123456789012:table/organisation/stream/2024-01-01T00:00:00.000"
        table_name = _extract_table_name(arn)
        assert table_name == "organisation"

    def test_different_table_names(self) -> None:
        """Test extraction with different table names."""
        arns = [
            "arn:aws:dynamodb:eu-west-2:123456789012:table/location/stream/2024-01-01T00:00:00.000",
            "arn:aws:dynamodb:eu-west-2:123456789012:table/healthcare-service/stream/2024-01-01T00:00:00.000",
            "arn:aws:dynamodb:eu-west-2:123456789012:table/ftrs-dos-dev-database-organisation/stream/2024-01-01T00:00:00.000",
        ]
        expected = [
            "location",
            "healthcare-service",
            "ftrs-dos-dev-database-organisation",
        ]

        for arn, expected_name in zip(arns, expected):
            assert _extract_table_name(arn) == expected_name

    def test_invalid_arn(self) -> None:
        """Test with invalid ARN format."""
        arn = "invalid-arn-format"
        table_name = _extract_table_name(arn)
        assert table_name is None

    def test_empty_arn(self) -> None:
        """Test with empty ARN."""
        table_name = _extract_table_name("")
        assert table_name is None


class TestDeserializeDocument:
    """Test suite for _deserialize_document function."""

    def test_simple_document(self) -> None:
        """Test deserialization of simple document."""

        deserializer = TypeDeserializer()

        raw_doc = {
            "id": {"S": "test-123"},
            "name": {"S": "Test Name"},
            "age": {"N": "30"},
            "active": {"BOOL": True},
        }

        result = _deserialize_document(raw_doc, deserializer)

        assert result["id"] == "test-123"
        assert result["name"] == "Test Name"
        assert result["age"] == 30
        assert result["active"] is True

    def test_nested_document(self) -> None:
        """Test deserialization of nested document."""

        deserializer = TypeDeserializer()

        raw_doc = {
            "id": {"S": "test-123"},
            "contact": {
                "M": {
                    "email": {"S": "test@example.com"},
                    "phone": {"S": "123-456-7890"},
                }
            },
        }

        result = _deserialize_document(raw_doc, deserializer)

        assert result["id"] == "test-123"
        assert result["contact"]["email"] == "test@example.com"
        assert result["contact"]["phone"] == "123-456-7890"

    def test_empty_document(self) -> None:
        """Test deserialization of empty document."""

        deserializer = TypeDeserializer()
        result = _deserialize_document({}, deserializer)
        assert result == {}


class TestDeserializeValue:
    """Test suite for _deserialize_value function."""

    def test_string_value(self) -> None:
        """Test deserialization of string value."""

        deserializer = TypeDeserializer()
        raw_value = {"S": "test-value"}
        result = _deserialize_value(raw_value, deserializer)
        assert result == "test-value"

    def test_number_value(self) -> None:
        """Test deserialization of number value."""

        deserializer = TypeDeserializer()
        raw_value = {"N": "42"}
        result = _deserialize_value(raw_value, deserializer)
        assert result == 42

    def test_empty_value(self) -> None:
        """Test deserialization of empty value."""

        deserializer = TypeDeserializer()
        result = _deserialize_value({}, deserializer)
        assert result is None


class TestProcessStreamRecords:
    """Test suite for process_stream_records function."""

    @pytest.fixture
    def mock_repository(self) -> MagicMock:
        """Mock VersionHistoryRepository."""
        with patch("version_history.stream_processor.VersionHistoryRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def sample_stream_event(self) -> dict:
        """Create a sample stream event."""
        serializer = TypeSerializer()

        old_doc = {
            "id": "test-123",
            "field": "document",
            "email": "old@example.com",
            "status": "pending",
            "lastUpdatedBy": {
                "display": "Test User",
                "type": "user",
                "value": "user-123",
            },
        }

        new_doc = {
            "id": "test-123",
            "field": "document",
            "email": "new@example.com",
            "status": "active",
            "lastUpdatedBy": {
                "display": "Test User Updated",
                "type": "user",
                "value": "user-456",
            },
        }

        old_image = {key: serializer.serialize(value) for key, value in old_doc.items()}
        new_image = {key: serializer.serialize(value) for key, value in new_doc.items()}

        return {
            "eventID": "1",
            "eventName": "MODIFY",
            "eventSource": "aws:dynamodb",
            "awsRegion": "eu-west-2",
            "dynamodb": {
                "SequenceNumber": "123456789",
                "Keys": {"id": {"S": "test-123"}, "field": {"S": "document"}},
                "OldImage": old_image,
                "NewImage": new_image,
            },
            "eventSourceARN": "arn:aws:dynamodb:eu-west-2:123456789012:table/organisation/stream/2024-01-01T00:00:00.000",
        }

    def test_successful_processing(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test successful processing of stream records."""
        records = [sample_stream_event]

        failed = process_stream_records(records)

        assert len(failed) == 0
        assert mock_repository.write_change_record.called
        call_args = mock_repository.write_change_record.call_args[0][0]
        assert call_args.entity_id == "organisation|test-123|document"
        assert call_args.change_type == "UPDATE"
        assert "email" in call_args.changed_fields
        assert "status" in call_args.changed_fields

    def test_multiple_records(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test processing multiple records."""
        # Create a second event with different ID
        event2 = sample_stream_event.copy()
        event2["dynamodb"] = sample_stream_event["dynamodb"].copy()
        event2["dynamodb"]["Keys"] = {
            "id": {"S": "test-456"},
            "field": {"S": "document"},
        }
        event2["dynamodb"]["SequenceNumber"] = "987654321"

        records = [sample_stream_event, event2]

        failed = process_stream_records(records)

        assert len(failed) == 0
        assert mock_repository.write_change_record.call_count == 2

    def test_missing_old_image(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test handling when OldImage is missing (INSERT event)."""
        event = sample_stream_event.copy()
        event["dynamodb"] = sample_stream_event["dynamodb"].copy()
        del event["dynamodb"]["OldImage"]

        records = [event]

        failed = process_stream_records(records)

        # Should skip the record, not fail
        assert len(failed) == 0
        assert not mock_repository.write_change_record.called

    def test_missing_new_image(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test handling when NewImage is missing (DELETE event)."""
        event = sample_stream_event.copy()
        event["dynamodb"] = sample_stream_event["dynamodb"].copy()
        del event["dynamodb"]["NewImage"]

        records = [event]

        failed = process_stream_records(records)

        # Should skip the record, not fail
        assert len(failed) == 0
        assert not mock_repository.write_change_record.called

    def test_no_changes_detected(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test when no business-relevant changes are detected."""
        # Make OldImage and NewImage identical
        event = sample_stream_event.copy()
        event["dynamodb"] = sample_stream_event["dynamodb"].copy()
        event["dynamodb"]["NewImage"] = sample_stream_event["dynamodb"]["OldImage"]

        records = [event]

        failed = process_stream_records(records)

        assert len(failed) == 0
        # Should not write to version history if no changes
        assert not mock_repository.write_change_record.called

    def test_invalid_table_arn(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test handling of invalid table ARN."""
        event = sample_stream_event.copy()
        event["eventSourceARN"] = "invalid-arn"

        records = [event]

        failed = process_stream_records(records)

        # Should fail the record
        assert len(failed) == 1
        assert failed[0] == "123456789"

    def test_missing_record_id(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test handling when record ID cannot be extracted."""
        event = sample_stream_event.copy()
        event["dynamodb"] = sample_stream_event["dynamodb"].copy()
        event["dynamodb"]["Keys"] = {}

        records = [event]

        failed = process_stream_records(records)

        # Should fail the record
        assert len(failed) == 1

    def test_partial_batch_failure(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test partial batch failure handling."""
        # First record succeeds
        event1 = sample_stream_event.copy()
        event1["dynamodb"] = sample_stream_event["dynamodb"].copy()
        event1["dynamodb"]["SequenceNumber"] = "111111111"

        # Second record fails (invalid ARN)
        event2 = sample_stream_event.copy()
        event2["dynamodb"] = sample_stream_event["dynamodb"].copy()
        event2["dynamodb"]["SequenceNumber"] = "222222222"
        event2["eventSourceARN"] = "invalid-arn"

        records = [event1, event2]

        failed = process_stream_records(records)

        assert len(failed) == 1
        assert failed[0] == "222222222"
        # First record should have been written
        assert mock_repository.write_change_record.called

    def test_repository_exception(
        self, mock_repository: MagicMock, sample_stream_event: dict
    ) -> None:
        """Test handling of repository exceptions."""
        mock_repository.write_change_record.side_effect = Exception("DB Error")

        records = [sample_stream_event]

        failed = process_stream_records(records)

        # Should fail the record
        assert len(failed) == 1
        assert failed[0] == "123456789"
