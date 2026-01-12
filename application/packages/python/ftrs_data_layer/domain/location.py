from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain.audit_event import (
    AuditEvent,
    default_data_migration_audit_event,
)
from ftrs_data_layer.domain.base import DBModel
from pydantic import BaseModel, Field


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
    createdBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
    createdTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modifiedBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
    modifiedTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lastUpdatedBy: AuditEvent = Field(
        default_factory=default_data_migration_audit_event
    )
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
