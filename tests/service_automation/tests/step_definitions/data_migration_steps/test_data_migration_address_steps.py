from typing import Any, Dict

import pytest
from pytest_bdd import given, parsers, then, when


from step_definitions.common_steps.data_migration_steps import *  # noqa: F403
from common.uuid_utils import generate_uuid
from utilities.common.dynamoDB_tables import get_table_name


@then("the service has the address")
def service_has_address(dynamodb: Dict[str, Any]) -> None:
    """Verify that at least one location record contains an address object.

    Scans the 'location' table and asserts an item exists with an address either
    at the top level or nested under 'document'.
    """
    dynamodb_resource = dynamodb["resource"]
    table = dynamodb_resource.Table(get_table_name('location'))
    scan = table.scan()
    items = scan.get("Items", [])
    assert items, "No items found in 'location' table after migration"

    def extract_address(item: Dict[str, Any]) -> Any:
        if "address" in item:
            return item["address"]
        if "document" in item and isinstance(item["document"], dict) and "address" in item["document"]:
            return item["document"]["address"]
        return None

    for item in items:
        address = extract_address(item)
        if address is not None:
            return

    pytest.fail("No location item with an address field was found")


@then(parsers.parse("the service address for ID '{service_id:d}' should be:"))
def service_address_should_be(service_id: int, datatable: list[list[str]], dynamodb: Dict[str, Any]) -> None:
    """Validate the address for a specific service ID matches expected key/value pairs.
    Uses generate_uuid() to compute the location UUID from the service ID,
    fetches the location record from DynamoDB, and validates address fields.

    Expected datatable format:
    | key    | value |
    Special value 'NULL' asserts the field is either missing or None.
    """
    # Generate the UUID for the location based on the service ID
    location_uuid = str(generate_uuid(service_id, "location"))

    dynamodb_resource = dynamodb["resource"]
    table = dynamodb_resource.Table(get_table_name('location'))

    response = table.get_item(Key={"id": location_uuid, "field": "document"})
    item = response.get("Item")

    assert item is not None, f"Location item with UUID {location_uuid} (generated from service ID {service_id}) not found in 'location' table"

    # Address is always in document.address structure
    assert "document" in item and isinstance(item["document"], dict), f"Location item missing 'document' field for UUID {location_uuid}"
    assert "address" in item["document"], f"Location document missing 'address' field for UUID {location_uuid} (service ID {service_id})"

    address = item["document"]["address"]

    # Build expected mapping from datatable (skip header row)
    expected: Dict[str, Any] = {}
    for i, row in enumerate(datatable):
        # Skip the header row (first row with column names)
        if i == 0:
            continue
        if len(row) != 2:
            pytest.fail(f"Invalid datatable row (expected 2 columns): {row}")
        key, value = row
        expected[key] = value

    for key, expected_value in expected.items():
        # Treat "NULL", "None", or empty string as expecting a null/missing/empty field
        if expected_value in ("NULL", "None", "") or expected_value.strip() == "":
            # Accept missing, None, or empty string
            actual = address.get(key)
            assert actual in (None, ""), (
                f"Address field '{key}' expected to be NULL/empty but has value '{actual}'"
            )
        else:
            assert key in address, f"Expected address field '{key}' missing"
            actual = address[key]
            assert actual == expected_value, (
                f"Mismatch for address field '{key}': expected '{expected_value}' got '{actual}'"
            )


@then(parsers.parse("the location for service ID '{service_id:d}' should have no address"))
def location_should_have_no_address(service_id: int, dynamodb: Dict[str, Any]) -> None:
    """Verify that the location for a specific service ID has no address (address is None).

    This is used for testing scenarios where address is "Not Available" or invalid,
    and should result in formatted_address = None.
    """
    # Generate the UUID for the location based on the service ID
    location_uuid = str(generate_uuid(service_id, "location"))

    dynamodb_resource = dynamodb["resource"]
    table = dynamodb_resource.Table(get_table_name('location'))

    response = table.get_item(Key={"id": location_uuid, "field": "document"})
    item = response.get("Item")

    assert item is not None, f"Location item with UUID {location_uuid} (generated from service ID {service_id}) not found in 'location' table"

    # Address is always in document.address structure
    assert "document" in item and isinstance(item["document"], dict), f"Location item missing 'document' field for UUID {location_uuid}"
    address = item["document"].get("address")

    assert address is None, (
        f"Expected location for service ID {service_id} to have no address (None), "
        f"but found: {address}"
    )


@then(parsers.parse("the service should have a validation error with code '{error_code}'"))
def service_should_have_validation_error(service_id: int, error_code: str, context: Dict[str, Any]) -> None:
    """Verify that a service migration resulted in a validation error with the specified code.

    This checks that the service was not successfully migrated due to validation errors.
    The error should be captured in the migration context metrics.
    """
    metrics = context.get("metrics", {})

    # Service with validation errors should not be migrated
    assert metrics.get("errors", 0) > 0, (
        f"Expected service {service_id} to have validation errors, but errors count is {metrics.get('errors', 0)}"
    )

    # The service should be counted as transformed but not migrated
    assert metrics.get("migrated", 0) == 0, (
        f"Expected service {service_id} not to be migrated due to validation error '{error_code}', "
        f"but migrated count is {metrics.get('migrated', 0)}"
    )
