from uuid import UUID

from ftrs_data_layer.domain.enums import ClinicalCodeSource, ClinicalCodeType
from pydantic import BaseModel, Field

INVALID_DISPOSITION_ITEM = "Each disposition item must be a JSON object"
INVALID_SG_SD_PAIR = "Both 'sg' and 'sd' components are required in the pair"
INVALID_CODE_TYPE = "Invalid codeType for symptom group:"
INVALID_CODE_TYPE_SD = "Invalid codeType for symptom discriminator:"


class BaseClinicalCode(BaseModel):
    id: UUID
    source: ClinicalCodeSource | None = None
    codeType: ClinicalCodeType
    codeID: int | str = None
    codeValue: str | None = None


class SymptomGroup(BaseClinicalCode):
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
