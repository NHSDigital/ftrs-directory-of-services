"""Tests for Location update expressions in DeepDiffToDynamoDBConverter."""

from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain import Location
from ftrs_data_layer.domain.location import Address, PositionGCS

from common.diff_utils import (
    deepdiff_to_dynamodb_expressions,
    get_location_diff,
)


class TestLocationUpdates:
    def test_simple_name_change(
        self,
        base_location: Location,
    ) -> None:
        modified = base_location.model_copy(update={"name": "New Location Name"})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_names == {"#attr_name": "name"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": "New Location Name"}
        }

    def test_active_status_change(
        self,
        base_location: Location,
    ) -> None:
        modified = base_location.model_copy(update={"active": False})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_active = :val_0"
        assert result.expression_attribute_names == {"#attr_active": "active"}
        assert result.expression_attribute_values == {":val_0": {"BOOL": False}}

    def test_nested_address_change(
        self,
        base_location: Location,
    ) -> None:
        new_address = Address(
            line1="456 New Street",
            line2="New Area",
            county="New County",
            town="New Town",
            postcode="NE2 2ND",
        )
        modified = base_location.model_copy(update={"address": new_address})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert len(result.expression_attribute_values) == 5  # noqa: PLR2004

        assert "#attr_address" in result.expression_attribute_names
        assert result.expression_attribute_names["#attr_address"] == "address"

        mapped_fields = set(result.expression_attribute_names.values())
        expected_fields = {"address", "line1", "line2", "county", "town", "postcode"}
        assert expected_fields == mapped_fields

        values_list = list(result.expression_attribute_values.values())
        assert {"S": "456 New Street"} in values_list
        assert {"S": "New Area"} in values_list
        assert {"S": "New County"} in values_list
        assert {"S": "New Town"} in values_list
        assert {"S": "NE2 2ND"} in values_list

    def test_single_address_field_change(
        self,
        base_location: Location,
    ) -> None:
        new_address = base_location.address.model_copy(update={"postcode": "NE3 3RD"})
        modified = base_location.model_copy(update={"address": new_address})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_address.#postcode = :val_0"
        assert result.expression_attribute_names == {
            "#attr_address": "address",
            "#postcode": "postcode",
        }
        assert result.expression_attribute_values == {":val_0": {"S": "NE3 3RD"}}

    def test_position_gcs_change(
        self,
        base_location: Location,
    ) -> None:
        """Decimals are converted to strings for healthcare precision."""
        new_position = PositionGCS(latitude=Decimal("52.0"), longitude=Decimal("0.5"))
        modified = base_location.model_copy(update={"positionGCS": new_position})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert len(result.expression_attribute_values) == 2  # noqa: PLR2004

        assert "positionGCS" in result.expression_attribute_names.values()
        assert "latitude" in result.expression_attribute_names.values()
        assert "longitude" in result.expression_attribute_names.values()

        values_list = list(result.expression_attribute_values.values())
        assert {"S": "52.0"} in values_list
        assert {"S": "0.5"} in values_list

    def test_managing_organisation_change(
        self,
        base_location: Location,
    ) -> None:
        new_org_id = UUID("99999999-9999-9999-9999-999999999999")
        modified = base_location.model_copy(update={"managingOrganisation": new_org_id})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #managingOrganisation = :val_0"
        assert result.expression_attribute_names == {
            "#managingOrganisation": "managingOrganisation"
        }
        assert result.expression_attribute_values == {
            ":val_0": {"S": "99999999-9999-9999-9999-999999999999"}
        }

    def test_primary_address_change(
        self,
        base_location: Location,
    ) -> None:
        modified = base_location.model_copy(update={"primaryAddress": False})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #primaryAddress = :val_0"
        assert result.expression_attribute_names == {
            "#primaryAddress": "primaryAddress"
        }
        assert result.expression_attribute_values == {":val_0": {"BOOL": False}}

    def test_set_optional_field_to_none(
        self,
        base_location: Location,
    ) -> None:
        modified = base_location.model_copy(update={"name": None})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "REMOVE" in result.update_expression or "SET" in result.update_expression
        assert (
            "#attr_name" in result.expression_attribute_names
            or "#name" in result.expression_attribute_names
        )
        assert "name" in result.expression_attribute_names.values()

    def test_set_none_field_to_value(
        self,
        base_location: Location,
    ) -> None:
        loc_with_none = base_location.model_copy(update={"name": None})
        modified = loc_with_none.model_copy(update={"name": "New Name"})
        diff = get_location_diff(loc_with_none, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_names == {"#attr_name": "name"}
        assert result.expression_attribute_values == {":val_0": {"S": "New Name"}}

    def test_empty_string_value(
        self,
        base_location: Location,
    ) -> None:
        loc_with_empty = base_location.model_copy(update={"name": ""})
        diff = get_location_diff(base_location, loc_with_empty)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_values == {":val_0": {"S": ""}}

    def test_unicode_characters_in_address(
        self,
        base_location: Location,
    ) -> None:
        welsh_address = base_location.address.model_copy(
            update={
                "town": "Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch"
            }
        )
        modified = base_location.model_copy(update={"address": welsh_address})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "#town" in result.expression_attribute_names
        values_list = list(result.expression_attribute_values.values())
        assert {
            "S": "Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch"
        } in values_list

    def test_high_precision_gps_coordinates(
        self,
        base_location: Location,
    ) -> None:
        high_precision = PositionGCS(
            latitude=Decimal("51.507351234567"),
            longitude=Decimal("-0.127758123456"),
        )
        modified = base_location.model_copy(update={"positionGCS": high_precision})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        values_list = list(result.expression_attribute_values.values())
        assert {"S": "51.507351234567"} in values_list
        assert {"S": "-0.127758123456"} in values_list

    def test_negative_coordinates(
        self,
        base_location: Location,
    ) -> None:
        positive_position = PositionGCS(
            latitude=Decimal("51.5074"),
            longitude=Decimal("1.2345"),
        )
        location_with_positive = base_location.model_copy(
            update={"positionGCS": positive_position}
        )

        negative_position = PositionGCS(
            latitude=Decimal("51.5074"),
            longitude=Decimal("-0.1278"),
        )
        modified = location_with_positive.model_copy(
            update={"positionGCS": negative_position}
        )
        diff = get_location_diff(location_with_positive, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert len(result.expression_attribute_values) == 1
        values_list = list(result.expression_attribute_values.values())
        assert {"S": "-0.1278"} in values_list
