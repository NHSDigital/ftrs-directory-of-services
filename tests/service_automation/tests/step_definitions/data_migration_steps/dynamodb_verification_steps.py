"""BDD steps for verifying DynamoDB table content."""

import json
from typing import Any, Dict

from common.uuid_utils import generate_uuid
from pytest_bdd import parsers, then

from step_definitions.data_migration_steps.dynamodb_utils import (
    DecimalEncoder,
    get_by_id_and_sort_key,
    validate_diff,
    validate_dynamic_fields,
)
from utilities.common.dynamoDB_tables import get_table_name


@then(
    parsers.parse(
        "there is {org_count_expected:d} organisation, {location_count_expected:d} location and {healthcare_service_count_expected:d} healthcare services created"
    )
)
def check_expected_table_counts(
    org_count_expected: int,
    location_count_expected: int,
    healthcare_service_count_expected: int,
    dynamodb: Dict[str, Any],
) -> None:
    """
    Verify expected counts of organisations, locations, and healthcare services.

    Performs a complete table scan - consider a different option for large tables.
    """
    dynamodb_resource = dynamodb["resource"]

    def check_table(table_name: str, count_expected: int) -> None:
        table = dynamodb_resource.Table(table_name)
        table_scan = table.scan()
        actual_count = len(table_scan["Items"])
        assert count_expected == actual_count, (
            f"Expected {table_name} count does not match actual"
        )

    check_table(get_table_name("organisation"), org_count_expected)
    check_table(get_table_name("location"), location_count_expected)
    check_table(get_table_name("healthcare-service"), healthcare_service_count_expected)


@then(parsers.parse("The '{table_name}' for service ID '{service_id}' has content:"))
def check_table_content_by_id(
    table_name: str,
    service_id: str,
    docstring: str,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify table content for a service by generated UUID."""
    namespace = table_name.replace("-", "_")
    generated_uuid = str(generate_uuid(service_id, namespace))
    _check_by_id_and_sort_key(table_name, generated_uuid, docstring, dynamodb)


@then(
    parsers.re(
        r"field '(?P<field_name>[\w-]*)' on table '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' has content:"
    )
)
def check_field_on_a_table_by_id(
    field_name: str,
    table_name: str,
    primary_id: str,
    docstring: str,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify specific field content on a table by ID."""
    _check_by_id_and_sort_key(
        table_name, primary_id, docstring, dynamodb, filtered_by_field=field_name
    )


@then(
    parsers.re(
        r"field '(?P<field_name>[\w-]*)' on table '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' and field sort key '(?P<field_sort_key>[\w-]+)' has content:"
    )
)
def check_field_on_a_table_by_id_and_sort_key(
    field_name: str,
    table_name: str,
    primary_id: str,
    docstring: str,
    dynamodb: Dict[str, Any],
    field_sort_key: str,
) -> None:
    """Verify specific field content on a table by ID and sort key."""
    _check_by_id_and_sort_key(
        table_name,
        primary_id,
        docstring,
        dynamodb,
        field_sort_key=field_sort_key,
        filtered_by_field=field_name,
    )


@then(
    parsers.re(
        r"the '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' has content:"
    )
)
def check_row_on_table_by_id(
    table_name: str,
    primary_id: str,
    docstring: str,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify complete row content on a table by ID."""
    _check_by_id_and_sort_key(table_name, primary_id, docstring, dynamodb)


@then(
    parsers.re(
        r"the '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' and field sort key '(?P<field_sort_key>[\w-]+)' has content:"
    )
)
def check_row_on_table_by_id_and_sort_key(
    table_name: str,
    primary_id: str,
    docstring: str,
    field_sort_key: str,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify complete row content on a table by ID and sort key."""
    _check_by_id_and_sort_key(
        table_name, primary_id, docstring, dynamodb, field_sort_key
    )


@then(
    parsers.re(
        r"field '(?P<field_name>[\w-]*)' on table '(?P<table_name>[\w-]*)' for id '(?P<primary_id>[\w-]+)' should have cleaned coordinates"
    )
)
def check_field_has_cleaned_coordinates(
    field_name: str,
    table_name: str,
    primary_id: str,
    dynamodb: Dict[str, Any],
) -> None:
    """Verify that position GCS coordinates have been cleaned/normalized."""
    retrieved_item = get_by_id_and_sort_key(
        dynamodb, table_name, primary_id, field_sort_key_value="document"
    )

    position_gcs = retrieved_item.get(field_name)
    assert position_gcs is not None, (
        f"Field '{field_name}' not found in item {primary_id}"
    )

    # Verify latitude and longitude exist and are properly formatted
    assert "latitude" in position_gcs, "latitude not found in positionGCS"
    assert "longitude" in position_gcs, "longitude not found in positionGCS"

    # Verify they are numeric strings (Decimal stored as strings in DynamoDB)
    latitude = str(position_gcs["latitude"])
    longitude = str(position_gcs["longitude"])

    # Basic validation - should be parseable as float
    try:
        float(latitude)
        float(longitude)
    except ValueError:
        assert False, (
            f"Coordinates are not valid numbers: lat={latitude}, lon={longitude}"
        )


def _check_by_id_and_sort_key(
    table_name: str,
    primary_id: str,
    docstring: str,
    dynamodb: Dict[str, Any],
    field_sort_key: str = "document",
    filtered_by_field: str | None = None,
) -> None:
    """
    Internal helper to check DynamoDB content by ID and sort key.

    Args:
        table_name: Name of the DynamoDB table
        primary_id: Primary key value
        docstring: Expected JSON content
        dynamodb: DynamoDB client/resource dict
        field_sort_key: Sort key value (default: "document")
        filtered_by_field: Optional field name to filter the comparison
    """
    retrieved_item = json.loads(
        json.dumps(
            get_by_id_and_sort_key(
                dynamodb, table_name, primary_id, field_sort_key_value=field_sort_key
            ),
            cls=DecimalEncoder,
        )
    )
    expected = json.loads(docstring)
    actual = (
        {k: v for k, v in retrieved_item.items() if k == filtered_by_field}
        if filtered_by_field
        else retrieved_item
    )
    validate_diff(expected, actual)

    if not filtered_by_field:
        validate_dynamic_fields(actual)
