from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain.auditevent import AuditEvent
from ftrs_data_layer.domain.base import DBModel, audit_default_value
from pydantic import BaseModel


class Address(BaseModel):
    line1: str | None
    line2: str | None
    county: str | None
    town: str | None
    postcode: str | None


class PositionGCS(BaseModel):
    latitude: Decimal
    longitude: Decimal


class Location(DBModel):
    identifier_oldDoS_uid: str | None = None
    active: bool
    address: Address
    managingOrganisation: UUID
    name: str | None = None
    positionGCS: PositionGCS | None = None
    positionReferenceNumber_UPRN: int | None = None
    positionReferenceNumber_UBRN: int | None = None
    primaryAddress: bool
    partOf: UUID | None = None
    createdBy: AuditEvent | None = audit_default_value
    modifiedBy: AuditEvent | None = audit_default_value
