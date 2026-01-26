"""Tests for basic DeepDiffToDynamoDBConverter functionality."""

from ftrs_data_layer.domain import Organisation

from common.diff_utils import (
    DeepDiffToDynamoDBConverter,
    DynamoDBUpdateExpressions,
    deepdiff_to_dynamodb_expressions,
    get_organisation_diff,
)


class TestDeepDiffToDynamoDBConverterBasics:
    def test_empty_diff_returns_empty_expressions(
        self,
        base_organisation: Organisation,
    ) -> None:
        diff = get_organisation_diff(base_organisation, base_organisation)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert result.is_empty()
        assert result.update_expression == ""
        assert result.expression_attribute_names == {}
        assert result.expression_attribute_values == {}

    def test_converter_returns_dynamodb_update_expressions(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"name": "New Name"})
        diff = get_organisation_diff(base_organisation, modified)
        result = deepdiff_to_dynamodb_expressions(diff)

        assert isinstance(result, DynamoDBUpdateExpressions)

    def test_convenience_function_works(
        self,
        base_organisation: Organisation,
    ) -> None:
        modified = base_organisation.model_copy(update={"name": "New Name"})
        diff = get_organisation_diff(base_organisation, modified)

        func_result = deepdiff_to_dynamodb_expressions(diff)
        class_result = DeepDiffToDynamoDBConverter(diff).convert()

        assert func_result.update_expression == class_result.update_expression
