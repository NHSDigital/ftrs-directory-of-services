"""Helper utilities for constructing SQS events in tests."""
from datetime import datetime
from typing import Any, Dict, List, Literal


SQSEventMethod = Literal["insert", "update", "delete"]


def build_sqs_event(
    table_name: str,
    record_id: int,
    method: SQSEventMethod,
    message_id: str = "test-message-1",
    region: str = "eu-west-2",
) -> Dict[str, Any]:
    """
    Build a minimal SQS event for testing data migration.

    Args:
        table_name: Name of the table (e.g., 'services')
        record_id: Database record ID (e.g., service ID)
        method: DMS operation type ('insert', 'update', or 'delete')
        message_id: Optional message ID for the SQS record
        region: AWS region for the event

    Returns:
        Dictionary containing SQS event structure

    Example:
        >>> event = build_sqs_event(
        ...     table_name="services",
        ...     record_id=300010,
        ...     method="insert"
        ... )
        >>> event["Records"][0]["body"]
        '{"type": "dms_event", "record_id": 300010, "table_name": "services", "method": "insert"}'
    """
    timestamp_ms = str(int(datetime.now().timestamp() * 1000))

    body = {
        "type": "dms_event",
        "record_id": record_id,
        "table_name": table_name,
        "method": method,
    }

    return {
        "Records": [
            {
                "messageId": message_id,
                "receiptHandle": f"test-receipt-handle-{record_id}",
                "body": str(body).replace("'", '"'),  # Convert to JSON string
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": timestamp_ms,
                    "SenderId": "EXAMPLE123456789012",
                    "ApproximateFirstReceiveTimestamp": timestamp_ms,
                },
                "messageAttributes": {},
                "md5OfBody": f"test-md5-{record_id}",
                "eventSource": "aws:sqs",
                "awsRegion": region,
            }
        ]
    }


def build_multi_record_sqs_event(
    records: List[Dict[str, Any]],
    region: str = "eu-west-2",
) -> Dict[str, Any]:
    """
    Build an SQS event with multiple records.

    Args:
        records: List of record dictionaries with keys: table_name, record_id, method
        region: AWS region for the event

    Returns:
        Dictionary containing SQS event with multiple records

    Example:
        >>> event = build_multi_record_sqs_event([
        ...     {"table_name": "services", "record_id": 300010, "method": "insert"},
        ...     {"table_name": "services", "record_id": 300011, "method": "update"}
        ... ])
        >>> len(event["Records"])
        2
    """
    timestamp_ms = str(int(datetime.now().timestamp() * 1000))

    sqs_records = []
    for idx, record in enumerate(records):
        body = {
            "type": "dms_event",
            "record_id": record["record_id"],
            "table_name": record["table_name"],
            "method": record["method"],
        }

        sqs_records.append(
            {
                "messageId": f"test-message-{idx + 1}",
                "receiptHandle": f"test-receipt-handle-{idx + 1}",
                "body": str(body).replace("'", '"'),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": timestamp_ms,
                    "SenderId": "EXAMPLE123456789012",
                    "ApproximateFirstReceiveTimestamp": timestamp_ms,
                },
                "messageAttributes": {},
                "md5OfBody": f"test-md5-{idx + 1}",
                "eventSource": "aws:sqs",
                "awsRegion": region,
            }
        )

    return {"Records": sqs_records}


def build_empty_sqs_event() -> Dict[str, Any]:
    """
    Build an empty SQS event (no records).

    Returns:
        Dictionary containing empty SQS event

    Example:
        >>> event = build_empty_sqs_event()
        >>> event["Records"]
        []
    """
    return {"Records": []}
