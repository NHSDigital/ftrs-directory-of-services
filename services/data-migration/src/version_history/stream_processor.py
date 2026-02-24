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

# System/metadata fields to exclude from document values
SYSTEM_FIELDS = {
    "id",
    "field",
    "created",
    "lastUpdated",
    "createdBy",
    "lastUpdatedBy",
}


def _extract_record_metadata(
    record: DynamoDBRecord,
) -> tuple[
    str,
    str,
    Optional[Dict[str, Any]],
    Optional[Dict[str, Any]],
    str,
    str,
    Dict[str, Any],
]:
    """Extract metadata from stream record."""
    event_source_arn = record.event_source_arn or ""
    full_table_name = extract_table_name_from_arn(event_source_arn)
    entity_name = extract_entity_name_from_table_name(full_table_name)

    keys = record.dynamodb.keys or {}
    old_image = record.dynamodb.old_image
    new_image = record.dynamodb.new_image

    record_id = keys.get("id")
    # Field name for composite key: "document" for gp org entities, may differ for pharmacy
    field_name = keys.get("field", "document")
    event_name = record.get("eventName", "MODIFY")

    return entity_name, event_name, old_image, new_image, record_id, field_name, keys


def _extract_field_values(
    old_image: Optional[Dict[str, Any]],
    new_image: Optional[Dict[str, Any]],
    field_name: str,
) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Extract field values from DynamoDB images.

    For 'document' field: extracts entire record excluding system fields.
    For specific fields: could extract individual field values.

    Args:
        old_image: Previous DynamoDB image
        new_image: New DynamoDB image
        field_name: Name of field to extract (e.g., 'document')

    Returns:
        Tuple of (old_value, new_value)
    """
    # For 'document' field type, extract entire record minus system fields
    if field_name == "document":
        old_value = (
            {k: v for k, v in old_image.items() if k not in SYSTEM_FIELDS}
            if old_image
            else None
        )
        new_value = (
            {k: v for k, v in new_image.items() if k not in SYSTEM_FIELDS}
            if new_image
            else None
        )
    else:
        # For specific field tracking, extract just that field
        old_value = old_image.get(field_name) if old_image else None
        new_value = new_image.get(field_name) if new_image else None

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_017,
        field_name=field_name,
        is_document_field=(field_name == "document"),
        system_fields_count=len(SYSTEM_FIELDS),
    )

    return old_value, new_value


def _determine_change_type(
    event_name: str,
    old_value: Optional[Dict[str, Any]],
    new_value: Optional[Dict[str, Any]],
) -> str:
    """Map DynamoDB event to change type."""
    event_to_change_type = {
        "INSERT": "CREATE",
        "REMOVE": "DELETE",
        "MODIFY": "UPDATE",
    }

    change_type = event_to_change_type.get(event_name, "UPDATE")

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_007,
        event_name=event_name,
        change_type=change_type,
        old_val_present=old_value is not None,
        new_val_present=new_value is not None,
        old_val=old_value,
        new_val=new_value,
        old_type=type(old_value).__name__,
        new_type=type(new_value).__name__,
    )

    return change_type


def _should_skip_update(
    change_type: str,
    field_delta: Dict[str, Any],
    entity_name: str,
    record_id: str,
    field_name: str,
) -> bool:
    """Check if UPDATE should be skipped due to no meaningful changes."""
    if change_type != "UPDATE":
        return False

    # Check for empty diff in complex values
    if not field_delta.get("diff"):
        LOGGER.log(
            VersionHistoryLogBase.VH_PROCESSOR_015,
            entity_name=entity_name,
            record_id=record_id,
            field_name=field_name,
        )
        return True
    else:
        LOGGER.log(
            VersionHistoryLogBase.VH_PROCESSOR_016,
            diff=field_delta.get("diff"),
        )

    return False


def _create_version_item(
    entity_name: str,
    record_id: str,
    change_type: str,
    field_delta: Dict[str, Any],
    new_image: Optional[Dict[str, Any]],
    old_image: Optional[Dict[str, Any]],
    field_name: str,
) -> Dict[str, Any]:
    """Build version history item for DynamoDB."""
    changed_by = extract_changed_by(new_image or old_image or {})

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_009,
        changed_by_type=changed_by.get("type"),
        changed_by_value=changed_by.get("value"),
        changed_by_display=changed_by.get("display"),
    )

    entity_id = f"{entity_name}#{record_id}#{field_name}"
    timestamp = datetime.now(UTC)

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_010,
        entity_id=entity_id,
        timestamp=timestamp.isoformat(),
    )

    return {
        "entity_id": entity_id,
        "timestamp": timestamp.isoformat(),
        "change_type": change_type,
        "changed_fields": {field_name: field_delta},
        "changed_by": changed_by,
    }


def process_stream_record(
    record: DynamoDBRecord,
    version_history_table: "Table",
) -> None:
    """Process DynamoDB stream record and write to version history."""
    entity_name, event_name, old_image, new_image, record_id, field_name, keys = (
        _extract_record_metadata(record)
    )

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_006,
        entity_name=entity_name,
        record_id=record_id,
        field_name=field_name,
        has_old_image=old_image is not None,
        has_new_image=new_image is not None,
        keys=keys,
    )

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_003,
        entity_name=entity_name,
        record_id=record_id,
        field_name=field_name,
        event_type=event_name,
    )

    old_value, new_value = _extract_field_values(old_image, new_image, field_name)
    change_type = _determine_change_type(event_name, old_value, new_value)
    field_delta = compute_field_delta(old_value, new_value)

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_008,
        field_name=field_name,
        delta_keys=list(field_delta.keys()),
        has_diff="diff" in field_delta,
        delta=field_delta,
        values_equal=field_delta.get("old") == field_delta.get("new"),
    )

    if _should_skip_update(
        change_type, field_delta, entity_name, record_id, field_name
    ):
        return

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_004,
        old_value=old_value,
        new_value=new_value,
    )

    version_item = _create_version_item(
        entity_name,
        record_id,
        change_type,
        field_delta,
        new_image,
        old_image,
        field_name,
    )

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_005,
        version_item=version_item,
    )

    version_history_table.put_item(Item=version_item)

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_002,
        entity_id=version_item["entity_id"],
        change_type=change_type,
        changed_fields=[field_name],
    )
