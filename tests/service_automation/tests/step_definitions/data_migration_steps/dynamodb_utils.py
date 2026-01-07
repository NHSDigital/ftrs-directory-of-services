"""Utility functions for DynamoDB operations in data migration tests."""

import json
from datetime import datetime
from decimal import Decimal
from pprint import pprint
from typing import Any, Dict

from deepdiff import DeepDiff

from utilities.common.dynamoDB_tables import get_table_name


# Constants for field handling
META_TIME_FIELDS = ["createdDateTime", "modifiedDateTime"]
NESTED_PATHS_WITH_META_FIELDS = ["endpoints"]

IGNORED_PATHS = [
    "field",
    *META_TIME_FIELDS,
    *[
        f"root['{nested}'][\\d+]['{field}']"
        for nested in NESTED_PATHS_WITH_META_FIELDS
        for field in META_TIME_FIELDS
    ],
]


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def get_by_id(
    dynamodb: Dict[str, Any],
    table_name: str,
    service_id: str,
) -> Dict[str, Any]:
    """
    Retrieve a DynamoDB item by ID.

    Args:
        dynamodb: DynamoDB client/resource dict
        table_name: Name of the table
        service_id: ID of the service

    Returns:
        The retrieved item

    Raises:
        AssertionError: If item not found
    """
    dynamodb_resource = dynamodb["resource"]
    target_table = dynamodb_resource.Table(get_table_name(table_name))
    response = target_table.get_item(Key={"id": service_id, "field": "document"})

    assert "Item" in response, f"No item found under {service_id}"
    return response["Item"]


def get_by_id_and_sort_key(
    dynamodb: Dict[str, Any],
    table_name: str,
    id_value: str,
    field_sort_key_value: str = "document",
) -> Dict[str, Any]:
    """
    Retrieve a DynamoDB item by ID and sort key.

    Args:
        dynamodb: DynamoDB client/resource dict
        table_name: Name of the table
        id_value: Primary key value
        field_sort_key_value: Sort key value (default: "document")

    Returns:
        The retrieved item

    Raises:
        AssertionError: If item not found
    """
    dynamodb_resource = dynamodb["resource"]
    target_table = dynamodb_resource.Table(get_table_name(table_name))
    response = target_table.get_item(
        Key={"id": id_value, "field": field_sort_key_value}
    )

    assert "Item" in response, (
        f"No item found under id: {id_value}, field sort key: {field_sort_key_value}"
    )
    return response["Item"]


def validate_diff(expected: Dict[str, Any], retrieved_item: Dict[str, Any]) -> None:
    """
    Validate that expected and retrieved items match.

    Args:
        expected: Expected item structure
        retrieved_item: Retrieved item from DynamoDB

    Raises:
        AssertionError: If differences found
    """
    diff = DeepDiff(
        expected, retrieved_item, ignore_order=True, exclude_regex_paths=IGNORED_PATHS
    )

    assert diff == {}, f"Differences found: {pprint(diff, indent=2)}"


def validate_dynamic_fields(retrieved_item: Dict[str, Any]) -> None:
    """
    Validate dynamic timestamp fields in retrieved item.

    Args:
        retrieved_item: Item retrieved from DynamoDB

    Raises:
        AssertionError: If timestamp fields invalid
    """

    def validate_metas(obj: Dict[str, Any], root_path: str = "$") -> None:
        for field in META_TIME_FIELDS:
            assert field in obj, f"Expected field '{field}' not found in item"
            validate_timestamp_format(f"{root_path}.{field}", obj[field])

        relevant_fields = {
            k: v for k, v in obj.items() if k in NESTED_PATHS_WITH_META_FIELDS
        }
        for key, value in relevant_fields.items():
            if isinstance(value, dict):
                validate_metas(value, f"{root_path}.{key}")
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        validate_metas(item, f"{root_path}.{key}[{i}]")

    validate_metas(retrieved_item)


def validate_timestamp_format(path_to_field: str, date_text: str) -> None:
    """
    Validate that a timestamp field has valid ISO format.

    Args:
        path_to_field: Path to the field in the object
        date_text: Timestamp text to validate

    Raises:
        AssertionError: If timestamp format invalid
    """
    try:
        datetime.fromisoformat(date_text)
    except ValueError:
        assert False, (
            f"Text under {path_to_field}: {date_text} not recognised as valid datetime"
        )
