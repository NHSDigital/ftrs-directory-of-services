"""Unit tests for version history stream processor."""

from typing import Any, Dict
from unittest.mock import MagicMock

from version_history.stream_processor import process_stream_record


class TestProcessStreamRecord:
    """Tests for process_stream_record function."""

    def test_process_organisation_record_successfully(
        self,
        sample_organisation_stream_record: Dict[str, Any],
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test processing Organisation stream record successfully."""
        process_stream_record(
            sample_organisation_stream_record, mock_version_history_table
        )

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        expected_entity_id = "organisation|550e8400-e29b-41d4-a716-446655440000|name"
        assert item["entity_id"] == expected_entity_id
        assert item["change_type"] == "UPDATE"
        assert item["changed_fields"] == {
            "name": {"old": "Old Organisation Name", "new": "New Organisation Name"}
        }
        assert item["changed_by"]["type"] == "app"
        assert item["changed_by"]["value"] == "INTERNAL001"
        assert "timestamp" in item

    def test_process_record_processes_location_table(
        self,
        sample_location_stream_record: Dict[str, Any],
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test that Location table records are processed."""
        process_stream_record(sample_location_stream_record, mock_version_history_table)

        # Should write to version history for Location table
        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        expected_entity_id = "location|660e8400-e29b-41d4-a716-446655440000|status"
        assert item["entity_id"] == expected_entity_id
        assert item["change_type"] == "UPDATE"
        assert item["changed_fields"] == {"status": {"old": "pending", "new": "active"}}
        assert item["changed_by"]["type"] == "user"
        assert item["changed_by"]["value"] == "user-123"

    def test_process_record_skips_identical_values(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test that records with identical old/new values are skipped."""
        record = {
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-local-database-organisation-test/stream/"
                "2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "status"},
                },
                "OldImage": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "status"},
                    "value": {"S": "active"},
                },
                "NewImage": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "status"},
                    "value": {"S": "active"},
                },
            },
        }

        process_stream_record(record, mock_version_history_table)

        # Should not write to version history for no-op updates
        mock_version_history_table.put_item.assert_not_called()

    def test_process_record_handles_missing_keys(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test handling record with missing id or field keys."""
        record = {
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-local-database-organisation-test/stream/"
                "2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {"id": {"S": "550e8400-e29b-41d4-a716-446655440000"}},
                "NewImage": {"value": {"S": "new_value"}},
            },
        }

        # Should not raise exception, should log warning and skip
        process_stream_record(record, mock_version_history_table)
        mock_version_history_table.put_item.assert_not_called()

    def test_process_record_handles_new_field_creation(
        self,
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test processing record where OldImage is missing (new field creation)."""
        record = {
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-local-database-organisation-test/stream/"
                "2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "newField"},
                },
                "NewImage": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "newField"},
                    "value": {"S": "new_value"},
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                },
            },
        }

        process_stream_record(record, mock_version_history_table)

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        expected_changed_fields = {"newField": {"old": None, "new": "new_value"}}
        assert item["changed_fields"] == expected_changed_fields

    def test_process_record_with_healthcare_service_table_name(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test processing record with multi-word entity name (healthcare-service)."""
        record = {
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-dev-database-healthcare-service/stream/"
                "2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "770e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "name"},
                },
                "OldImage": {
                    "value": {"S": "Old Service Name"},
                },
                "NewImage": {
                    "value": {"S": "New Service Name"},
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                },
            },
        }

        # Healthcare service should now be processed
        process_stream_record(record, mock_version_history_table)
        mock_version_history_table.put_item.assert_called_once()

        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        expected_entity_id = (
            "healthcare-service|770e8400-e29b-41d4-a716-446655440000|name"
        )
        assert item["entity_id"] == expected_entity_id
        assert item["change_type"] == "UPDATE"
        expected_changed_fields = {
            "name": {"old": "Old Service Name", "new": "New Service Name"}
        }
        assert item["changed_fields"] == expected_changed_fields
        assert item["changed_by"]["type"] == "app"
        assert item["changed_by"]["value"] == "INTERNAL001"

    def test_process_record_handles_insert_event(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test processing INSERT event (new record creation)."""
        record = {
            "eventName": "INSERT",
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-local-database-organisation-test/stream/"
                "2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "name"},
                },
                "NewImage": {
                    "id": {"S": "550e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "name"},
                    "value": {"S": "New Organisation"},
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                },
            },
        }

        process_stream_record(record, mock_version_history_table)

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        assert item["change_type"] == "CREATE"
        expected_changed_fields = {"name": {"old": None, "new": "New Organisation"}}
        assert item["changed_fields"] == expected_changed_fields

    def test_process_record_handles_remove_event(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test processing REMOVE event (record deletion)."""
        record = {
            "eventName": "REMOVE",
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-local-database-location-test/stream/"
                "2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "660e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "status"},
                },
                "OldImage": {
                    "id": {"S": "660e8400-e29b-41d4-a716-446655440000"},
                    "field": {"S": "status"},
                    "value": {"S": "active"},
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "user"},
                            "value": {"S": "user-123"},
                            "display": {"S": "John Doe"},
                        }
                    },
                },
            },
        }

        process_stream_record(record, mock_version_history_table)

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        assert item["change_type"] == "DELETE"
        expected_changed_fields = {"status": {"old": "active", "new": None}}
        assert item["changed_fields"] == expected_changed_fields
        assert item["changed_by"]["type"] == "user"
        assert item["changed_by"]["value"] == "user-123"
