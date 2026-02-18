"""Utility functions for version history tracking."""

from typing import Any, Dict

from boto3.dynamodb.types import TypeDeserializer

DESERIALIZER = TypeDeserializer()


def extract_table_name_from_arn(event_source_arn: str) -> str:
    """
    Extract table name from DynamoDB stream ARN.

    Args:
        event_source_arn: ARN like "arn:aws:dynamodb:region:account:table/organisation/stream/..."

    Returns:
        Table name (e.g., "ftrs-dos-dev-database-organisation")
    """
    # ARN format: arn:aws:dynamodb:region:account:table/{table_name}/stream/{stream_id}
    parts = event_source_arn.split("/")
    return parts[1] if len(parts) > 1 else ""


def deserialize_dynamodb_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deserialize DynamoDB format to Python objects.

    Args:
        item: DynamoDB item with type descriptors (e.g., {"field": {"S": "value"}})

    Returns:
        Deserialized Python dict
    """
    return {k: DESERIALIZER.deserialize(v) for k, v in item.items()}


def extract_changed_by(new_image: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract ChangedBy information from NewImage's lastUpdatedBy field.

    Args:
        new_image: Deserialized NewImage from DynamoDB stream

    Returns:
        ChangedBy dict with type, value, and display fields
    """
    last_updated_by = new_image.get("lastUpdatedBy", {})

    # Set a default if lastUpdatedBy is missing
    if not last_updated_by:
        return {
            "type": "app",
            "value": "INTERNAL001",
            "display": "Data Migration",
        }

    return {
        "type": last_updated_by.get("type", "app"),
        "value": last_updated_by.get("value", "INTERNAL001"),
        "display": last_updated_by.get("display", "Data Migration"),
    }
