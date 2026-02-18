"""Unit tests for version history utility functions."""

from decimal import Decimal
from typing import Any, Dict

import pytest

from version_history.utils import (
    deserialize_dynamodb_item,
    extract_changed_by,
    extract_table_name_from_arn,
)


class TestExtractTableNameFromArn:
    """Tests for extract_table_name_from_arn function."""

    def test_extract_table_name_from_full_arn(self) -> None:
        """Test extracting table name from full ARN."""
        arn = (
            "arn:aws:dynamodb:eu-west-2:123456789012:table/"
            "ftrs-dos-local-database-organisation-test/stream/"
            "2025-01-01T00:00:00.000"
        )
        result = extract_table_name_from_arn(arn)
        assert result == "ftrs-dos-local-database-organisation-test"

    def test_extract_table_name_handles_short_table_name(self) -> None:
        """Test extracting simple table name."""
        arn = (
            "arn:aws:dynamodb:eu-west-2:123456789012:table/organisation/"
            "stream/2025-01-01T00:00:00.000"
        )
        result = extract_table_name_from_arn(arn)
        assert result == "organisation"

    def test_extract_table_name_handles_malformed_arn(self) -> None:
        """Test handling malformed ARN."""
        arn = "invalid-arn"
        result = extract_table_name_from_arn(arn)
        assert result == ""

    @pytest.mark.parametrize(
        "arn,expected",
        [
            (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/ftrs-dos-dev-database-organisation/stream/2025",
                "ftrs-dos-dev-database-organisation",
            ),
            (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/ftrs-dos-local-database-healthcare-service-test/stream/2025",
                "ftrs-dos-local-database-healthcare-service-test",
            ),
            (
                "arn:aws:dynamodb:eu-west-2:123456789012:table/ftrs-dos-prod-database-location/stream/2025",
                "ftrs-dos-prod-database-location",
            ),
        ],
    )
    def test_extract_table_name_parametrized(self, arn: str, expected: str) -> None:
        """Test extracting table names from various realistic ARNs."""
        result = extract_table_name_from_arn(arn)
        assert result == expected


class TestDeserializeDynamoDBItem:
    """Tests for deserialize_dynamodb_item function."""

    def test_deserialize_string_values(self) -> None:
        """Test deserializing string values."""
        item = {"field": {"S": "value"}, "id": {"S": "123"}}
        result = deserialize_dynamodb_item(item)
        assert result == {"field": "value", "id": "123"}

    def test_deserialize_map_values(self) -> None:
        """Test deserializing map (dict) values."""
        item = {
            "lastUpdatedBy": {
                "M": {
                    "type": {"S": "app"},
                    "value": {"S": "INTERNAL001"},
                    "display": {"S": "Data Migration"},
                }
            }
        }
        result = deserialize_dynamodb_item(item)
        assert result == {
            "lastUpdatedBy": {
                "type": "app",
                "value": "INTERNAL001",
                "display": "Data Migration",
            }
        }

    def test_deserialize_empty_item(self) -> None:
        """Test deserializing empty item."""
        item: Dict[str, Any] = {}
        result = deserialize_dynamodb_item(item)
        assert result == {}

    def test_deserialize_number_values(self) -> None:
        """Test deserializing number values."""
        item = {"count": {"N": "42"}, "price": {"N": "19.99"}}
        result = deserialize_dynamodb_item(item)
        assert result == {"count": Decimal(42), "price": Decimal("19.99")}

    def test_deserialize_boolean_values(self) -> None:
        """Test deserializing boolean values."""
        item = {"active": {"BOOL": True}, "deleted": {"BOOL": False}}
        result = deserialize_dynamodb_item(item)
        assert result == {"active": True, "deleted": False}

    def test_deserialize_list_values(self) -> None:
        """Test deserializing list values."""
        item = {"tags": {"L": [{"S": "tag1"}, {"S": "tag2"}]}}
        result = deserialize_dynamodb_item(item)
        assert result == {"tags": ["tag1", "tag2"]}


class TestExtractChangedBy:
    """Tests for extract_changed_by function."""

    def test_extract_changed_by_from_valid_image(self) -> None:
        """Test extracting ChangedBy from valid NewImage."""
        new_image = {
            "lastUpdatedBy": {
                "type": "app",
                "value": "INTERNAL001",
                "display": "Data Migration",
            }
        }
        result = extract_changed_by(new_image)
        assert result == {
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        }

    def test_extract_changed_by_from_user_image(self) -> None:
        """Test extracting ChangedBy from user-initiated change."""
        new_image = {
            "lastUpdatedBy": {
                "type": "user",
                "value": "user-123",
                "display": "John Doe",
            }
        }
        result = extract_changed_by(new_image)
        assert result == {
            "type": "user",
            "value": "user-123",
            "display": "John Doe",
        }

    def test_extract_changed_by_defaults_when_missing(self) -> None:
        """Test default values when lastUpdatedBy is missing."""
        new_image: Dict[str, Any] = {}
        result = extract_changed_by(new_image)
        assert result == {
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        }

    def test_extract_changed_by_handles_partial_data(self) -> None:
        """Test handling partial lastUpdatedBy data."""
        new_image = {"lastUpdatedBy": {"type": "app"}}
        result = extract_changed_by(new_image)
        assert result == {
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        }

    @pytest.mark.parametrize(
        "last_updated_by,expected",
        [
            (
                {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
                {"type": "app", "value": "INTERNAL001", "display": "Data Migration"},
            ),
            (
                {"type": "user", "value": "user-456", "display": "Jane Smith"},
                {"type": "user", "value": "user-456", "display": "Jane Smith"},
            ),
            (
                {"type": "system", "value": "cron-job", "display": "Scheduled Task"},
                {"type": "system", "value": "cron-job", "display": "Scheduled Task"},
            ),
            ({}, {"type": "app", "value": "INTERNAL001", "display": "Data Migration"}),
        ],
    )
    def test_extract_changed_by_parametrized(
        self, last_updated_by: Dict[str, str], expected: Dict[str, str]
    ) -> None:
        """Test extracting ChangedBy with various input scenarios."""
        new_image = {"lastUpdatedBy": last_updated_by} if last_updated_by else {}
        result = extract_changed_by(new_image)
        assert result == expected
