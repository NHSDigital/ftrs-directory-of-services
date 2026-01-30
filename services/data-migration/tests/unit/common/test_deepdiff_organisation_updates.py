"""Tests for Organisation update expressions in DeepDiffToDynamoDBConverter."""

from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import EndpointStatus, TelecomType
from ftrs_data_layer.domain.telecom import Telecom

from common.diff_utils import (
    deepdiff_to_dynamodb_expressions,
    get_organisation_diff,
)


class TestOrganisationUpdates:
    def test_simple_string_field_change(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"name": "Updated Organisation"})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_name = :val_0"
        assert result.expression_attribute_names == {"#attr_name": "name"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": "Updated Organisation"}
        }

    def test_boolean_field_change(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"active": False})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_active = :val_0"
        assert result.expression_attribute_names == {"#attr_active": "active"}
        assert result.expression_attribute_values == {":val_0": {"BOOL": False}}

    def test_type_field_change(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(
            update={"type": "Other Organisation Type"}
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #attr_type = :val_0"
        assert result.expression_attribute_names == {"#attr_type": "type"}
        assert result.expression_attribute_values == {
            ":val_0": {"S": "Other Organisation Type"}
        }

    def test_ods_code_change(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(
            update={"identifier_ODS_ODSCode": "NEW001"}
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #identifier_ODS_ODSCode = :val_0"
        assert result.expression_attribute_names == {
            "#identifier_ODS_ODSCode": "identifier_ODS_ODSCode"
        }
        assert result.expression_attribute_values == {":val_0": {"S": "NEW001"}}

    def test_multiple_field_changes(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(
            update={
                "name": "New Name",
                "active": False,
                "identifier_ODS_ODSCode": "NEW999",
            }
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert "#attr_name" in result.update_expression
        assert "#attr_active" in result.update_expression
        assert "#identifier_ODS_ODSCode" in result.update_expression

        assert result.expression_attribute_names["#attr_name"] == "name"
        assert result.expression_attribute_names["#attr_active"] == "active"
        assert (
            result.expression_attribute_names["#identifier_ODS_ODSCode"]
            == "identifier_ODS_ODSCode"
        )

        assert len(result.expression_attribute_values) == 3  # noqa: PLR2004
        values_list = list(result.expression_attribute_values.values())
        assert {"S": "New Name"} in values_list
        assert {"BOOL": False} in values_list
        assert {"S": "NEW999"} in values_list

    def test_add_endpoint_to_organisation(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        modified = base_organisation.model_copy(update={"endpoints": [base_endpoint]})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #endpoints = :val_0"
        assert result.expression_attribute_names == {"#endpoints": "endpoints"}
        assert len(result.expression_attribute_values) == 1

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 1
        assert "M" in val["L"][0]

        endpoint_map = val["L"][0]["M"]
        for field in ["id", "status", "connectionType", "address", "order"]:
            assert field in endpoint_map

        assert endpoint_map["status"] == {"S": EndpointStatus.ACTIVE.value}
        assert endpoint_map["address"] == {"S": "https://test.endpoint.com"}

    def test_remove_endpoint_from_organisation(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        org_with_endpoint = base_organisation.model_copy(
            update={"endpoints": [base_endpoint]}
        )
        modified = org_with_endpoint.model_copy(update={"endpoints": []})
        diff = get_organisation_diff(org_with_endpoint, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #endpoints = :val_0"
        assert result.expression_attribute_names == {"#endpoints": "endpoints"}
        assert result.expression_attribute_values == {":val_0": {"L": []}}

    def test_modify_endpoint_in_organisation(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        org_with_endpoint = base_organisation.model_copy(
            update={"endpoints": [base_endpoint]}
        )
        modified_endpoint = base_endpoint.model_copy(
            update={"address": "https://new.endpoint.com"}
        )
        modified = org_with_endpoint.model_copy(
            update={"endpoints": [modified_endpoint]}
        )
        diff = get_organisation_diff(org_with_endpoint, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #endpoints[0].#attr_address = :val_0"
        assert result.expression_attribute_names == {
            "#endpoints": "endpoints",
            "#attr_address": "address",
        }
        assert result.expression_attribute_values == {
            ":val_0": {"S": "https://new.endpoint.com"}
        }

    def test_add_telecom_to_organisation(
        self,
        base_organisation: Organisation,
    ) -> None:
        new_telecom = Telecom(
            type=TelecomType.EMAIL, value="new@nhs.net", isPublic=True
        )
        modified = base_organisation.model_copy(
            update={"telecom": [*base_organisation.telecom, new_telecom]}
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #telecom = :val_0"
        assert result.expression_attribute_names == {"#telecom": "telecom"}
        assert len(result.expression_attribute_values) == 1

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 2  # noqa: PLR2004

        for item in val["L"]:
            assert "M" in item
            telecom_map = item["M"]
            assert "type" in telecom_map
            assert "value" in telecom_map
            assert "isPublic" in telecom_map
