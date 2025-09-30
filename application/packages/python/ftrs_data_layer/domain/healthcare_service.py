from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain.availability import OpeningTime
from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.clinical_code import (
    Disposition,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
    TimeUnit,
)
from pydantic import BaseModel, Field


class Telecom(BaseModel):
    phone_public: str | None
    phone_private: str | None
    email: str | None
    web: str | None


class AgeRange(BaseModel):
    rangeFrom: Decimal = Field(alias="from")
    rangeTo: Decimal = Field(alias="to")


class AgeRangeType(BaseModel):
    range: AgeRange
    type: TimeUnit


class HealthcareService(DBModel):
    identifier_oldDoS_uid: str | None = None
    active: bool
    category: HealthcareServiceCategory
    type: HealthcareServiceType
    providedBy: UUID | None
    location: UUID | None
    name: str
    telecom: Telecom | None
    openingTime: list[OpeningTime] | None
    symptomGroupSymptomDiscriminators: list[SymptomGroupSymptomDiscriminatorPair]
    dispositions: list[Disposition]
    migrationNotes: list[str] | None = None
    ageEligibilityCriteria: list[AgeRangeType] | None = None
