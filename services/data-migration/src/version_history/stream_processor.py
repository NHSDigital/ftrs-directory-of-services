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
    event_name = record.get("eventName", "MODIFY")

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

    # Map DynamoDB event types to change types
    change_type_map = {
        "INSERT": "CREATE",
        "MODIFY": "UPDATE",
        "REMOVE": "DELETE",
    }
    change_type = change_type_map.get(event_name, "UPDATE")

    # Handle different event types
    if event_name == "INSERT":
        # CREATE: only new_image exists
        changed_fields = {field_name: {"old": None, "new": new_value}}
    elif event_name == "REMOVE":
        # DELETE: only old_image exists
        changed_fields = {field_name: {"old": old_value, "new": None}}
    else:
        # UPDATE: both images exist, skip if no change
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
        changed_fields = {field_name: {"old": old_value, "new": new_value}}

    # Extract ChangedBy from NewImage (for DELETE, use OldImage)
    changed_by = extract_changed_by(new_image or old_image)

    # Build entity_id: {entity_name}|{record_id}|{field_name}
    entity_id = f"{entity_name}|{record_id}|{field_name}"

    # Generate timestamp in ISO8601 format with Z suffix
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Create version history item
    version_item = {
        "entity_id": entity_id,
        "timestamp": timestamp,
        "change_type": change_type,
        "changed_fields": changed_fields,
        "changed_by": changed_by,
    }

    # Write to version history table
    version_history_table.put_item(Item=version_item)

    LOGGER.info(
        "Version history recorded",
        extra={
            "entity_id": entity_id,
            "change_type": change_type,
            "changed_fields": list(changed_fields.keys()),
        },
    )
