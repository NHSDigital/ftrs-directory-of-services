from enum import StrEnum

from pydantic import BaseModel


class AuditEventType(StrEnum):
    app = "app"
    user = "user"


class AuditEvent(BaseModel):
    type: AuditEventType
    value: str
    display: str


def default_data_migration_audit_event() -> AuditEvent:
    """Create a default audit event for inital data migration"""
    return AuditEvent(
        type=AuditEventType.app,
        value="ftrs-data-migration",  # TODO: FTRS-1524 what is the product ID of the data-migration application?
        display="Data Migration",
    )
