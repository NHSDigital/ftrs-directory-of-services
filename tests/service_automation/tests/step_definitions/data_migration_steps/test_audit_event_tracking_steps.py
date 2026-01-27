"""
Step definitions for audit event tracking in data migration.
Tests for createdBy, lastUpdatedBy, createdTime, and lastUpdated fields.
"""
from datetime import datetime
from typing import Any, Dict

import pytest
from pytest_bdd import given, parsers, scenarios, then

from step_definitions.common_steps.data_steps import *  # noqa: F403
from step_definitions.common_steps.data_migration_steps import *  # noqa: F403
from step_definitions.data_migration_steps.dos_data_manipulation_steps import *  # noqa: F403
from utilities.common.dynamoDB_tables import get_table_name


# Load all scenarios from the feature file
scenarios("../../tests/features/data_migration_features/audit_event_tracking.feature")


# Storage for audit timestamps across test steps
stored_audit_values: Dict[str, Any] = {}


def get_entity_record(dynamodb: Dict[str, Any], entity_type: str, service_id: str) -> Dict[str, Any]:
    """
    Retrieve entity record from DynamoDB based on entity type and service ID.

    Args:
        dynamodb: DynamoDB client and resource dictionary
        entity_type: Type of entity (organisation, location, healthcare-service)
        service_id: Service ID to lookup

    Returns:
        Entity record from DynamoDB
    """
    from uuid import UUID, uuid5

    dynamodb_resource = dynamodb["resource"]

    # Map entity type to UUID namespace (healthcare-service uses underscore in UUID namespace)
    uuid_namespace_map = {
        "organisation": "organisation",
        "location": "location",
        "healthcare-service": "healthcare_service",
    }
    uuid_namespace = uuid_namespace_map.get(entity_type, entity_type)

    # Build deterministic UUID from service_id using migration UUID namespace
    migration_uuid_ns = UUID("fa3aaa15-9f83-4f4a-8f86-fd1315248bcb")
    entity_uuid = str(uuid5(migration_uuid_ns, f"{uuid_namespace}-{service_id}"))

    # Get entity record directly
    table_name = get_table_name(entity_type)
    entity_table = dynamodb_resource.Table(table_name)
    entity_response = entity_table.get_item(Key={"id": entity_uuid, "field": "document"})
    assert "Item" in entity_response, f"{entity_type} not found for service ID {service_id}"

    return entity_response["Item"]


def get_endpoint_records(dynamodb: Dict[str, Any], service_id: str) -> list[Dict[str, Any]]:
    """
    Retrieve all endpoint records for a service.

    Args:
        dynamodb: DynamoDB client and resource dictionary
        service_id: Service ID to lookup

    Returns:
        List of endpoint records
    """
    dynamodb_resource = dynamodb["resource"]

    # Get organisation first to find endpoint IDs
    org_record = get_entity_record(dynamodb, "organisation", service_id)
    endpoint_ids = org_record.get("endpoints", [])

    if not endpoint_ids:
        return []

    endpoint_table = dynamodb_resource.Table(get_table_name("endpoint"))
    endpoints = []

    for endpoint_id in endpoint_ids:
        response = endpoint_table.get_item(Key={"id": endpoint_id, "field": "document"})
        if "Item" in response:
            endpoints.append(response["Item"])

    return endpoints


def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """
    Get nested value from dictionary using dot notation.

    Args:
        obj: Dictionary to extract value from
        path: Dot-separated path (e.g., "createdBy.type")

    Returns:
        Value at the specified path
    """
    keys = path.split(".")
    value = obj
    for key in keys:
        if not isinstance(value, dict):
            pytest.fail(f"Expected dict at path segment '{key}', got {type(value)}")
        if key not in value:
            pytest.fail(f"Key '{key}' not found in path '{path}'")
        value = value[key]
    return value


# === GIVEN steps for storing audit values ===

@given(parsers.parse("I store the {entity_type} audit timestamps for service '{service_id}'"))
def store_audit_timestamps(
    entity_type: str, service_id: str, dynamodb: Dict[str, Any]
) -> None:
    """
    Store audit timestamps and createdBy/lastUpdatedBy for later comparison.

    Args:
        entity_type: Type of entity (organisation, location, healthcare service, endpoint)
        service_id: Service ID
        dynamodb: DynamoDB fixture
    """
    entity_type_normalized = entity_type.replace(" ", "-")

    if entity_type_normalized == "endpoint":
        endpoints = get_endpoint_records(dynamodb, service_id)
        stored_audit_values[f"{entity_type}_{service_id}"] = [
            {
                "createdTime": endpoint.get("createdTime"),
                "createdBy": endpoint.get("createdBy"),
                "lastUpdated": endpoint.get("lastUpdated"),
                "lastUpdatedBy": endpoint.get("lastUpdatedBy"),
            }
            for endpoint in endpoints
        ]
    else:
        record = get_entity_record(dynamodb, entity_type_normalized, service_id)
        stored_audit_values[f"{entity_type}_{service_id}"] = {
            "createdTime": record.get("createdTime"),
            "createdBy": record.get("createdBy"),
            "lastUpdated": record.get("lastUpdated"),
            "lastUpdatedBy": record.get("lastUpdatedBy"),
        }


# === THEN steps for checking audit field values ===

@then(parsers.parse('the {entity_type} record has "{field}" populated'))
def check_entity_field_populated(
    entity_type: str, field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field is populated (not None, not empty).

    Args:
        entity_type: Type of entity (organisation, location, healthcare service)
        field: Field name to check
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    entity_type_normalized = entity_type.replace(" ", "-")
    # Get service_id from either sqs_service_id or service_id
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    record = get_entity_record(dynamodb, entity_type_normalized, service_id)

    value = record.get(field)
    assert value is not None, f"Field '{field}' is None for {entity_type}"
    assert value != "", f"Field '{field}' is empty for {entity_type}"


@then(parsers.parse('the {entity_type} record for healthcare service has "{field}" populated'))
def check_organisation_field_populated_by_hs(
    entity_type: str, field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field is populated for organisation via healthcare service lookup.

    Args:
        entity_type: Type of entity (should be organisation)
        field: Field name to check
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    check_entity_field_populated(entity_type, field, migration_context, dynamodb)


@then(parsers.parse('the {entity_type} "{field_path}" is "{expected_value}"'))
def check_entity_field_value(
    entity_type: str, field_path: str, expected_value: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field (including nested) has the expected value.

    Args:
        entity_type: Type of entity (organisation, location, healthcare service)
        field_path: Field path (can use dot notation like "createdBy.type")
        expected_value: Expected value
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    entity_type_normalized = entity_type.replace(" ", "-")
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    record = get_entity_record(dynamodb, entity_type_normalized, service_id)

    actual_value = get_nested_value(record, field_path)
    assert actual_value == expected_value, (
        f"Field '{field_path}' mismatch for {entity_type}: "
        f"expected '{expected_value}', got '{actual_value}'"
    )


@then(parsers.parse('the {entity_type} "{field1}" equals "{field2}"'))
def check_entity_fields_equal(
    entity_type: str, field1: str, field2: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that two fields have the same value.

    Args:
        entity_type: Type of entity (organisation, location, healthcare service)
        field1: First field name
        field2: Second field name
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    entity_type_normalized = entity_type.replace(" ", "-")
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    record = get_entity_record(dynamodb, entity_type_normalized, service_id)

    value1 = record.get(field1)
    value2 = record.get(field2)

    assert value1 == value2, (
        f"Fields '{field1}' and '{field2}' should be equal for {entity_type}: "
        f"'{field1}'={value1}, '{field2}'={value2}"
    )


@then(parsers.parse('the {entity_type} "{field}" is unchanged from stored value'))
def check_entity_field_unchanged(
    entity_type: str, field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field value hasn't changed from the stored value.

    Args:
        entity_type: Type of entity (organisation, location, healthcare service)
        field: Field name to check
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    entity_type_normalized = entity_type.replace(" ", "-")
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])

    storage_key = f"{entity_type}_{service_id}"
    assert storage_key in stored_audit_values, f"No stored values for {storage_key}"

    stored_value = stored_audit_values[storage_key].get(field)
    assert stored_value is not None, f"Field '{field}' not found in stored values"

    record = get_entity_record(dynamodb, entity_type_normalized, service_id)
    current_value = record.get(field)

    assert current_value == stored_value, (
        f"Field '{field}' has changed for {entity_type}: "
        f"stored={stored_value}, current={current_value}"
    )


@then(parsers.parse('the {entity_type} "{field}" is greater than stored "{stored_field}"'))
def check_entity_field_greater_than_stored(
    entity_type: str, field: str, stored_field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a timestamp field is greater than a stored timestamp.

    Args:
        entity_type: Type of entity (organisation, location, healthcare service)
        field: Field name to check (current value)
        stored_field: Stored field name to compare against
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    entity_type_normalized = entity_type.replace(" ", "-")
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])

    storage_key = f"{entity_type}_{service_id}"
    assert storage_key in stored_audit_values, f"No stored values for {storage_key}"

    stored_value = stored_audit_values[storage_key].get(stored_field)
    assert stored_value is not None, f"Field '{stored_field}' not found in stored values"

    record = get_entity_record(dynamodb, entity_type_normalized, service_id)
    current_value = record.get(field)

    # Parse timestamps
    stored_time = datetime.fromisoformat(stored_value.replace("Z", "+00:00"))
    current_time = datetime.fromisoformat(current_value.replace("Z", "+00:00"))

    assert current_time > stored_time, (
        f"Field '{field}' should be greater than stored '{stored_field}' for {entity_type}: "
        f"stored={stored_value}, current={current_value}"
    )


# === THEN steps for checking endpoint audit fields ===

@then(parsers.parse('the endpoint records have "{field}" populated'))
def check_endpoint_field_populated(
    field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field is populated in all endpoint records.

    Args:
        field: Field name to check
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    endpoints = get_endpoint_records(dynamodb, service_id)

    assert len(endpoints) > 0, f"No endpoints found for service {service_id}"

    for i, endpoint in enumerate(endpoints):
        value = endpoint.get(field)
        assert value is not None, f"Field '{field}' is None for endpoint {i}"
        assert value != "", f"Field '{field}' is empty for endpoint {i}"


@then(parsers.parse('all endpoints "{field_path}" is "{expected_value}"'))
def check_all_endpoints_field_value(
    field_path: str, expected_value: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field has the expected value in all endpoint records.

    Args:
        field_path: Field path (can use dot notation)
        expected_value: Expected value
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    endpoints = get_endpoint_records(dynamodb, service_id)

    assert len(endpoints) > 0, f"No endpoints found for service {service_id}"

    for i, endpoint in enumerate(endpoints):
        actual_value = get_nested_value(endpoint, field_path)
        assert actual_value == expected_value, (
            f"Field '{field_path}' mismatch for endpoint {i}: "
            f"expected '{expected_value}', got '{actual_value}'"
        )


@then(parsers.parse('all endpoints "{field1}" equals "{field2}"'))
def check_all_endpoints_fields_equal(
    field1: str, field2: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that two fields have the same value in all endpoint records.

    Args:
        field1: First field name
        field2: Second field name
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    endpoints = get_endpoint_records(dynamodb, service_id)

    assert len(endpoints) > 0, f"No endpoints found for service {service_id}"

    for i, endpoint in enumerate(endpoints):
        value1 = endpoint.get(field1)
        value2 = endpoint.get(field2)

        assert value1 == value2, (
            f"Fields '{field1}' and '{field2}' should be equal for endpoint {i}: "
            f"'{field1}'={value1}, '{field2}'={value2}"
        )


@then(parsers.parse('all endpoints "{field}" is unchanged from stored value'))
def check_all_endpoints_field_unchanged(
    field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a field value hasn't changed from stored values in all endpoints.

    Args:
        field: Field name to check
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    storage_key = f"endpoint_{service_id}"

    assert storage_key in stored_audit_values, f"No stored values for {storage_key}"
    stored_endpoints = stored_audit_values[storage_key]

    current_endpoints = get_endpoint_records(dynamodb, service_id)

    assert len(current_endpoints) == len(stored_endpoints), (
        f"Number of endpoints changed: stored={len(stored_endpoints)}, current={len(current_endpoints)}"
    )

    for i, (stored_endpoint, current_endpoint) in enumerate(zip(stored_endpoints, current_endpoints)):
        stored_value = stored_endpoint.get(field)
        current_value = current_endpoint.get(field)

        assert current_value == stored_value, (
            f"Field '{field}' changed for endpoint {i}: "
            f"stored={stored_value}, current={current_value}"
        )


@then(parsers.parse('all endpoints "{field}" is greater than stored "{stored_field}"'))
def check_all_endpoints_field_greater_than_stored(
    field: str, stored_field: str, migration_context: Dict[str, Any], dynamodb: Dict[str, Any]
) -> None:
    """
    Verify that a timestamp field is greater than stored timestamp in all endpoints.

    Args:
        field: Field name to check (current value)
        stored_field: Stored field name to compare against
        migration_context: Migration context with service_id
        dynamodb: DynamoDB fixture
    """
    service_id = str(migration_context.get("sqs_service_id") or migration_context["service_id"])
    storage_key = f"endpoint_{service_id}"

    assert storage_key in stored_audit_values, f"No stored values for {storage_key}"
    stored_endpoints = stored_audit_values[storage_key]

    current_endpoints = get_endpoint_records(dynamodb, service_id)

    assert len(current_endpoints) == len(stored_endpoints), (
        f"Number of endpoints changed: stored={len(stored_endpoints)}, current={len(current_endpoints)}"
    )

    for i, (stored_endpoint, current_endpoint) in enumerate(zip(stored_endpoints, current_endpoints)):
        stored_value = stored_endpoint.get(stored_field)
        current_value = current_endpoint.get(field)

        # Parse timestamps
        stored_time = datetime.fromisoformat(stored_value.replace("Z", "+00:00"))
        current_time = datetime.fromisoformat(current_value.replace("Z", "+00:00"))

        assert current_time > stored_time, (
            f"Field '{field}' should be greater than stored '{stored_field}' for endpoint {i}: "
            f"stored={stored_value}, current={current_value}"
        )
