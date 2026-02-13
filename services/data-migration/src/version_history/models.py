"""Version history record models."""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class VersionHistoryRecord(BaseModel):
    """
    Represents a version history record in SCD Type 2 format.

    Attributes:
        entity_id: Primary key with format: <table_name>|<record_id>|<field>
        timestamp: ISO 8601 timestamp (sort key)
        change_type: Type of change (CREATE, UPDATE, DELETE)
        changed_fields: Dictionary of changed fields with old/new values
        changed_by: Audit event from lastUpdatedBy field
    """

    entity_id: str = Field(
        ...,
        description="Composite identifier: <table_name>|<record_id>|<field>",
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp with Z suffix (UTC)",
    )
    change_type: Literal["CREATE", "UPDATE", "DELETE"] = Field(
        ...,
        description="Type of change operation",
    )
    changed_fields: dict[str, dict[str, Any]] = Field(
        ...,
        description="Map of field names to old/new value pairs",
    )
    changed_by: dict[str, str] = Field(
        ...,
        description="Audit event with display, type, and value fields",
    )

    @staticmethod
    def create_entity_id(
        table_name: str, record_id: str, field: str = "document"
    ) -> str:
        """
        Create an entity_id in the format: <table_name>|<record_id>|<field>.

        Args:
            table_name: The name of the source table
            record_id: The ID of the record that changed
            field: The field name (default: "document" for attribute-level tables)

        Returns:
            Formatted entity_id string
        """
        return f"{table_name}|{record_id}|{field}"

    @staticmethod
    def create_timestamp() -> str:
        """
        Create an ISO 8601 timestamp with Z suffix.

        Returns:
            Timestamp string in ISO 8601 format
        """
        return datetime.now(UTC).isoformat() + "Z"

    def to_dynamodb_item(self) -> dict[str, Any]:
        """
        Convert the record to a DynamoDB item format.

        Returns:
            Dictionary suitable for DynamoDB put_item operation
        """
        return {
            "entity_id": self.entity_id,
            "timestamp": self.timestamp,
            "change_type": self.change_type,
            "changed_fields": self.changed_fields,
            "changed_by": self.changed_by,
        }
