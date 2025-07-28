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
)
from pydantic import BaseModel


class Telecom(BaseModel):
    phone_public: str | None
    phone_private: str | None
    email: str | None
    web: str | None


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
