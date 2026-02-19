from typing import Any, Dict

from ftrs_data_layer.domain.auditevent import AuditEvent
from pydantic import BaseModel, Field


class VersionHistory(BaseModel):
    """
    Model for version history entries that track changes to Organisation,
    Location, and HealthcareService records.

    The entity_id follows the format: {entity_name}|{record_id}|{field_name}
    The timestamp is in ISO8601 format with Z suffix (e.g., "2026-02-17T10:00:00Z")
    """

    entity_id: str = Field(
        ...,
        description="Composite identifier: {entity_name}|{record_id}|{field_name}",
    )
    timestamp: str = Field(
        ...,
        description="ISO8601 timestamp with Z suffix indicating when the change occurred",
    )
    change_type: str = Field(
        ...,
        description="Type of change: UPDATE, CREATE, or DELETE",
    )
    changed_fields: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dictionary mapping field names to {old: ..., new: ...} values",
    )
    changed_by: AuditEvent = Field(
        ...,
        description="AuditEvent indicating who/what made the change",
    )
