"""Unit tests for version history utility functions."""

from typing import Any, Dict

import pytest

from version_history.utils import (
    compute_field_delta,
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
        assert "values_changed" in result
        assert "root" in result["values_changed"]
        assert (
            result["values_changed"]["root"]["old_value"] == "Riverside Medical Centre"
        )
        assert (
            result["values_changed"]["root"]["new_value"] == "Riverside Health Practice"
        )

    def test_compute_delta_for_integer_values(self) -> None:
        """Test computing delta for integer values."""
        old_integer_value = 12345678
        new_integer_value = 87654321
        result = compute_field_delta(old_integer_value, new_integer_value)
        assert "values_changed" in result
        assert result["values_changed"]["root"]["old_value"] == old_integer_value
        assert result["values_changed"]["root"]["new_value"] == new_integer_value

    def test_compute_delta_for_boolean_values(self) -> None:
        """Test computing delta for boolean values."""
        result = compute_field_delta(False, True)
        assert "values_changed" in result
        assert result["values_changed"]["root"]["old_value"] is False
        assert result["values_changed"]["root"]["new_value"] is True

    def test_compute_delta_for_none_values(self) -> None:
        """Test computing delta when old value is None."""
        result = compute_field_delta(None, "F84001")
        # DeepDiff reports None -> value as type_changes
        assert "type_changes" in result
        assert result["type_changes"]["root"]["old_value"] is None
        assert result["type_changes"]["root"]["new_value"] == "F84001"

    def test_compute_delta_for_none_to_none(self) -> None:
        """Test computing delta when both values are None."""
        result = compute_field_delta(None, None)
        # Identical values produce empty dict
        assert result == {}

    def test_compute_delta_for_dict_values(self) -> None:
        """Test computing delta for dictionary values."""
        old_dict = {"phone_public": "0300 123 4567", "email": "old@practice.nhs.uk"}
        new_dict = {"phone_public": "0300 987 6543", "web": "https://practice.nhs.uk"}
        result = compute_field_delta(old_dict, new_dict)

        # DeepDiff should report changed, added, and removed items
        assert "values_changed" in result  # phone_public changed
        assert "dictionary_item_added" in result  # web added
        assert "dictionary_item_removed" in result  # email removed
        assert (
            result["values_changed"]["root['phone_public']"]["old_value"]
            == "0300 123 4567"
        )
        assert (
            result["values_changed"]["root['phone_public']"]["new_value"]
            == "0300 987 6543"
        )

    def test_compute_delta_for_list_values(self) -> None:
        """Test computing delta for list values."""
        old_list = ["Dx01", "Dx02", "Dx03"]
        new_list = ["Dx01", "Dx04", "Dx05"]
        result = compute_field_delta(old_list, new_list)

        # DeepDiff reports list changes
        assert (
            "values_changed" in result
            or "iterable_item_added" in result
            or "iterable_item_removed" in result
        )
        assert isinstance(result, dict)

    def test_compute_delta_for_type_mismatch(self) -> None:
        """Test computing delta when types don't match."""
        result = compute_field_delta(
            "0300 123 4567",
            {"phone_public": "0300 123 4567", "phone_private": "0300 111 2222"},
        )
        # DeepDiff reports type changes
        assert "type_changes" in result
        assert "root" in result["type_changes"]
        assert result["type_changes"]["root"]["old_value"] == "0300 123 4567"
        assert result["type_changes"]["root"]["new_value"] == {
            "phone_public": "0300 123 4567",
            "phone_private": "0300 111 2222",
        }

    def test_compute_delta_for_identical_dict_values(self) -> None:
        """Test computing delta for identical dictionary values."""
        test_dict = {
            "line1": "123 High Street",
            "postcode": "SW1A 1AA",
            "town": "London",
        }
        result = compute_field_delta(test_dict, test_dict)

        # Identical values produce empty dict
        assert result == {}

    def test_compute_delta_for_nested_dict_values(self) -> None:
        """Test computing delta for nested dictionary values."""
        old_dict = {"positionGCS": {"latitude": "51.5074", "longitude": "-0.1278"}}
        new_dict = {"positionGCS": {"latitude": "51.5075", "longitude": "-0.1278"}}
        result = compute_field_delta(old_dict, new_dict)

        # DeepDiff should show nested path to changed value
        assert "values_changed" in result
        assert "root['positionGCS']['latitude']" in result["values_changed"]
        assert (
            result["values_changed"]["root['positionGCS']['latitude']"]["old_value"]
            == "51.5074"
        )
        assert (
            result["values_changed"]["root['positionGCS']['latitude']"]["new_value"]
            == "51.5075"
        )

    @pytest.mark.parametrize(
        "old_value,new_value,is_identical",
        [
            ("Riverside Medical Centre", "Riverside Health Practice", False),
            (12345678, 87654321, False),
            (False, True, False),
            (None, "F84001", False),
            (
                {"identifier_ODS_ODSCode": "A12345"},
                {"identifier_ODS_ODSCode": "B67890"},
                False,
            ),
            (["Dx01", "Dx02"], ["Dx03", "Dx04"], False),
            ("active", {"active": True, "primaryAddress": False}, False),
        ],
    )
    def test_compute_delta_parametrized(
        self,
        old_value: Any,  # noqa: ANN401
        new_value: Any,  # noqa: ANN401
        is_identical: bool,
    ) -> None:
        """Test computing delta with various value types."""
        result = compute_field_delta(old_value, new_value)

        # All test cases have differences, so result should not be empty
        if is_identical:
            assert result == {}
        else:
            assert result  # Non-empty dict
            assert isinstance(result, dict)
