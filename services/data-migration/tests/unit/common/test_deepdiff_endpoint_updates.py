"""Tests for Endpoint update expressions in DeepDiffToDynamoDBConverter."""

from uuid import UUID

import pytest
from ftrs_data_layer.domain import Organisation
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointStatus,
)

from common.diff_utils import deepdiff_to_dynamodb_expressions, get_organisation_diff


def _modify_endpoint_field(
    org: Organisation, endpoint: Endpoint, update: dict[str, object]
) -> tuple:
    """Helper to create org with endpoint and apply a modification."""
    org_with_endpoint = org.model_copy(update={"endpoints": [endpoint]})
    modified_endpoint = endpoint.model_copy(update=update)
    modified = org_with_endpoint.model_copy(update={"endpoints": [modified_endpoint]})
    diff = get_organisation_diff(org_with_endpoint, modified)
    return deepdiff_to_dynamodb_expressions(diff)


class TestEndpointUpdates:
    @pytest.mark.parametrize(
        ("field", "value", "expected_expr", "expected_names", "expected_val"),
        [
            (
                "status",
                EndpointStatus.OFF,
                "SET #endpoints[0].#attr_status = :val_0",
                {"#endpoints": "endpoints", "#attr_status": "status"},
                {"S": EndpointStatus.OFF.value},
            ),
            (
                "address",
                "https://updated.endpoint.nhs.uk",
                "SET #endpoints[0].#attr_address = :val_0",
                {"#endpoints": "endpoints", "#attr_address": "address"},
                {"S": "https://updated.endpoint.nhs.uk"},
            ),
            (
                "connectionType",
                EndpointConnectionType.EMAIL,
                "SET #endpoints[0].#connectionType = :val_0",
                {"#endpoints": "endpoints", "#connectionType": "connectionType"},
                {"S": EndpointConnectionType.EMAIL.value},
            ),
            (
                "businessScenario",
                EndpointBusinessScenario.COPY,
                "SET #endpoints[0].#businessScenario = :val_0",
                {"#endpoints": "endpoints", "#businessScenario": "businessScenario"},
                {"S": EndpointBusinessScenario.COPY.value},
            ),
            (
                "order",
                2,
                "SET #endpoints[0].#attr_order = :val_0",
                {"#endpoints": "endpoints", "#attr_order": "order"},
                {"N": "2"},
            ),
            (
                "isCompressionEnabled",
                True,
                "SET #endpoints[0].#isCompressionEnabled = :val_0",
                {
                    "#endpoints": "endpoints",
                    "#isCompressionEnabled": "isCompressionEnabled",
                },
                {"BOOL": True},
            ),
        ],
    )
    def test_endpoint_field_change(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
        field: str,
        value: object,
        expected_expr: str,
        expected_names: dict,
        expected_val: dict,
    ) -> None:
        result = _modify_endpoint_field(
            base_organisation, base_endpoint, {field: value}
        )

        assert result.update_expression == expected_expr
        assert result.expression_attribute_names == expected_names
        assert result.expression_attribute_values == {":val_0": expected_val}

    def test_add_multiple_endpoints(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        endpoint2 = base_endpoint.model_copy(
            update={
                "id": UUID("a66cafc4-eee0-403e-bdcb-46d4c079f6ac"),
                "order": 2,
                "businessScenario": EndpointBusinessScenario.COPY,
            }
        )
        modified = base_organisation.model_copy(
            update={"endpoints": [base_endpoint, endpoint2]}
        )
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #endpoints = :val_0"
        assert result.expression_attribute_names == {"#endpoints": "endpoints"}

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 2  # noqa: PLR2004

        # Each item should be a map with endpoint fields
        for i, item in enumerate(val["L"]):
            assert "M" in item
            endpoint_map = item["M"]
            assert "id" in endpoint_map
            assert "order" in endpoint_map

        assert val["L"][0]["M"]["order"] == {"N": "1"}
        assert val["L"][1]["M"]["order"] == {"N": "2"}

        assert val["L"][0]["M"]["id"] == {"S": "aaceeace-0cb7-46df-89d9-ca8cd3cbc843"}
        assert val["L"][1]["M"]["id"] == {"S": "a66cafc4-eee0-403e-bdcb-46d4c079f6ac"}

    def test_reorder_identical_endpoints_detects_no_changes(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        endpoint_clone = base_endpoint.model_copy()
        org_with_endpoints = base_organisation.model_copy(
            update={"endpoints": [base_endpoint, endpoint_clone]}
        )
        modified = org_with_endpoints.model_copy(
            update={"endpoints": [endpoint_clone, base_endpoint]}
        )
        diff = get_organisation_diff(org_with_endpoints, modified)
        result = deepdiff_to_dynamodb_expressions(diff)
        assert result.is_empty()

    def test_swap_different_endpoints_detects_changes(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        endpoint2 = base_endpoint.model_copy(
            update={
                "id": UUID("55555555-5555-5555-5555-555555555555"),
                "order": 2,
            }
        )
        org_with_endpoints = base_organisation.model_copy(
            update={"endpoints": [base_endpoint, endpoint2]}
        )
        modified = org_with_endpoints.model_copy(
            update={"endpoints": [endpoint2, base_endpoint]}
        )
        diff = get_organisation_diff(org_with_endpoints, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.is_empty()

    def test_all_endpoint_status_values(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        org_with_endpoint = base_organisation.model_copy(
            update={"endpoints": [base_endpoint]}
        )

        for status in EndpointStatus:
            modified_endpoint = base_endpoint.model_copy(update={"status": status})
            modified = base_organisation.model_copy(
                update={"endpoints": [modified_endpoint]}
            )
            diff = get_organisation_diff(org_with_endpoint, modified)
            result = deepdiff_to_dynamodb_expressions(diff)

            if status != EndpointStatus.ACTIVE:
                assert ":val_0" in result.expression_attribute_values
                actual_value = result.expression_attribute_values[":val_0"]["S"]
                assert actual_value == status.value

    def test_zero_order_value(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        endpoint_with_zero_order = base_endpoint.model_copy(update={"order": 0})
        org_with_endpoint = base_organisation.model_copy(
            update={"endpoints": [endpoint_with_zero_order]}
        )
        modified_endpoint = endpoint_with_zero_order.model_copy(update={"order": 1})
        modified = org_with_endpoint.model_copy(
            update={"endpoints": [modified_endpoint]}
        )

        diff = get_organisation_diff(org_with_endpoint, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.update_expression == "SET #endpoints[0].#attr_order = :val_0"
        assert result.expression_attribute_values == {":val_0": {"N": "1"}}
