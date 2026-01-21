"""Helper utilities for constructing SQS events in tests."""

from datetime import datetime
from typing import Any, Dict, Literal

from service_migration.application import DMSEvent

# Constants
TEST_AWS_REGION = "eu-west-2"
TEST_SQS_QUEUE_NAME = "test-queue"

SQSEventMethod = Literal["insert", "update", "delete"]


def build_sqs_event(
    table_name: str,
    record_id: int,
    service_id: int,
    method: SQSEventMethod,
    message_id: str = "test-message-1",
    region: str = TEST_AWS_REGION,
) -> Dict[str, Any]:
    """
    Build a minimal SQS event for testing data migration.

    Args:
        table_name: Name of the table (e.g., 'services')
        record_id: Database record ID
        service_id: Service ID for the record
        method: DMS operation type ('insert', 'update', or 'delete')
        message_id: Optional message ID for the SQS record
        region: AWS region for the event

    Returns:
        Dictionary containing SQS event structure

    Example:
        ... event = build_sqs_event(
        ...     table_name="services",
        ...     record_id=300010,
        ...     service_id=300010,
        ...     method="insert"
        ... )
        ... len(event["Records"])
        1
    """
    timestamp_ms = str(int(datetime.now().timestamp() * 1000))

    dms_event = DMSEvent(
        record_id=record_id,
        service_id=service_id,
        table_name=table_name,
        method=method,
    )

    return {
        "Records": [
            {
                "messageId": message_id,
                "receiptHandle": f"test-receipt-handle-{record_id}",
                "body": dms_event.model_dump_json(),
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
