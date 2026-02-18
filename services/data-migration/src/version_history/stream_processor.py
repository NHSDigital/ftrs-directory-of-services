"""Stream processing logic for version history tracking."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict

from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import extract_entity_name_from_table_name

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

from version_history.utils import (
    deserialize_dynamodb_item,
    extract_changed_by,
    extract_table_name_from_arn,
)

LOGGER = Logger.get(service="version-history")

TRACKED_TABLES = {"organisation", "location", "healthcare-service"}


def process_stream_record(
    record: Dict[str, Any],
    version_history_table: "Table",
) -> None:
    """
    Process a single DynamoDB stream record and write to version history.

    Args:
        record: DynamoDB stream record
        version_history_table: DynamoDB table resource for version-history

    Raises:
        Exception: If processing fails
    """
    dynamodb_data = record.get("dynamodb", {})
    event_source_arn = record.get("eventSourceARN", "")

    # Extract full table name from ARN and then extract entity name
    full_table_name = extract_table_name_from_arn(event_source_arn)
    entity_name = extract_entity_name_from_table_name(full_table_name)

    if entity_name not in TRACKED_TABLES:
        LOGGER.debug(
            "Skipping non-tracked table",
            extra={"entity_name": entity_name},
        )
        return

    # Deserialize keys and images
    keys = deserialize_dynamodb_item(dynamodb_data.get("Keys", {}))
    old_image = deserialize_dynamodb_item(dynamodb_data.get("OldImage", {}))
    new_image = deserialize_dynamodb_item(dynamodb_data.get("NewImage", {}))

    record_id = keys.get("id")
    field_name = keys.get("field")

    if not record_id or not field_name:
        LOGGER.warning(
            "Missing required keys in stream record",
            extra={"keys": keys, "record_id": record_id, "field_name": field_name},
        )
        return

    # Extract old and new values
    old_value = old_image.get("value") if old_image else None
    new_value = new_image.get("value") if new_image else None

    # Skip if values are identical (no-op update)
    if old_value == new_value:
        LOGGER.debug(
            "No change detected, skipping version history",
            extra={
                "entity_name": entity_name,
                "record_id": record_id,
                "field_name": field_name,
            },
        )
        return

    # Build changed fields dict
    changed_fields = {field_name: {"old": old_value, "new": new_value}}

    # Extract ChangedBy from NewImage
    changed_by = extract_changed_by(new_image)

    # Build entity_id: {entity_name}|{record_id}|{field_name}
    entity_id = f"{entity_name}|{record_id}|{field_name}"

    # Generate timestamp in ISO8601 format with Z suffix
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create version history item
    version_item = {
        "entity_id": entity_id,
        "timestamp": timestamp,
        "change_type": "UPDATE",
        "changed_fields": changed_fields,
        "changed_by": changed_by,
    }

    # Write to version history table
    version_history_table.put_item(Item=version_item)

    LOGGER.info(
        "Version history recorded",
        extra={"entity_id": entity_id, "changed_fields": list(changed_fields.keys())},
    )
