import json
from enum import Enum

import numpy as np
from pydantic import BaseModel
from uuid import UUID
from sqlmodel import Field

INVALID_DISPOSITION_ITEM = "Each disposition item must be a JSON object"
INVALID_SG_SD_PAIR = "Both 'sg' and 'sd' components are required in the pair"
INVALID_CODE_TYPE = "Invalid codeType for symptom group:"
INVALID_CODE_TYPE_SD = "Invalid codeType for symptom discriminator:"


class ClinicalCodeSource(str, Enum):
    PATHWAYS = "pathways"
    SERVICE_FINDER = "servicefinder"


class ClinicalCodeType(str, Enum):
    SYMPTOM_GROUP = "Symptom Group (SG)"
    SYMPTOM_DISCRIMINATOR = "Symptom Discriminator (SD)"
    DISPOSITION = "Disposition (Dx)"


class BaseClinicalCode(BaseModel):
    id: UUID
    source: ClinicalCodeSource
    codeType: ClinicalCodeType
    codeID: int | str
    codeValue: str | None


class SymptomGroup(BaseClinicalCode):
    codeType: ClinicalCodeType = ClinicalCodeType.SYMPTOM_GROUP


class SymptomDiscriminator(BaseClinicalCode):
    codeType: ClinicalCodeType = ClinicalCodeType.SYMPTOM_GROUP


class SymptomDiscriminator(BaseClinicalCode):
    codeType: ClinicalCodeType = ClinicalCodeType.SYMPTOM_DISCRIMINATOR
    synonyms: list[str] = Field(default_factory=list)


class Disposition(BaseClinicalCode):
    codeType: ClinicalCodeType = ClinicalCodeType.DISPOSITION
    time: int | None = 0


class SymptomGroupSymptomDiscriminatorPair(BaseModel):
    sg: SymptomGroup
    sd: SymptomDiscriminator
