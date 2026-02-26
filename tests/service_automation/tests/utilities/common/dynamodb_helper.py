"""DynamoDB helper utilities for testing."""

from typing import Any, Dict
from uuid import UUID, uuid5

import pytest

from utilities.common.dynamoDB_tables import get_table_name


def get_dynamodb_table(
    dynamodb: Dict[str, Any],
    entity_type: str,
    stack_name: str = "database",
) -> Any:
    """
    Get a DynamoDB table resource.

    Args:
        dynamodb: DynamoDB fixture with client and resource
        entity_type: Entity type (organisation, location, healthcare-service, etc.)
        stack_name: Stack name (default: database)

    Returns:
        DynamoDB Table resource
    """
    dynamodb_resource = dynamodb["resource"]
    table_name = get_table_name(entity_type, stack_name=stack_name)
    return dynamodb_resource.Table(table_name)


def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """
    Get nested value from dictionary using dot notation.

    Args:
        obj: Dictionary to extract value from
        path: Dot-separated path (e.g., "createdBy.type")

    Returns:
        Value at the specified path

    Raises:
        pytest.fail: If path is invalid or key not found

    Example:
        >>> data = {"user": {"name": "John", "age": 30}}
        >>> get_nested_value(data, "user.name")
        'John'
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


def get_entity_record(
    dynamodb: Dict[str, Any],
    entity_type: str,
    service_id: str,
) -> Dict[str, Any]:
    """
    Retrieve entity record from DynamoDB based on entity type and service ID.

    Uses deterministic UUID generation from service_id to locate records.

    Args:
        dynamodb: DynamoDB client and resource dictionary
        entity_type: Type of entity (organisation, location, healthcare-service)
        service_id: Service ID to lookup

    Returns:
        Entity record from DynamoDB

    Raises:
        AssertionError: If entity not found
    """
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
    entity_table = get_dynamodb_table(dynamodb, entity_type)
    entity_response = entity_table.get_item(
        Key={"id": entity_uuid, "field": "document"}
    )
    assert "Item" in entity_response, (
        f"{entity_type} not found for service ID {service_id}"
    )

    return entity_response["Item"]


def create_entity_record_from_table(
    dynamodb: Dict[str, Any],
    entity_type: str,
    table_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create an entity record in DynamoDB from parsed table data.

    Args:
        dynamodb: DynamoDB fixture
        entity_type: Entity type (organisation, location, healthcare-service)
        table_data: Dictionary with 'id', 'field', and 'value' keys
                    (values may be strings, bools, or ints from gherkin parsing)

    Returns:
        Created item data

    Raises:
        ValueError: If required fields are missing
    """
    entity_id = table_data.get("id")
    field_name = table_data.get("field")
    value = table_data.get("value")

    # Check for None specifically, not falsy values (False, 0, "" are valid)
    if entity_id is None or field_name is None or value is None:
        raise ValueError(
            f"Missing required fields in table data. "
            f"Got: id={entity_id}, field={field_name}, value={value}"
        )

    entity_table = get_dynamodb_table(dynamodb, entity_type)

    # Convert values to strings for DynamoDB storage
    # Boolean True/False -> "true"/"false" (lowercase for consistency)
    # This preserves the original Gherkin format for version history comparisons
    if isinstance(value, bool):
        value_str = "true" if value else "false"
    else:
        value_str = str(value)

    item = {
        "id": str(entity_id),
        "field": str(field_name),
        "value": value_str,
    }

    entity_table.put_item(Item=item)

    return {
        "entity_id": entity_id,
        "field_name": field_name,
        "entity_type": entity_type,
        "old_value": value_str,  # Return the normalized string value
    }


def update_entity_field(
    dynamodb: Dict[str, Any],
    entity_type: str,
    entity_id: str,
    field_name: str,
    new_value: str,
) -> None:
    """
    Update an entity field in DynamoDB.

    Args:
        dynamodb: DynamoDB fixture
        entity_type: Entity type (organisation, location, healthcare-service)
        entity_id: Entity UUID
        field_name: Field name to update
        new_value: New field value
    """
    entity_table = get_dynamodb_table(dynamodb, entity_type)

    entity_table.update_item(
        Key={"id": entity_id, "field": field_name},
        UpdateExpression="SET #value = :new_value",
        ExpressionAttributeNames={"#value": "value"},
        ExpressionAttributeValues={":new_value": new_value},
    )
