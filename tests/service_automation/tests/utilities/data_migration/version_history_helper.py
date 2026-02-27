"""Helper for simulating version history Lambda in LocalStack tests."""

import os
import time
from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock

from loguru import logger
from version_history.lambda_handler import lambda_handler


class VersionHistoryHelper:
    """
    Test helper - directly invokes Lambda handler function.

    NOTE: Not testing AWS Streams → Lambda integration.
    """

    def __init__(self, dynamodb_endpoint: str | None = None):
        """
        Initialize the version history helper.

        Args:
            dynamodb_endpoint: DynamoDB endpoint URL for LocalStack
        """
        self.dynamodb_endpoint = dynamodb_endpoint

    def process_update_as_stream_event(
        self,
        table_name: str,
        entity_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        last_updated_by: Dict[str, str] | None = None,
    ) -> None:
        """
        Simulate a DynamoDB stream event and process it through Lambda handler.

        This mimics what would happen in real AWS:
        1. DynamoDB captures change
        2. Stream event generated
        3. Lambda triggered
        4. Lambda processes event
        5. Version history written

        Args:
            table_name: Full DynamoDB table name
            entity_id: Record ID
            field_name: Field being updated
            old_value: Previous value
            new_value: New value
            last_updated_by: Optional audit info
        """
        last_updated_by = self._get_default_audit_info(last_updated_by)
        stream_event = self._build_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            last_updated_by=last_updated_by,
        )
        logger.debug(
            f"Processing stream event for {table_name} "
            f"field {field_name}: {old_value} -> {new_value}"
        )
        self._process_stream_event(stream_event)

    def process_document_update_as_stream_event(
        self,
        table_name: str,
        entity_id: str,
        old_document: Dict[str, Any],
        new_document: Dict[str, Any],
        last_updated_by: Dict[str, str] | None = None,
    ) -> None:
        """
        Simulate a DynamoDB stream event for document field updates.

        This simulates the document storage pattern where the entire entity
        document is stored in a single record with field='document'.

        Args:
            table_name: Full DynamoDB table name
            entity_id: Record ID
            old_document: Previous document state (without system fields)
            new_document: New document state (without system fields)
            last_updated_by: Optional audit info
        """
        last_updated_by = self._get_default_audit_info(last_updated_by)
        stream_event = self._build_document_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            old_document=old_document,
            new_document=new_document,
            last_updated_by=last_updated_by,
        )
        logger.debug(f"Processing document UPDATE event for {table_name} id={entity_id}")
        self._process_stream_event(stream_event)

    def process_document_create_as_stream_event(
        self,
        table_name: str,
        entity_id: str,
        new_document: Dict[str, Any],
        last_updated_by: Dict[str, str] | None = None,
    ) -> None:
        """
        Simulate a DynamoDB stream event for document creation (INSERT).

        Args:
            table_name: Full DynamoDB table name
            entity_id: Record ID
            new_document: New document state (without system fields)
            last_updated_by: Optional audit info
        """
        last_updated_by = self._get_default_audit_info(last_updated_by)
        stream_event = self._build_document_create_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            new_document=new_document,
            last_updated_by=last_updated_by,
        )
        logger.debug(f"Processing document CREATE event for {table_name} id={entity_id}")
        self._process_stream_event(stream_event)

    def process_document_delete_as_stream_event(
        self,
        table_name: str,
        entity_id: str,
        old_document: Dict[str, Any],
        last_updated_by: Dict[str, str] | None = None,
    ) -> None:
        """
        Simulate a DynamoDB stream event for document deletion (REMOVE).

        Args:
            table_name: Full DynamoDB table name
            entity_id: Record ID
            old_document: Previous document state (without system fields)
            last_updated_by: Optional audit info
        """
        last_updated_by = self._get_default_audit_info(last_updated_by)
        stream_event = self._build_document_delete_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            old_document=old_document,
            last_updated_by=last_updated_by,
        )
        logger.debug(f"Processing document DELETE event for {table_name} id={entity_id}")
        self._process_stream_event(stream_event)

    def _get_default_audit_info(self, last_updated_by: Dict[str, str] | None) -> Dict[str, str]:
        """Get default audit info if none provided."""
        return last_updated_by or {
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        }

    def _process_stream_event(self, stream_event: Dict[str, Any]) -> None:
        """Process stream event through Lambda handler with LocalStack endpoint."""
        lambda_event = {"Records": [stream_event]}
        mock_context = self._create_mock_lambda_context()

        original_endpoint = os.environ.get("ENDPOINT_URL")
        try:
            if self.dynamodb_endpoint:
                os.environ["ENDPOINT_URL"] = self.dynamodb_endpoint
            lambda_handler(lambda_event, mock_context)
        finally:
            if original_endpoint:
                os.environ["ENDPOINT_URL"] = original_endpoint
            elif "ENDPOINT_URL" in os.environ:
                del os.environ["ENDPOINT_URL"]

    def _build_stream_event(
        self,
        table_name: str,
        entity_id: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        last_updated_by: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Build a mock DynamoDB stream event record.

        Matches the format of real DynamoDB stream events.
        """
        return {
            "eventID": f"test-event-{entity_id}-{field_name}",
            "eventName": "MODIFY",
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "eu-west-2",
            "eventSourceARN": (
                f"arn:aws:dynamodb:eu-west-2:123456789012:table/"
                f"{table_name}/stream/2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "ApproximateCreationDateTime": int(time.time()),
                "Keys": {
                    "id": {"S": entity_id},
                    "field": {"S": field_name},
                },
                "OldImage": {
                    "id": {"S": entity_id},
                    "field": {"S": field_name},
                    "value": self._serialize_value(old_value),
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": last_updated_by.get("type", "system")},
                            "value": {"S": last_updated_by.get("value", "unknown")},
                            "display": {"S": last_updated_by.get("display", "System")},
                        }
                    },
                },
                "NewImage": {
                    "id": {"S": entity_id},
                    "field": {"S": field_name},
                    "value": self._serialize_value(new_value),
                    "lastUpdatedBy": {
                        "M": {
                            "type": {"S": last_updated_by.get("type", "system")},
                            "value": {"S": last_updated_by.get("value", "unknown")},
                            "display": {"S": last_updated_by.get("display", "System")},
                        }
                    },
                },
                "SequenceNumber": f"{int(time.time() * 1000)}",
                "SizeBytes": 123,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
        }

    def _build_document_stream_event(
        self,
        table_name: str,
        entity_id: str,
        old_document: Dict[str, Any],
        new_document: Dict[str, Any],
        last_updated_by: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Build a mock DynamoDB stream event for document field updates.

        The document storage pattern stores the entire entity document
        with field='document' and all document fields at the root level.
        """
        old_image = self._build_document_image(entity_id, old_document, last_updated_by)
        new_image = self._build_document_image(entity_id, new_document, last_updated_by)
        return self._build_base_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            event_name="MODIFY",
            event_suffix="document",
            old_image=old_image,
            new_image=new_image,
        )

    def _build_document_image(
        self,
        entity_id: str,
        document: Dict[str, Any],
        last_updated_by: Dict[str, str],
    ) -> Dict[str, Any]:
        """Build DynamoDB image with document fields at root level."""
        image = {
            "id": {"S": entity_id},
            "field": {"S": "document"},
            "lastUpdatedBy": {
                "M": {
                    "type": {"S": last_updated_by.get("type", "system")},
                    "value": {"S": last_updated_by.get("value", "unknown")},
                    "display": {"S": last_updated_by.get("display", "System")},
                }
            },
        }
        for key, value in document.items():
            image[key] = self._serialize_value(value)
        return image

    def _build_base_stream_event(
        self,
        table_name: str,
        entity_id: str,
        event_name: str,
        event_suffix: str,
        old_image: Dict[str, Any] | None = None,
        new_image: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Build base DynamoDB stream event structure."""
        event = {
            "eventID": f"test-event-{entity_id}-{event_suffix}",
            "eventName": event_name,
            "eventVersion": "1.1",
            "eventSource": "aws:dynamodb",
            "awsRegion": "eu-west-2",
            "eventSourceARN": (
                f"arn:aws:dynamodb:eu-west-2:123456789012:table/"
                f"{table_name}/stream/2025-01-01T00:00:00.000"
            ),
            "dynamodb": {
                "ApproximateCreationDateTime": int(time.time()),
                "Keys": {
                    "id": {"S": entity_id},
                    "field": {"S": "document"},
                },
                "SequenceNumber": f"{int(time.time() * 1000)}",
                "SizeBytes": 123,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
        }
        if old_image:
            event["dynamodb"]["OldImage"] = old_image
        if new_image:
            event["dynamodb"]["NewImage"] = new_image
        return event

    def _build_document_create_stream_event(
        self,
        table_name: str,
        entity_id: str,
        new_document: Dict[str, Any],
        last_updated_by: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Build a mock DynamoDB stream event for document creation (INSERT).

        INSERT events only have NewImage (no OldImage).
        """
        new_image = self._build_document_image(entity_id, new_document, last_updated_by)
        return self._build_base_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            event_name="INSERT",
            event_suffix="document-insert",
            new_image=new_image,
        )

    def _build_document_delete_stream_event(
        self,
        table_name: str,
        entity_id: str,
        old_document: Dict[str, Any],
        last_updated_by: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Build a mock DynamoDB stream event for document deletion (REMOVE).

        REMOVE events only have OldImage (no NewImage).
        """
        old_image = self._build_document_image(entity_id, old_document, last_updated_by)
        return self._build_base_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            event_name="REMOVE",
            event_suffix="document-remove",
            old_image=old_image,
        )

    def _serialize_value(self, value: Any) -> Dict[str, Any]:
        """Serialize a Python value to DynamoDB format."""
        if isinstance(value, str):
            return {"S": value}
        elif isinstance(value, bool):
            return {"BOOL": value}
        elif isinstance(value, (int, float)):
            return {"N": str(value)}
        elif isinstance(value, dict):
            return {"M": {k: self._serialize_value(v) for k, v in value.items()}}
        elif isinstance(value, list):
            return {"L": [self._serialize_value(v) for v in value]}
        else:
            return {"S": str(value)}

    def _create_mock_lambda_context(self) -> Any:
        """Create a mock Lambda context for testing."""
        current_date = datetime.now().strftime("%Y/%m/%d")

        mock_context = MagicMock()
        mock_context.function_name = "test-version-history-function"
        mock_context.memory_limit_in_mb = 512
        mock_context.aws_request_id = "test-request-id"
        mock_context.log_group_name = "/aws/lambda/test-version-history-function"
        mock_context.log_stream_name = f"{current_date}/[$LATEST]test-request-id"
        mock_context.get_remaining_time_in_millis = lambda: 300000

        return mock_context
