"""Utility functions for version history testing."""

from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from utilities.common.dynamoDB_tables import get_table_name


def get_version_history_records(
    dynamodb_resource: Any,
    entity_id: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Get version history records for a specific entity.

    Args:
        dynamodb_resource: DynamoDB resource
        entity_id: Entity ID in format {entity_type}|{record_id}|{field_name}
        limit: Maximum number of records to retrieve

    Returns:
        List of version history records sorted by timestamp (latest first)
    """
    version_history_table_name = get_table_name("version-history")
    version_history_table = dynamodb_resource.Table(version_history_table_name)

    response = version_history_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("entity_id").eq(entity_id),
        ScanIndexForward=False,  # Latest first
        Limit=limit,
    )

    return response.get("Items", [])


def get_latest_version_history_record(
    dynamodb_resource: Any,
    entity_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get the latest version history record for a specific entity.

    Args:
        dynamodb_resource: DynamoDB resource
        entity_id: Entity ID in format {entity_type}|{record_id}|{field_name}

    Returns:
        Latest version history record or None if not found
    """
    records = get_version_history_records(dynamodb_resource, entity_id, limit=1)
    return records[0] if records else None


def verify_version_history_change(
    version_record: Dict[str, Any],
    field_name: str,
    old_value: Any,
    new_value: Any,
) -> None:
    """
    Verify that a version history record contains the expected change.

    Args:
        version_record: Version history record
        field_name: Name of the changed field
        old_value: Expected old value
        new_value: Expected new value

    Raises:
        AssertionError: If the change doesn't match expectations
    """
    changed_fields = version_record.get("changed_fields", {})
    assert field_name in changed_fields, (
        f"Field '{field_name}' not found in changed_fields"
    )

    field_change = changed_fields[field_name]
    assert field_change.get("old") == old_value, (
        f"Expected old value '{old_value}', got '{field_change.get('old')}'"
    )
    assert field_change.get("new") == new_value, (
        f"Expected new value '{new_value}', got '{field_change.get('new')}'"
    )


def verify_version_history_timestamp(
    version_record: Dict[str, Any],
    max_age_seconds: int = 10,
) -> None:
    """
    Verify that a version history record has a valid and recent timestamp.

    Args:
        version_record: Version history record
        max_age_seconds: Maximum age in seconds for the record

    Raises:
        AssertionError: If timestamp is invalid or too old
    """
    timestamp = version_record.get("timestamp")
    assert timestamp, "No timestamp found in version history record"

    # Parse and verify recency
    parsed_time = datetime.fromisoformat(timestamp)
    now = datetime.now(parsed_time.tzinfo)
    age_seconds = (now - parsed_time).total_seconds()

    assert age_seconds <= max_age_seconds, (
        f"Timestamp is too old ({age_seconds}s), expected age <= {max_age_seconds}s"
    )


def verify_changed_by(
    version_record: Dict[str, Any],
    expected_type: str,
    expected_value: str,
    expected_display: str,
) -> None:
    """
    Verify the changed_by field in a version history record.

    Args:
        version_record: Version history record
        expected_type: Expected type (app, user, system)
        expected_value: Expected value
        expected_display: Expected display name

    Raises:
        AssertionError: If changed_by doesn't match expectations
    """
    changed_by = version_record.get("changed_by", {})

    assert changed_by.get("type") == expected_type, (
        f"Expected type '{expected_type}', got '{changed_by.get('type')}'"
    )

    assert changed_by.get("value") == expected_value, (
        f"Expected value '{expected_value}', got '{changed_by.get('value')}'"
    )

    assert changed_by.get("display") == expected_display, (
        f"Expected display '{expected_display}', got '{changed_by.get('display')}'"
    )


def build_entity_id(entity_type: str, record_id: str, field_name: str) -> str:
    """
    Build an entity_id for version history lookup.

    Args:
        entity_type: Entity type (organisation, location, healthcare-service)
        record_id: Record UUID
        field_name: Field name

    Returns:
        Entity ID in format {entity_type}|{record_id}|{field_name}
    """
    return f"{entity_type}|{record_id}|{field_name}"


def get_version_history_count(
    dynamodb_resource: Any,
    entity_id: str,
) -> int:
    """
    Get count of version history records for an entity.

    Useful for verifying that no new records were created when
    updating a field to the same value.

    Args:
        dynamodb_resource: DynamoDB resource
        entity_id: Entity ID in format {entity_type}|{record_id}|{field_name}

    Returns:
        Number of version history records for this entity

    Example:
        >>> initial_count = get_version_history_count(dynamodb, entity_id)
        >>> # Perform action that shouldn't create records
        >>> update_to_same_value()
        >>> final_count = get_version_history_count(dynamodb, entity_id)
        >>> assert final_count == initial_count, "Unexpected version history created"
    """
    version_history_table_name = get_table_name("version-history")
    version_history_table = dynamodb_resource.Table(version_history_table_name)

    response = version_history_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("entity_id").eq(entity_id),
        Select="COUNT",
    )

    return response.get("Count", 0)
