"""Tests for edge cases, null handling, overlapping paths and REMOVE expressions."""

from uuid import UUID

from deepdiff import DeepDiff
from ftrs_data_layer.domain import (
    HealthcareService,
    Location,
    Organisation,
)
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import TelecomType
from ftrs_data_layer.domain.telecom import Telecom

from common.diff_utils import (
    DeepDiffToDynamoDBConverter,
    deepdiff_to_dynamodb_expressions,
    get_healthcare_service_diff,
    get_location_diff,
    get_organisation_diff,
)


class TestOverlappingPathHandling:
    """Tests for handling overlapping paths when list items are added/removed."""

    def test_add_endpoint_while_modifying_existing_endpoint(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        """When adding a new endpoint and modifying an existing one, should replace entire list."""
        org_with_endpoint = base_organisation.model_copy(
            update={"endpoints": [base_endpoint]}
        )
        modified_endpoint = base_endpoint.model_copy(
            update={"address": "https://modified.endpoint.com"}
        )
        new_endpoint = base_endpoint.model_copy(
            update={
                "id": UUID("55555555-5555-5555-5555-555555555555"),
                "order": 2,
            }
        )
        modified = org_with_endpoint.model_copy(
            update={"endpoints": [modified_endpoint, new_endpoint]}
        )
        diff = get_organisation_diff(org_with_endpoint, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should replace the entire endpoints list, not update individual fields
        assert result.update_expression == "SET #endpoints = :val_0"
        assert result.expression_attribute_names == {"#endpoints": "endpoints"}

        # The value should be the complete list
        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 2  # noqa: PLR2004

    def test_remove_endpoint_while_modifying_existing_endpoint(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        """When removing an endpoint and modifying another, should replace entire list."""
        endpoint2 = base_endpoint.model_copy(
            update={
                "id": UUID("55555555-5555-5555-5555-555555555555"),
                "order": 2,
            }
        )
        org_with_endpoints = base_organisation.model_copy(
            update={"endpoints": [base_endpoint, endpoint2]}
        )
        modified_endpoint = base_endpoint.model_copy(
            update={"address": "https://modified.endpoint.com"}
        )
        modified = org_with_endpoints.model_copy(
            update={"endpoints": [modified_endpoint]}
        )
        diff = get_organisation_diff(org_with_endpoints, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should replace the entire endpoints list
        assert result.update_expression == "SET #endpoints = :val_0"
        assert result.expression_attribute_names == {"#endpoints": "endpoints"}

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 1

    def test_add_telecom_while_modifying_existing_telecom(
        self,
        base_organisation: Organisation,
    ) -> None:
        """When adding and modifying telecoms simultaneously, should replace entire list."""
        existing_telecom = Telecom(
            type=TelecomType.PHONE, value="0300 311 22 33", isPublic=True
        )
        org_with_telecom = base_organisation.model_copy(
            update={"telecom": [existing_telecom]}
        )
        modified_telecom = existing_telecom.model_copy(
            update={"value": "0300 999 88 77"}
        )
        new_telecom = Telecom(
            type=TelecomType.EMAIL, value="test@nhs.net", isPublic=True
        )
        modified = org_with_telecom.model_copy(
            update={"telecom": [modified_telecom, new_telecom]}
        )
        diff = get_organisation_diff(org_with_telecom, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should replace the entire telecom list
        assert result.update_expression == "SET #telecom = :val_0"
        assert result.expression_attribute_names == {"#telecom": "telecom"}

        val = result.expression_attribute_values[":val_0"]
        assert "L" in val
        assert len(val["L"]) == 2  # noqa: PLR2004


class TestNullValueHandling:
    """Tests for setting fields to null values."""

    def test_set_telecom_field_to_none(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        """Setting a telecom field from a value to None should use SET with NULL."""
        new_telecom = base_healthcare_service.telecom.model_copy(update={"web": None})
        modified = base_healthcare_service.model_copy(update={"telecom": new_telecom})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert "#telecom" in result.expression_attribute_names
        assert "#web" in result.expression_attribute_names
        # The value should be NULL type
        values_list = list(result.expression_attribute_values.values())
        assert {"NULL": True} in values_list

    def test_set_multiple_telecom_fields_to_none(
        self,
        base_healthcare_service: HealthcareService,
    ) -> None:
        """Setting multiple telecom fields to None."""
        new_telecom = base_healthcare_service.telecom.model_copy(
            update={"web": None, "email": None}
        )
        modified = base_healthcare_service.model_copy(update={"telecom": new_telecom})
        diff = get_healthcare_service_diff(base_healthcare_service, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        # Should have two NULL values
        null_count = sum(
            1
            for v in result.expression_attribute_values.values()
            if v == {"NULL": True}
        )
        assert null_count == 2  # noqa: PLR2004


class TestRemoveExpressions:
    """Tests for REMOVE expressions when dictionary items are removed."""

    def test_remove_optional_field_from_location(
        self,
        base_location: Location,
    ) -> None:
        """When a field changes from a value to None, it should use SET with NULL."""
        modified = base_location.model_copy(update={"name": None})
        diff = get_location_diff(base_location, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        # The current implementation uses SET with NULL for type changes to None
        assert "SET" in result.update_expression
        assert "name" in result.expression_attribute_names.values()

    def test_remove_field_generates_remove_expression(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        """When a field is deleted from a dict, should generate REMOVE."""
        # Create a raw diff with dictionary_item_removed
        old_dict = {"name": "Test", "extra_field": "value"}
        new_dict = {"name": "Test"}
        diff = DeepDiff(old_dict, new_dict, view="tree")
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "REMOVE" in result.update_expression
        assert "#extra_field" in result.expression_attribute_names

    def test_add_field_generates_set_expression(
        self,
        base_organisation: Organisation,
    ) -> None:
        """When a new field is added to a dict, should generate SET."""
        # Create a raw diff with dictionary_item_added
        old_dict = {"name": "Test"}
        new_dict = {"name": "Test", "new_field": "new_value"}
        diff = DeepDiff(old_dict, new_dict, view="tree")
        result = deepdiff_to_dynamodb_expressions(diff)

        assert "SET" in result.update_expression
        assert "#new_field" in result.expression_attribute_names
        values_list = list(result.expression_attribute_values.values())
        assert {"S": "new_value"} in values_list


class TestEdgeCases:
    """Tests for edge cases and less common code paths."""

    def test_empty_path_returns_empty_string(self) -> None:
        """When path is just 'root', should return empty string."""
        converter = DeepDiffToDynamoDBConverter(DeepDiff({}, {}, view="tree"))
        result = converter._to_dynamodb_path("root")
        assert result == ""

    def test_path_starting_with_array_index(self) -> None:
        """When path starts with array index (unusual but possible)."""
        converter = DeepDiffToDynamoDBConverter(DeepDiff({}, {}, view="tree"))
        result = converter._to_dynamodb_path("root[0]")
        assert result == "[0]"

    def test_single_quoted_string_keys_in_path(self) -> None:
        """DeepDiff uses single quotes for string keys."""
        converter = DeepDiffToDynamoDBConverter(DeepDiff({}, {}, view="tree"))
        parts = converter._parse_path_components("['field_name']")
        assert parts == ["field_name"]

    def test_remove_clause_skipped_when_inside_replaced_list(
        self,
        base_organisation: Organisation,
        base_endpoint: Endpoint,
    ) -> None:
        """When removing an item from a list that's being replaced, skip individual removes."""
        # Create scenario: remove an endpoint while also removing a field from another endpoint
        endpoint1 = base_endpoint.model_copy()
        endpoint2 = base_endpoint.model_copy(
            update={
                "id": UUID("55555555-5555-5555-5555-555555555555"),
                "order": 2,
            }
        )
        org_with_endpoints = base_organisation.model_copy(
            update={"endpoints": [endpoint1, endpoint2]}
        )
        # Remove endpoint2 entirely (list structure change)
        modified = org_with_endpoints.model_copy(update={"endpoints": [endpoint1]})
        diff = get_organisation_diff(org_with_endpoints, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should only have SET for replacing the entire list, not individual REMOVE
        assert "SET" in result.update_expression
        # Should not have individual field removes since list is being replaced
        assert result.update_expression.count("REMOVE") == 0

    def test_multiple_items_added_to_list_single_set(self) -> None:
        """When multiple items are added to a list, should only generate one SET."""
        old_dict = {"items": [1, 2]}
        new_dict = {"items": [1, 2, 3, 4]}  # Adding multiple items
        diff = DeepDiff(old_dict, new_dict, view="tree")
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should only have one SET clause for items, not multiple
        assert result.update_expression.count("#items") == 1
        assert "SET #items = :val_0" == result.update_expression

    def test_iterable_item_removed_processed_correctly(self) -> None:
        """Test that iterable_item_removed is processed correctly."""
        old_dict = {"items": [1, 2, 3]}
        new_dict = {"items": [1]}  # Remove items
        diff = DeepDiff(old_dict, new_dict, view="tree")
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should replace entire list
        assert "SET #items = :val_0" == result.update_expression
        val = result.expression_attribute_values[":val_0"]
        assert val == {"L": [{"N": "1"}]}

    def test_both_add_and_remove_from_same_list(self) -> None:
        """Adding and removing from the same list should result in single SET."""
        old_dict = {"items": [1, 2, 3]}
        new_dict = {"items": [2, 4]}  # Remove 1 and 3, add 4
        diff = DeepDiff(old_dict, new_dict, view="tree")
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should replace entire list with a single SET
        assert result.update_expression == "SET #items = :val_0"
        val = result.expression_attribute_values[":val_0"]
        assert val == {"L": [{"N": "2"}, {"N": "4"}]}

    def test_add_remove_clause_skips_nested_path(self) -> None:
        """Test _add_remove_clause skips paths nested inside replaced lists."""
        converter = DeepDiffToDynamoDBConverter(DeepDiff({}, {}, view="tree"))
        # Mark a list path as replaced
        converter._replaced_list_paths.add("#items")
        # Try to add a remove clause for nested path
        converter._add_remove_clause("root['items'][0]['field']")
        # Should not add to remove clauses since it's inside replaced list
        assert len(converter._remove_clauses) == 0

    def test_list_size_change_replaces_entire_list(self) -> None:
        """When list size changes, the entire list should be replaced."""
        old_dict = {"items": [1, 2, 3]}
        new_dict = {"items": [4, 5]}  # Different size and values
        diff = DeepDiff(old_dict, new_dict, view="tree")
        result = deepdiff_to_dynamodb_expressions(diff)

        # Should only have one SET clause total
        assert result.update_expression == "SET #items = :val_0"
        # Verify the new list is correct
        val = result.expression_attribute_values[":val_0"]
        assert val == {"L": [{"N": "4"}, {"N": "5"}]}

    def test_parse_path_skips_non_bracket_characters(self) -> None:
        """Path parser should skip non-bracket characters at start."""
        converter = DeepDiffToDynamoDBConverter(DeepDiff({}, {}, view="tree"))
        # Paths can have leading characters before the first bracket
        parts = converter._parse_path_components("abc['field']")
        assert parts == ["field"]

    def test_parse_path_with_numeric_index(self) -> None:
        """Path parser should handle numeric indices."""
        converter = DeepDiffToDynamoDBConverter(DeepDiff({}, {}, view="tree"))
        parts = converter._parse_path_components("['items'][0]")
        assert parts == ["items", 0]

    def test_only_iterable_item_added_no_removed(self) -> None:
        """When only items are added (no removal), should still work correctly."""
        old_dict = {"items": [1]}
        new_dict = {"items": [1, 2]}  # Only adding, no removal
        diff = DeepDiff(old_dict, new_dict, view="tree")
        # Verify that iterable_item_removed is not in diff
        assert "iterable_item_removed" not in diff
        assert "iterable_item_added" in diff

        result = deepdiff_to_dynamodb_expressions(diff)
        assert "SET #items = :val_0" == result.update_expression

    def test_only_iterable_item_removed_no_added(self) -> None:
        """When only items are removed (no addition), should still work correctly."""
        old_dict = {"items": [1, 2]}
        new_dict = {"items": [1]}  # Only removing, no addition
        diff = DeepDiff(old_dict, new_dict, view="tree")
        # Verify that iterable_item_added is not in diff
        assert "iterable_item_added" not in diff
        assert "iterable_item_removed" in diff

        result = deepdiff_to_dynamodb_expressions(diff)
        assert "SET #items = :val_0" == result.update_expression

    def test_no_iterable_changes_only_value_changes(self) -> None:
        """When there are no list changes, only value changes."""
        old_dict = {"name": "old", "items": [1, 2]}
        new_dict = {"name": "new", "items": [1, 2]}  # Only name changes, list is same
        diff = DeepDiff(old_dict, new_dict, view="tree")
        # Verify no iterable changes
        assert "iterable_item_added" not in diff
        assert "iterable_item_removed" not in diff
        assert "values_changed" in diff

        result = deepdiff_to_dynamodb_expressions(diff)
        assert "SET #attr_name = :val_0" == result.update_expression
