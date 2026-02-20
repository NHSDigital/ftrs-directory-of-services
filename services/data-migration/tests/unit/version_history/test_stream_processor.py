"""Unit tests for version history stream processor."""

from typing import Any, Dict
from unittest.mock import MagicMock

from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecord,
)

from version_history.stream_processor import process_stream_record


class TestProcessStreamRecord:
    """Tests for process_stream_record function."""

    def test_process_organisation_document_field_change(
        self,
        sample_organisation_document_stream_record: Dict[str, Any],
        mock_version_history_table: MagicMock,
    ) -> None:
        """Test processing Organisation document field (full document storage pattern)."""
        record = DynamoDBRecord(sample_organisation_document_stream_record)
        process_stream_record(record, mock_version_history_table)

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        expected_entity_id = (
            "organisation|d0d6af8a-1138-5a2f-a4e2-5f489fb44653|document"
        )
        assert item["entity_id"] == expected_entity_id
        assert item["change_type"] == "UPDATE"
        assert "document" in item["changed_fields"]

        # Verify that the document field contains a diff of the changes
        document_delta = item["changed_fields"]["document"]
        assert "diff" in document_delta
        assert "old" in document_delta
        assert "new" in document_delta

        # Verify system fields were excluded from the values
        old_val = document_delta["old"]
        new_val = document_delta["new"]
        assert "id" not in old_val
        assert "field" not in old_val
        assert "created" not in old_val
        assert "lastUpdated" not in old_val
        assert "name" in old_val
        assert old_val["name"] == "Old Practice Name"
        assert new_val["name"] == "New Practice Name"

        assert item["changed_by"]["type"] == "app"
        assert item["changed_by"]["value"] == "INTERNAL001"

    def test_process_document_field_skips_when_no_changes(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test that document field updates with no actual changes are skipped."""
        record_dict = {
            "eventName": "MODIFY",
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-dev-database-organisation/stream/"
                "2026-02-20T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "d0d6af8a-1138-5a2f-a4e2-5f489fb44653"},
                    "field": {"S": "document"},
                },
                "OldImage": {
                    "id": {"S": "d0d6af8a-1138-5a2f-a4e2-5f489fb44653"},
                    "field": {"S": "document"},
                    "created": {"S": "2026-02-17T14:28:01.640710Z"},
                    "lastUpdated": {"S": "2026-02-17T14:28:01.640710Z"},
                    "createdBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                    "name": {"S": "Same Practice Name"},
                    "active": {"BOOL": True},
                },
                "NewImage": {
                    "id": {"S": "d0d6af8a-1138-5a2f-a4e2-5f489fb44653"},
                    "field": {"S": "document"},
                    "created": {"S": "2026-02-17T14:28:01.640710Z"},
                    "lastUpdated": {"S": "2026-02-20T14:45:00.000000Z"},
                    "createdBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                    "name": {"S": "Same Practice Name"},
                    "active": {"BOOL": True},
                },
            },
        }

        record = DynamoDBRecord(record_dict)
        process_stream_record(record, mock_version_history_table)

        # Should not write to version history when only metadata changed
        mock_version_history_table.put_item.assert_not_called()

    def test_process_document_field_handles_insert_event(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test processing INSERT event (new document creation)."""
        record_dict = {
            "eventName": "INSERT",
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-dev-database-organisation/stream/"
                "2026-02-20T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"},
                    "field": {"S": "document"},
                },
                "NewImage": {
                    "id": {"S": "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"},
                    "field": {"S": "document"},
                    "created": {"S": "2026-02-20T10:00:00.000000Z"},
                    "lastUpdated": {"S": "2026-02-20T10:00:00.000000Z"},
                    "createdBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "app"},
                            "value": {"S": "INTERNAL001"},
                            "display": {"S": "Data Migration"},
                        }
                    },
                    "name": {"S": "New Practice Name"},
                    "active": {"BOOL": True},
                    "identifier_ODS_ODSCode": {"S": "B98765"},
                    "type": {"S": "GP Practice"},
                },
            },
        }

        record = DynamoDBRecord(record_dict)
        process_stream_record(record, mock_version_history_table)

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        assert item["change_type"] == "CREATE"
        expected_changed_fields = {
            "document": {
                "old": None,
                "new": {
                    "name": "New Practice Name",
                    "active": True,
                    "identifier_ODS_ODSCode": "B98765",
                    "type": "GP Practice",
                },
            }
        }
        assert item["changed_fields"] == expected_changed_fields
        assert item["changed_by"]["type"] == "app"
        assert item["changed_by"]["value"] == "INTERNAL001"

    def test_process_document_field_handles_remove_event(
        self, mock_version_history_table: MagicMock
    ) -> None:
        """Test processing REMOVE event (document deletion)."""
        record_dict = {
            "eventName": "REMOVE",
            "eventSourceARN": (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/"
                "ftrs-dos-dev-database-location/stream/"
                "2026-02-20T00:00:00.000"
            ),
            "dynamodb": {
                "Keys": {
                    "id": {"S": "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"},
                    "field": {"S": "document"},
                },
                "OldImage": {
                    "id": {"S": "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"},
                    "field": {"S": "document"},
                    "created": {"S": "2026-01-15T10:00:00.000000Z"},
                    "lastUpdated": {"S": "2026-02-10T15:30:00.000000Z"},
                    "createdBy": {
                        "M": {
                            "type": {"S": "user"},
                            "value": {"S": "user-456"},
                            "display": {"S": "Jane Smith"},
                        }
                    },
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": "user"},
                            "value": {"S": "user-456"},
                            "display": {"S": "Jane Smith"},
                        }
                    },
                    "name": {"S": "Old Location Name"},
                    "status": {"S": "active"},
                    "physicalType": {"S": "building"},
                },
            },
        }

        record = DynamoDBRecord(record_dict)
        process_stream_record(record, mock_version_history_table)

        mock_version_history_table.put_item.assert_called_once()
        call_args = mock_version_history_table.put_item.call_args
        item = call_args.kwargs["Item"]

        assert item["change_type"] == "DELETE"
        expected_changed_fields = {
            "document": {
                "old": {
                    "name": "Old Location Name",
                    "status": "active",
                    "physicalType": "building",
                },
                "new": None,
            }
        }
        assert item["changed_fields"] == expected_changed_fields
        assert item["changed_by"]["type"] == "user"
        assert item["changed_by"]["value"] == "user-456"
