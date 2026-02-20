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


def _extract_record_metadata(
    record: DynamoDBRecord,
) -> tuple[str, str, Optional[Dict[str, Any]], Optional[Dict[str, Any]], str, str]:
    """Extract metadata from stream record."""
    event_source_arn = record.event_source_arn or ""
    full_table_name = extract_table_name_from_arn(event_source_arn)
    entity_name = extract_entity_name_from_table_name(full_table_name)

    keys = record.dynamodb.keys or {}
    old_image = record.dynamodb.old_image
    new_image = record.dynamodb.new_image

    record_id = keys.get("id")
    field_name = keys.get("field")
    event_name = record.get("eventName", "MODIFY")

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

    return entity_name, event_name, old_image, new_image, record_id, field_name


def _determine_change_type(
    event_name: str,
    old_image: Optional[Dict[str, Any]],
    new_image: Optional[Dict[str, Any]],
    field_name: str,
) -> tuple[str, Any, Any]:
    """Map DynamoDB event to change type and extract values."""
    # System/metadata fields to exclude when extracting document values
    SYSTEM_FIELDS = {
        "id",
        "field",
        "created",
        "lastUpdated",
        "createdBy",
        "lastUpdatedBy",
    }

    # For "document" field, the entire item (minus system fields) is the value
    # For other fields, look for a "value" key
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
        LOGGER.log(
            VersionHistoryLogBase.VH_PROCESSOR_017,
            field_name=field_name,
            is_document_field=True,
            system_fields_count=len(SYSTEM_FIELDS),
        )
    else:
        old_value = old_image.get("value") if old_image else None
        new_value = new_image.get("value") if new_image else None
        LOGGER.log(
            VersionHistoryLogBase.VH_PROCESSOR_017,
            field_name=field_name,
            is_document_field=False,
            system_fields_count=0,
        )

    event_config = {
        "INSERT": ("CREATE", None, new_value),
        "REMOVE": ("DELETE", old_value, None),
        "MODIFY": ("UPDATE", old_value, new_value),
    }

    change_type, old_val, new_val = event_config.get(
        event_name, ("UPDATE", old_value, new_value)
    )

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_007,
        event_name=event_name,
        change_type=change_type,
        old_val_present=old_val is not None,
        new_val_present=new_val is not None,
        old_val=old_val,
        new_val=new_val,
        old_type=type(old_val).__name__,
        new_type=type(new_val).__name__,
    )

    return change_type, old_val, new_val


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

    # Simple values: check direct equality
    if "diff" not in field_delta:
        if field_delta.get("old") == field_delta.get("new"):
            LOGGER.log(
                VersionHistoryLogBase.VH_PROCESSOR_013,
                entity_name=entity_name,
                record_id=record_id,
                field_name=field_name,
                old_val=field_delta.get("old"),
                new_val=field_delta.get("new"),
            )
            return True
        else:
            LOGGER.log(
                VersionHistoryLogBase.VH_PROCESSOR_014,
                old_val=field_delta.get("old"),
                new_val=field_delta.get("new"),
            )
    # Complex values: check for empty diff
    elif not field_delta.get("diff"):
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
    field_name: str,
    change_type: str,
    changed_fields: Dict[str, Any],
    new_image: Optional[Dict[str, Any]],
    old_image: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build version history item for DynamoDB."""
    changed_by = extract_changed_by(new_image or old_image or {})

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_009,
        changed_by_type=changed_by.get("type"),
        changed_by_value=changed_by.get("value"),
        changed_by_display=changed_by.get("display"),
    )

    entity_id = f"{entity_name}|{record_id}|{field_name}"
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
        "changed_fields": changed_fields,
        "changed_by": changed_by,
    }


def process_stream_record(
    record: DynamoDBRecord,
    version_history_table: "Table",
) -> None:
    """Process DynamoDB stream record and write to version history."""
    entity_name, event_name, old_image, new_image, record_id, field_name = (
        _extract_record_metadata(record)
    )

    change_type, old_val, new_val = _determine_change_type(
        event_name, old_image, new_image, field_name
    )

    field_delta = compute_field_delta(old_val, new_val)

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

    changed_fields = {field_name: field_delta}

    LOGGER.log(
        VersionHistoryLogBase.VH_PROCESSOR_004,
        old_value=old_val,
        new_value=new_val,
    )

    version_item = _create_version_item(
        entity_name,
        record_id,
        field_name,
        change_type,
        changed_fields,
        new_image,
        old_image,
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
        changed_fields=list(changed_fields.keys()),
    )
