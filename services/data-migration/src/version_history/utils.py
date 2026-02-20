"""Utility functions for version history tracking."""

import json
from typing import Any, Dict

from boto3.dynamodb.types import TypeDeserializer
from deepdiff import DeepDiff

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


def compute_field_delta(old_value: Any, new_value: Any) -> Dict[str, Any]:  # noqa: ANN401
    """
    Compute a structured delta between old and new field values.

    For simple values (str, int, bool, None), returns {"old": old_value, "new": new_value}.
    For complex values (dict, list), uses DeepDiff to compute a detailed delta.

    Args:
        old_value: Previous field value
        new_value: New field value

    Returns:
        Dictionary with delta information:
        - For simple values: {"old": <value>, "new": <value>}
        - For complex values: {"old": <value>, "new": <value>, "diff": <deepdiff_json>}
    """
    # Simple types: return old/new
    if not isinstance(old_value, (dict, list)) and not isinstance(
        new_value, (dict, list)
    ):
        return {"old": old_value, "new": new_value}

    # Type mismatch: return old/new
    if type(old_value) is not type(new_value):
        return {"old": old_value, "new": new_value}

    # Complex types: compute detailed diff
    diff = DeepDiff(
        old_value,
        new_value,
        view="tree",
        threshold_to_diff_deeper=0,
        ignore_order=True,
    )

    diff_json = json.loads(diff.to_json())
    return {"old": old_value, "new": new_value, "diff": diff_json}
