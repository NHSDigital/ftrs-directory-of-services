from ftrs_data_layer.domain.enums import TelecomType
from pydantic import BaseModel, Field


class Telecom(BaseModel):
    type: TelecomType = Field(frozen=True)
    value: str
    isPublic: bool
