"""Stream event processor for version history."""

import re
from typing import Any

from boto3.dynamodb.types import TypeDeserializer
from ftrs_common.logger import Logger

from version_history.change_detector import detect_changes, extract_changed_by
from version_history.models import VersionHistoryRecord
from version_history.repository import VersionHistoryRepository

logger = Logger.get(service="version-history-stream-processor")


def process_stream_records(
    records: list[dict[str, Any]], endpoint_url: str | None = None
) -> list[str]:
    """
    Process DynamoDB stream records and write version history.

    Args:
        records: List of DynamoDB stream records from the event
        endpoint_url: Optional DynamoDB endpoint URL (for local development)

    Returns:
        List of failed record sequenceNumbers for batch failure handling
    """
    repository = VersionHistoryRepository(endpoint_url=endpoint_url)
    deserializer = TypeDeserializer()
    failed_sequence_numbers: list[str] = []

    logger.log("VH_STREAM_001", record_count=len(records))

    for record in records:
        sequence_number = record.get("dynamodb", {}).get("SequenceNumber", "unknown")

        try:
            # Extract event details
            event_name = record.get("eventName")
            event_source_arn = record.get("eventSourceARN", "")

            # Extract table name from ARN
            table_name = _extract_table_name(event_source_arn)
            if not table_name:
                logger.error(
                    f"Could not extract table name from ARN: {event_source_arn}"
                )
                failed_sequence_numbers.append(sequence_number)
                continue

            # Get record ID from Keys
            dynamodb_data = record.get("dynamodb", {})
            keys = dynamodb_data.get("Keys", {})
            record_id = _deserialize_value(keys.get("id", {}), deserializer)

            if not record_id:
                logger.error(f"Could not extract record ID from keys: {keys}")
                failed_sequence_numbers.append(sequence_number)
                continue

            # Get OldImage and NewImage
            old_image_raw = dynamodb_data.get("OldImage", {})
            new_image_raw = dynamodb_data.get("NewImage", {})

            # Skip if no images available
            if not old_image_raw or not new_image_raw:
                logger.log(
                    "VH_STREAM_002",
                    record_id=record_id,
                    table_name=table_name,
                    event_name=event_name,
                )
                continue

            # Deserialize DynamoDB JSON format
            old_document = _deserialize_document(old_image_raw, deserializer)
            new_document = _deserialize_document(new_image_raw, deserializer)

            # Detect changes
            changed_fields = detect_changes(old_document, new_document)

            # Skip if no business-relevant changes
            if not changed_fields:
                logger.log(
                    "VH_STREAM_003",
                    record_id=record_id,
                    table_name=table_name,
                )
                continue

            # Extract audit information
            changed_by = extract_changed_by(new_document)

            # Create version history record
            version_record = VersionHistoryRecord(
                entity_id=VersionHistoryRecord.create_entity_id(
                    table_name=table_name,
                    record_id=str(record_id),
                    field="document",
                ),
                timestamp=VersionHistoryRecord.create_timestamp(),
                change_type="UPDATE",  # MODIFY events are always updates
                changed_fields=changed_fields,
                changed_by=changed_by,
            )

            # Write to version history table
            repository.write_change_record(version_record)

            logger.log(
                "VH_STREAM_004",
                record_id=record_id,
                table_name=table_name,
                changed_field_count=len(changed_fields),
            )

        except Exception as e:
            logger.error(
                f"Failed to process stream record {sequence_number}: {e}",
                exc_info=True,
            )
            failed_sequence_numbers.append(sequence_number)

    if failed_sequence_numbers:
        logger.log("VH_STREAM_005", failed_count=len(failed_sequence_numbers))

    logger.log(
        "VH_STREAM_006",
        total_records=len(records),
        failed_records=len(failed_sequence_numbers),
    )

    return failed_sequence_numbers


def _extract_table_name(event_source_arn: str) -> str | None:
    """
    Extract table name from DynamoDB stream ARN.

    ARN format: arn:aws:dynamodb:region:account:table/table-name/stream/timestamp

    Args:
        event_source_arn: The DynamoDB stream ARN

    Returns:
        Table name or None if extraction fails
    """
    match = re.search(r"/table/([^/]+)/stream/", event_source_arn)
    if match:
        return match.group(1)
    return None


def _deserialize_document(
    raw_document: dict[str, Any], deserializer: TypeDeserializer
) -> dict[str, Any]:
    """
    Deserialize a DynamoDB document from stream format.

    Args:
        raw_document: Raw DynamoDB JSON document
        deserializer: TypeDeserializer instance

    Returns:
        Deserialized Python dictionary
    """
    deserialized = {}
    for key, value in raw_document.items():
        deserialized[key] = deserializer.deserialize(value)
    return deserialized


def _deserialize_value(
    raw_value: dict[str, Any], deserializer: TypeDeserializer
) -> Any:  # noqa: ANN401
    """
    Deserialize a single DynamoDB value.

    Args:
        raw_value: Raw DynamoDB JSON value
        deserializer: TypeDeserializer instance

    Returns:
        Deserialized Python value
    """
    if not raw_value:
        return None
    return deserializer.deserialize(raw_value)
