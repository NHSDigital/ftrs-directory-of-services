from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.domain.clinical_code import BaseClinicalCode
from pydantic import BaseModel, Field


class TriageCodeCombination(BaseModel):
    value: str
    id: str


class TriageCode(BaseClinicalCode, DBModel):
    id: str
    field: str | None = "item"
    synonyms: list[str] = Field(default_factory=list)
    time: int | None = 0
    zCodeExists: bool | None = False
    combinations: list[TriageCodeCombination] = Field(default_factory=list)
    dx_group_ids: list[int] = Field(default_factory=list)
