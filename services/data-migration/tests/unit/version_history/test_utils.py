"""Unit tests for version history utility functions."""

from decimal import Decimal
from typing import Any, Dict

import pytest

from version_history.utils import (
    compute_field_delta,
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
        item = {
            "name": {"S": "City Medical Centre"},
            "identifier_ODS_ODSCode": {"S": "A12345"},
        }
        result = deserialize_dynamodb_item(item)
        assert result == {
            "name": "City Medical Centre",
            "identifier_ODS_ODSCode": "A12345",
        }

    def test_deserialize_map_values(self) -> None:
        """Test deserializing map (dict) values."""
        item = {
            "telecom": {
                "M": {
                    "phone_public": {"S": "0300 123 4567"},
                    "email": {"S": "contact@practice.nhs.uk"},
                    "web": {"S": "https://practice.nhs.uk"},
                }
            }
        }
        result = deserialize_dynamodb_item(item)
        assert result == {
            "telecom": {
                "phone_public": "0300 123 4567",
                "email": "contact@practice.nhs.uk",
                "web": "https://practice.nhs.uk",
            }
        }

    def test_deserialize_empty_item(self) -> None:
        """Test deserializing empty item."""
        item: Dict[str, Any] = {}
        result = deserialize_dynamodb_item(item)
        assert result == {}

    def test_deserialize_number_values(self) -> None:
        """Test deserializing number values."""
        item = {
            "positionReferenceNumber_UPRN": {"N": "12345678"},
            "latitude": {"N": "51.5074"},
        }
        result = deserialize_dynamodb_item(item)
        assert result == {
            "positionReferenceNumber_UPRN": Decimal(12345678),
            "latitude": Decimal("51.5074"),
        }

    def test_deserialize_boolean_values(self) -> None:
        """Test deserializing boolean values."""
        item = {"active": {"BOOL": True}, "primaryAddress": {"BOOL": False}}
        result = deserialize_dynamodb_item(item)
        assert result == {"active": True, "primaryAddress": False}

    def test_deserialize_list_values(self) -> None:
        """Test deserializing list values."""
        item = {"dispositions": {"L": [{"S": "Dx01"}, {"S": "Dx02"}]}}
        result = deserialize_dynamodb_item(item)
        assert result == {"dispositions": ["Dx01", "Dx02"]}


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


class TestComputeFieldDelta:
    """Tests for compute_field_delta function."""

    def test_compute_delta_for_simple_string_values(self) -> None:
        """Test computing delta for simple string values."""
        result = compute_field_delta(
            "Riverside Medical Centre", "Riverside Health Practice"
        )
        assert result == {
            "old": "Riverside Medical Centre",
            "new": "Riverside Health Practice",
        }
        assert "diff" not in result

    def test_compute_delta_for_integer_values(self) -> None:
        """Test computing delta for integer values."""
        result = compute_field_delta(12345678, 87654321)
        assert result == {"old": 12345678, "new": 87654321}
        assert "diff" not in result

    def test_compute_delta_for_boolean_values(self) -> None:
        """Test computing delta for boolean values."""
        result = compute_field_delta(False, True)
        assert result == {"old": False, "new": True}
        assert "diff" not in result

    def test_compute_delta_for_none_values(self) -> None:
        """Test computing delta when old value is None."""
        result = compute_field_delta(None, "F84001")
        assert result == {"old": None, "new": "F84001"}
        assert "diff" not in result

    def test_compute_delta_for_none_to_none(self) -> None:
        """Test computing delta when both values are None."""
        result = compute_field_delta(None, None)
        assert result == {"old": None, "new": None}
        assert "diff" not in result

    def test_compute_delta_for_dict_values(self) -> None:
        """Test computing delta for dictionary values."""
        old_dict = {"phone_public": "0300 123 4567", "email": "old@practice.nhs.uk"}
        new_dict = {"phone_public": "0300 987 6543", "web": "https://practice.nhs.uk"}
        result = compute_field_delta(old_dict, new_dict)

        assert result["old"] == old_dict
        assert result["new"] == new_dict
        assert "diff" in result
        assert isinstance(result["diff"], dict)

    def test_compute_delta_for_list_values(self) -> None:
        """Test computing delta for list values."""
        old_list = ["Dx01", "Dx02", "Dx03"]
        new_list = ["Dx01", "Dx04", "Dx05"]
        result = compute_field_delta(old_list, new_list)

        assert result["old"] == old_list
        assert result["new"] == new_list
        assert "diff" in result
        assert isinstance(result["diff"], dict)

    def test_compute_delta_for_type_mismatch(self) -> None:
        """Test computing delta when types don't match."""
        result = compute_field_delta(
            "0300 123 4567",
            {"phone_public": "0300 123 4567", "phone_private": "0300 111 2222"},
        )
        assert result == {
            "old": "0300 123 4567",
            "new": {"phone_public": "0300 123 4567", "phone_private": "0300 111 2222"},
        }
        assert "diff" not in result

    def test_compute_delta_for_identical_dict_values(self) -> None:
        """Test computing delta for identical dictionary values."""
        test_dict = {
            "line1": "123 High Street",
            "postcode": "SW1A 1AA",
            "town": "London",
        }
        result = compute_field_delta(test_dict, test_dict)

        assert result["old"] == test_dict
        assert result["new"] == test_dict
        assert "diff" in result

    def test_compute_delta_for_nested_dict_values(self) -> None:
        """Test computing delta for nested dictionary values."""
        old_dict = {"positionGCS": {"latitude": "51.5074", "longitude": "-0.1278"}}
        new_dict = {"positionGCS": {"latitude": "51.5075", "longitude": "-0.1278"}}
        result = compute_field_delta(old_dict, new_dict)

        assert result["old"] == old_dict
        assert result["new"] == new_dict
        assert "diff" in result

    @pytest.mark.parametrize(
        "old_value,new_value,has_diff",
        [
            ("Riverside Medical Centre", "Riverside Health Practice", False),
            (12345678, 87654321, False),
            (False, True, False),
            (None, "F84001", False),
            (
                {"identifier_ODS_ODSCode": "A12345"},
                {"identifier_ODS_ODSCode": "B67890"},
                True,
            ),
            (["Dx01", "Dx02"], ["Dx03", "Dx04"], True),
            ("active", {"active": True, "primaryAddress": False}, False),
        ],
    )
    def test_compute_delta_parametrized(
        self,
        old_value: Any,  # noqa: ANN401
        new_value: Any,  # noqa: ANN401
        has_diff: bool,  # noqa: ANN401
    ) -> None:
        """Test computing delta with various value types."""
        result = compute_field_delta(old_value, new_value)

        assert result["old"] == old_value
        assert result["new"] == new_value
        if has_diff:
            assert "diff" in result
        else:
            assert "diff" not in result
