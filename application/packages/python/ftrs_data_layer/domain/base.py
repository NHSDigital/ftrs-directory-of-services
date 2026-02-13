from datetime import UTC, datetime
from uuid import UUID, uuid4

from ftrs_data_layer.domain.auditevent import AuditEvent, AuditEventType
from pydantic import BaseModel, Field

# TODO: Remove this once ingress API changes are made
audit_default_value = AuditEvent(
    type=AuditEventType.app, value="SYSTEM", display="SYSTEM"
)


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID = Field(default_factory=uuid4)
    created: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    createdBy: AuditEvent = audit_default_value
    lastUpdatedBy: AuditEvent = audit_default_value
