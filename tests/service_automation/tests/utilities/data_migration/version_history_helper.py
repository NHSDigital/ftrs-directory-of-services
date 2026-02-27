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
        if last_updated_by is None:
            last_updated_by = {
                "type": "app",
                "value": "INTERNAL001",
                "display": "Data Migration",
            }

        # Build a mock DynamoDB stream event (matches real stream format)
        stream_event = self._build_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            last_updated_by=last_updated_by,
        )

        # Create Lambda event with stream record
        lambda_event = {"Records": [stream_event]}

        # Create mock Lambda context
        mock_context = self._create_mock_lambda_context()

        # Inject endpoint URL for LocalStack
        original_endpoint = os.environ.get("ENDPOINT_URL")
        try:
            if self.dynamodb_endpoint:
                os.environ["ENDPOINT_URL"] = self.dynamodb_endpoint

            # Call Lambda handler directly (like MigrationHelper does)
            logger.debug(
                f"Processing stream event for {table_name} "
                f"field {field_name}: {old_value} -> {new_value}"
            )
            lambda_handler(lambda_event, mock_context)

        finally:
            # Restore original endpoint
            if original_endpoint:
                os.environ["ENDPOINT_URL"] = original_endpoint
            elif "ENDPOINT_URL" in os.environ:
                del os.environ["ENDPOINT_URL"]

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
        if last_updated_by is None:
            last_updated_by = {
                "type": "app",
                "value": "INTERNAL001",
                "display": "Data Migration",
            }

        # Build a mock DynamoDB stream event for document updates
        stream_event = self._build_document_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            old_document=old_document,
            new_document=new_document,
            last_updated_by=last_updated_by,
        )

        # Create Lambda event with stream record
        lambda_event = {"Records": [stream_event]}

        # Create mock Lambda context
        mock_context = self._create_mock_lambda_context()

        # Inject endpoint URL for LocalStack
        original_endpoint = os.environ.get("ENDPOINT_URL")
        try:
            if self.dynamodb_endpoint:
                os.environ["ENDPOINT_URL"] = self.dynamodb_endpoint

            # Call Lambda handler directly
            logger.debug(
                f"Processing document stream event for {table_name} id={entity_id}"
            )
            lambda_handler(lambda_event, mock_context)

        finally:
            # Restore original endpoint
            if original_endpoint:
                os.environ["ENDPOINT_URL"] = original_endpoint
            elif "ENDPOINT_URL" in os.environ:
                del os.environ["ENDPOINT_URL"]

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
        if last_updated_by is None:
            last_updated_by = {
                "type": "app",
                "value": "INTERNAL001",
                "display": "Data Migration",
            }

        # Build a mock DynamoDB stream event for document creation
        stream_event = self._build_document_create_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            new_document=new_document,
            last_updated_by=last_updated_by,
        )

        # Create Lambda event with stream record
        lambda_event = {"Records": [stream_event]}

        # Create mock Lambda context
        mock_context = self._create_mock_lambda_context()

        # Inject endpoint URL for LocalStack
        original_endpoint = os.environ.get("ENDPOINT_URL")
        try:
            if self.dynamodb_endpoint:
                os.environ["ENDPOINT_URL"] = self.dynamodb_endpoint

            # Call Lambda handler directly
            logger.debug(
                f"Processing document CREATE event for {table_name} id={entity_id}"
            )
            lambda_handler(lambda_event, mock_context)

        finally:
            # Restore original endpoint
            if original_endpoint:
                os.environ["ENDPOINT_URL"] = original_endpoint
            elif "ENDPOINT_URL" in os.environ:
                del os.environ["ENDPOINT_URL"]

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
        if last_updated_by is None:
            last_updated_by = {
                "type": "app",
                "value": "INTERNAL001",
                "display": "Data Migration",
            }

        # Build a mock DynamoDB stream event for document deletion
        stream_event = self._build_document_delete_stream_event(
            table_name=table_name,
            entity_id=entity_id,
            old_document=old_document,
            last_updated_by=last_updated_by,
        )

        # Create Lambda event with stream record
        lambda_event = {"Records": [stream_event]}

        # Create mock Lambda context
        mock_context = self._create_mock_lambda_context()

        # Inject endpoint URL for LocalStack
        original_endpoint = os.environ.get("ENDPOINT_URL")
        try:
            if self.dynamodb_endpoint:
                os.environ["ENDPOINT_URL"] = self.dynamodb_endpoint

            # Call Lambda handler directly
            logger.debug(
                f"Processing document DELETE event for {table_name} id={entity_id}"
            )
            lambda_handler(lambda_event, mock_context)

        finally:
            # Restore original endpoint
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
        # Build OldImage with document fields at root level
        old_image = {
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
        # Add all document fields
        for key, value in old_document.items():
            old_image[key] = self._serialize_value(value)

        # Build NewImage with document fields at root level
        new_image = {
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
        # Add all document fields
        for key, value in new_document.items():
            new_image[key] = self._serialize_value(value)

        return {
            "eventID": f"test-event-{entity_id}-document",
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
                    "field": {"S": "document"},
                },
                "OldImage": old_image,
                "NewImage": new_image,
                "SequenceNumber": f"{int(time.time() * 1000)}",
                "SizeBytes": 123,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
        }

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
        # Build NewImage with document fields at root level
        new_image = {
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
        # Add all document fields
        for key, value in new_document.items():
            new_image[key] = self._serialize_value(value)

        return {
            "eventID": f"test-event-{entity_id}-document-insert",
            "eventName": "INSERT",
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
                "NewImage": new_image,
                "SequenceNumber": f"{int(time.time() * 1000)}",
                "SizeBytes": 123,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
        }

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
        # Build OldImage with document fields at root level
        old_image = {
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
        # Add all document fields
        for key, value in old_document.items():
            old_image[key] = self._serialize_value(value)

        return {
            "eventID": f"test-event-{entity_id}-document-remove",
            "eventName": "REMOVE",
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
                "OldImage": old_image,
                "SequenceNumber": f"{int(time.time() * 1000)}",
                "SizeBytes": 123,
                "StreamViewType": "NEW_AND_OLD_IMAGES",
            },
        }

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
