from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain.availability import OpeningTime
from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.clinical_code import (
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.domain.enums import (
    Gender,
    HealthcareServiceCategory,
    HealthcareServiceType,
    TimeUnit,
)
from pydantic import BaseModel


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
    identifier_oldDoS_uid: str | None = None
    active: bool
    category: HealthcareServiceCategory
    type: HealthcareServiceType
    providedBy: UUID | None
    location: UUID | None
    endpoint: list[UUID] | None
    name: str
    telecom: HealthcareServiceTelecom | None
    openingTime: list[OpeningTime] | None
    symptomGroupSymptomDiscriminators: list[SymptomGroupSymptomDiscriminatorPair]
    dispositions: list[str]
    ageEligibilityCriteria: list[AgeRangeType] | None = None
    genderEligibilityCriteria: list[Gender] | None = None
