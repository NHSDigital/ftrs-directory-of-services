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

from version_history.utils import (
    compute_field_delta,
    extract_changed_by,
    extract_table_name_from_arn,
)

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
    event_source_arn = record.event_source_arn or ""
    full_table_name = extract_table_name_from_arn(event_source_arn)
    entity_name = extract_entity_name_from_table_name(full_table_name)

    keys = record.dynamodb.keys or {}
    old_image: Optional[Dict[str, Any]] = record.dynamodb.old_image
    new_image: Optional[Dict[str, Any]] = record.dynamodb.new_image

    record_id = keys.get("id")
    field_name = keys.get("field")

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_006,
        entity_name=entity_name,
        record_id=record_id,
        field_name=field_name,
        has_old_image=old_image is not None,
        has_new_image=new_image is not None,
        keys=keys,
    )

    # Extract old and new values
    old_value = old_image.get("value") if old_image else None
    new_value = new_image.get("value") if new_image else None

    # Get event name - access directly from the record dictionary
    event_name = record.get("eventName", "MODIFY")

    # Log start of processing with key details
    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_003,
        entity_name=entity_name,
        record_id=record_id,
        field_name=field_name,
        event_type=event_name,
    )

    # Map event types to change types and delta parameters
    event_config = {
        "INSERT": ("CREATE", None, new_value),
        "REMOVE": ("DELETE", old_value, None),
        "MODIFY": ("UPDATE", old_value, new_value),
    }

    # Get configuration for this event type, default to UPDATE
    change_type, old_val, new_val = event_config.get(
        event_name, ("UPDATE", old_value, new_value)
    )

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_007,
        event_name=event_name,
        change_type=change_type,
        old_val_present=old_val is not None,
        new_val_present=new_val is not None,
    )

    # Skip if UPDATE with no actual change
    if change_type == "UPDATE" and old_val == new_val:
        LOGGER.log(
            VersionHistoryLogBase.VH_PROCESSOR_001,
            entity_name=entity_name,
            record_id=record_id,
            field_name=field_name,
        )
        return

    # Compute field delta and create changed_fields
    field_delta = compute_field_delta(old_val, new_val)
    changed_fields = {field_name: field_delta}

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_008,
        field_name=field_name,
        delta_keys=list(field_delta.keys()),
        has_diff="diff" in field_delta,
    )

    # Log the detected change
    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_004,
        old_value=old_value,
        new_value=new_value,
    )

    # Extract ChangedBy from NewImage (for DELETE, use OldImage)
    changed_by = extract_changed_by(new_image or old_image or {})

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_009,
        changed_by_type=changed_by.get("type"),
        changed_by_value=changed_by.get("value"),
        changed_by_display=changed_by.get("display"),
    )

    # Build entity_id: {entity_name}|{record_id}|{field_name}
    entity_id = f"{entity_name}|{record_id}|{field_name}"

    # Generate timestamp
    timestamp = datetime.now(UTC)

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_010,
        entity_id=entity_id,
        timestamp=timestamp.isoformat(),
    )

    # Create version history item
    version_item = {
        "entity_id": entity_id,
        "timestamp": timestamp.isoformat(),
        "change_type": change_type,
        "changed_fields": changed_fields,
        "changed_by": changed_by,
    }

    # Log before writing to table
    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_005,
        version_item=version_item,
    )

    # Write to version history table
    version_history_table.put_item(Item=version_item)

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_002,
        entity_id=entity_id,
        change_type=change_type,
        changed_fields=list(changed_fields.keys()),
    )
