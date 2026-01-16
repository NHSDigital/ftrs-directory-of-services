from enum import StrEnum

from pydantic import BaseModel


class AuditEventType(StrEnum):
    app = "app"
    user = "user"


class AuditEvent(BaseModel):
    type: AuditEventType
    value: str
    display: str
