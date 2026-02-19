"""Stream processing logic for version history tracking."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from aws_lambda_powertools.utilities.data_classes.dynamo_db_stream_event import (
    DynamoDBRecord,
)
from ftrs_common.logger import Logger
from ftrs_common.utils.db_service import extract_entity_name_from_table_name
from ftrs_data_layer.logbase import VersionHistoryLogBase

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

from version_history.utils import extract_changed_by, extract_table_name_from_arn

LOGGER = Logger.get(service="version-history")


def process_stream_record(
    record: DynamoDBRecord,
    version_history_table: "Table",
) -> None:
    """
    Process a single DynamoDB stream record and write to version history.

    Args:
        record: DynamoDB stream record (DynamoDBRecord from Powertools)
        version_history_table: DynamoDB table resource for version-history

    Raises:
        Exception: If processing fails
    """
    # Extract full table name from ARN and then extract entity name
    event_source_arn = record.event_source_arn or ""
    full_table_name = extract_table_name_from_arn(event_source_arn)
    entity_name = extract_entity_name_from_table_name(full_table_name)

    # Access automatically deserialized keys and images
    keys = record.dynamodb.keys or {}
    old_image: Optional[Dict[str, Any]] = record.dynamodb.old_image
    new_image: Optional[Dict[str, Any]] = record.dynamodb.new_image

    record_id = keys.get("id")
    field_name = keys.get("field")

    # Extract old and new values
    old_value = old_image.get("value") if old_image else None
    new_value = new_image.get("value") if new_image else None

    # Get event name - access directly from the record dictionary
    # DynamoDBRecord inherits from DictWrapper which provides dict-like access
    event_name = record.get("eventName", "MODIFY")

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
            LOGGER.log(
                VersionHistoryLogBase.VH_PROCESSOR_001,
                entity_name=entity_name,
                record_id=record_id,
                field_name=field_name,
            )
            return
        changed_fields = {field_name: {"old": old_value, "new": new_value}}

    # Extract ChangedBy from NewImage (for DELETE, use OldImage)
    changed_by = extract_changed_by(new_image or old_image or {})

    # Build entity_id: {entity_name}|{record_id}|{field_name}
    entity_id = f"{entity_name}|{record_id}|{field_name}"

    # Generate timestamp
    timestamp = datetime.now(UTC)

    # Create version history item
    version_item = {
        "entity_id": entity_id,
        "timestamp": timestamp.isoformat(),
        "change_type": change_type,
        "changed_fields": changed_fields,
        "changed_by": changed_by,
    }

    # Write to version history table
    version_history_table.put_item(Item=version_item)

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_002,
        entity_id=entity_id,
        change_type=change_type,
        changed_fields=list(changed_fields.keys()),
    )
