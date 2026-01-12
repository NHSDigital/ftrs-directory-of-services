"""Tests for DynamoDB expression format and DynamoDBUpdateExpressions dataclass."""

from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain import (
    HealthcareService,
    Location,
    Organisation,
)
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.location import PositionGCS

from common.diff_utils import (
    DynamoDBUpdateExpressions,
    deepdiff_to_dynamodb_expressions,
    get_healthcare_service_diff,
    get_location_diff,
    get_organisation_diff,
)


class TestComplexUpdateScenarios:
    def test_deeply_nested_changes(
        self,
        base_location: Location,
    ) -> None:
        new_position = PositionGCS(
            latitude=Decimal("53.1234"),
            longitude=base_location.positionGCS.longitude,
        )
        modified = base_location.model_copy(update={"positionGCS": new_position})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #positionGCS.#latitude = :val_0"
        assert result.expression_attribute_names == {
            "#positionGCS": "positionGCS",
            "#latitude": "latitude",
        }
        assert result.expression_attribute_values == {":val_0": {"S": "53.1234"}}

    def test_multiple_nested_and_simple_changes(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        new_telecom = base_healthcare_service.telecom.model_copy(
            update={"email": "changed@test.com"}
        )
        modified = base_healthcare_service.model_copy(
            update={
                "name": "Changed Name",
                "active": False,
                "telecom": new_telecom,
            }
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert len(result.expression_attribute_values) == 3  # noqa: PLR2004
        assert "name" in result.expression_attribute_names.values()
        assert "active" in result.expression_attribute_names.values()
        assert "telecom" in result.expression_attribute_names.values()
        assert "email" in result.expression_attribute_names.values()
        values_list = list(result.expression_attribute_values.values())
        assert {"S": "Changed Name"} in values_list
        assert {"BOOL": False} in values_list
        assert {"S": "changed@test.com"} in values_list

    def test_empty_list_to_populated_list(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        modified = base_healthcare_service.model_copy(
            update={"dispositions": ["DX001", "DX002"]}
        )
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #dispositions = :val_0"
        assert result.expression_attribute_names == {"#dispositions": "dispositions"}
        assert result.expression_attribute_values == {
            ":val_0": {"L": [{"S": "DX001"}, {"S": "DX002"}]}
        }

    def test_populated_list_to_empty_list(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        service_with_items = base_healthcare_service.model_copy(
            update={"dispositions": ["DX001", "DX002"]}
        )
        modified = service_with_items.model_copy(update={"dispositions": []})
        diff = get_healthcare_service_diff(service_with_items, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #dispositions = :val_0"
        assert result.expression_attribute_names == {"#dispositions": "dispositions"}
        assert result.expression_attribute_values == {":val_0": {"L": []}}

    def test_reserved_word_handling(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(
            update={
                "name": "New Name",
                "type": "Other Type",
                "active": False,
            }
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "#attr_name" in result.expression_attribute_names
        assert "#attr_type" in result.expression_attribute_names
        assert "#attr_active" in result.expression_attribute_names
        assert result.expression_attribute_names["#attr_name"] == "name"
        assert result.expression_attribute_names["#attr_type"] == "type"
        assert result.expression_attribute_names["#attr_active"] == "active"
        assert len(result.expression_attribute_names) == 3  # noqa: PLR2004

    def test_uuid_field_change(
        self,
        base_location: Location,
    ) -> None:
        new_uuid = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        modified = base_location.model_copy(update={"managingOrganisation": new_uuid})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #managingOrganisation = :val_0"
        assert result.expression_attribute_names == {
            "#managingOrganisation": "managingOrganisation"
        }
        assert result.expression_attribute_values == {
            ":val_0": {"S": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}
        }

    def test_decimal_field_change(
        self,
        base_location: Location,
    ) -> None:
        """GPS coordinates preserve full decimal precision as strings."""
        new_position = PositionGCS(
            latitude=Decimal("55.123456789"),
            longitude=Decimal("-2.987654321"),
        )
        modified = base_location.model_copy(update={"positionGCS": new_position})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert len(result.expression_attribute_values) == 2  # noqa: PLR2004
        assert "positionGCS" in result.expression_attribute_names.values()

        values_list = list(result.expression_attribute_values.values())
        assert {"S": "55.123456789"} in values_list
        assert {"S": "-2.987654321"} in values_list

    def test_integer_field_change(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        org_with_endpoint = base_organisation.model_copy(
            update={"endpoints": [base_endpoint]}
        )
        modified_endpoint = base_endpoint.model_copy(
            update={"identifier_oldDoS_id": 999}
        )
        modified = org_with_endpoint.model_copy(
            update={"endpoints": [modified_endpoint]}
        )
        diff = get_organisation_diff(org_with_endpoint, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert (
            result.update_expression
            == "SET #endpoints[0].#identifier_oldDoS_id = :val_0"
        )
        assert result.expression_attribute_names == {
            "#endpoints": "endpoints",
            "#identifier_oldDoS_id": "identifier_oldDoS_id",
        }
        assert result.expression_attribute_values == {":val_0": {"N": "999"}}


class TestDynamoDBExpressionFormat:
    def test_set_expression_format(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"name": "Test"})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_names == {"#attr_name": "name"}
        assert result.expression_attribute_values == {":val_0": {"S": "Test"}}

    def test_expression_attribute_names_format(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"name": "Test"})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        for key in result.expression_attribute_names:
            assert key.startswith("#")
        assert result.expression_attribute_names == {"#attr_name": "name"}

    def test_expression_attribute_values_format(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(
            update={"name": "Test", "active": False}
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert len(result.expression_attribute_values) == 2  # noqa: PLR2004
        for key in result.expression_attribute_values:
            assert key.startswith(":")
        for key, value in result.expression_attribute_values.items():
            assert isinstance(value, dict)
            assert len(value) == 1
            assert any(
                k in value
                for k in ["S", "N", "BOOL", "L", "M", "NULL", "B", "SS", "NS"]
            )

    def test_multiple_set_clauses_comma_separated(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(
            update={"name": "Test", "active": False}
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression.startswith("SET ")
        parts = result.update_expression.removeprefix("SET ").split(", ")
        assert len(parts) == 2  # noqa: PLR2004
        for part in parts:
            assert "=" in part
            assert part.strip().startswith("#")

    def test_nested_path_format(
        self,
        base_location: Location,
    ) -> None:
        new_address = base_location.address.model_copy(update={"postcode": "NEW"})
        modified = base_location.model_copy(update={"address": new_address})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_address.#postcode = :val_0"
        assert result.expression_attribute_names == {
            "#attr_address": "address",
            "#postcode": "postcode",
        }
        assert result.expression_attribute_values == {":val_0": {"S": "NEW"}}


class TestDynamoDBUpdateExpressionsDataclass:
    def test_is_empty_when_no_expression(self) -> None:
        expressions = DynamoDBUpdateExpressions()
        assert expressions.is_empty()

    def test_is_empty_when_has_expression(self) -> None:
        expressions = DynamoDBUpdateExpressions(
            update_expression="SET #name = :val_0",
            expression_attribute_names={"#name": "name"},
            expression_attribute_values={":val_0": {"S": "Test"}},
        )
        assert not expressions.is_empty()

    def test_default_values(self) -> None:
        expressions = DynamoDBUpdateExpressions()
        assert expressions.update_expression == ""
        assert expressions.expression_attribute_names == {}
        assert expressions.expression_attribute_values == {}

    def test_get_expression_attribute_names_or_none_returns_none_when_empty(
        self,
    ) -> None:
        expressions = DynamoDBUpdateExpressions()
        assert expressions.get_expression_attribute_names_or_none() is None

    def test_get_expression_attribute_names_or_none_returns_dict_when_populated(
        self,
    ) -> None:
        expressions = DynamoDBUpdateExpressions(
            update_expression="SET #name = :val_0",
            expression_attribute_names={"#name": "name"},
            expression_attribute_values={":val_0": {"S": "Test"}},
        )
        assert expressions.get_expression_attribute_names_or_none() == {"#name": "name"}

    def test_get_expression_attribute_values_or_none_returns_none_when_empty(
        self,
    ) -> None:
        expressions = DynamoDBUpdateExpressions()
        assert expressions.get_expression_attribute_values_or_none() is None

    def test_get_expression_attribute_values_or_none_returns_dict_when_populated(
        self,
    ) -> None:
        expressions = DynamoDBUpdateExpressions(
            update_expression="SET #name = :val_0",
            expression_attribute_names={"#name": "name"},
            expression_attribute_values={":val_0": {"S": "Test"}},
        )
        assert expressions.get_expression_attribute_values_or_none() == {
            ":val_0": {"S": "Test"}
        }

    def test_boolean_false_value(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"active": False})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_active = :val_0"
        assert result.expression_attribute_values == {":val_0": {"BOOL": False}}

    def test_special_characters_in_string(
        self,
        base_organisation: Organisation,
    ) -> None:
        special_name = "Dr. O'Brien & Partners (NHS GP Practice)"
        modified = base_organisation.model_copy(update={"name": special_name})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_values == {":val_0": {"S": special_name}}
