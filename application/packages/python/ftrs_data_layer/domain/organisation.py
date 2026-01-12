from datetime import UTC, date, datetime

from ftrs_data_layer.domain.audit_event import (
    AuditEvent,
    default_data_migration_audit_event,
)
from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import OrganisationType, OrganisationTypeCode
from ftrs_data_layer.domain.telecom import Telecom
from pydantic import BaseModel, Field


class LegalDates(BaseModel):
    start: date | None = None
    end: date | None = None


class Organisation(DBModel):
    createdBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
    createdTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modifiedBy: AuditEvent = Field(default_factory=default_data_migration_audit_event)
    modifiedTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    lastUpdatedBy: AuditEvent = Field(
        default_factory=default_data_migration_audit_event
    )
    identifier_oldDoS_uid: str | None = None
    identifier_ODS_ODSCode: str
    active: bool
    name: str
    type: OrganisationType | str | None = None
    primary_role_code: OrganisationTypeCode | str | None = None
    non_primary_role_codes: list[OrganisationTypeCode | str] = Field(
        default_factory=list
    )
    telecom: list[Telecom] | str | None
    endpoints: list["Endpoint"] = Field(default_factory=list)
    legalDates: LegalDates | None = None
