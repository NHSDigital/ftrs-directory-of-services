from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.domain.clinical_code import BaseClinicalCode
from pydantic import Field


class TriageCode(BaseClinicalCode, DBModel):
    field: str | None = "item"
    synonyms: list[str] = Field(default_factory=list)
    time: int | None = 0
    zCodeExists: bool | None
    combinations: list[str] = Field(default_factory=list)
    dx_group_ids: list[int] = Field(default_factory=list)
