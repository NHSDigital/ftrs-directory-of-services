from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain.audit_event import (
    AuditEvent,
    default_data_migration_audit_event,
)
from ftrs_data_layer.domain.availability import OpeningTime
from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.clinical_code import (
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
    TimeUnit,
)
from pydantic import BaseModel, Field


class HealthcareServiceTelecom(BaseModel):
    phone_public: str | None
    phone_private: str | None
    email: str | None
    web: str | None


class AgeRangeType(BaseModel):
    rangeFrom: Decimal
    rangeTo: Decimal
    type: TimeUnit


class HealthcareService(DBModel):
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
    category: HealthcareServiceCategory
    type: HealthcareServiceType
    providedBy: UUID | None
    location: UUID | None
    name: str
    telecom: HealthcareServiceTelecom | None
    openingTime: list[OpeningTime] | None
    symptomGroupSymptomDiscriminators: list[SymptomGroupSymptomDiscriminatorPair]
    dispositions: list[str]
    migrationNotes: list[str] | None = None
    ageEligibilityCriteria: list[AgeRangeType] | None = None
