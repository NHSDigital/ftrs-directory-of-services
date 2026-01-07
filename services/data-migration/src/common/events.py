from typing import Literal

from pydantic import BaseModel, field_validator


class DMSEvent(BaseModel):
    record_id: int
    service_id: int
    table_name: str
    method: Literal["insert", "update", "delete"]

    @field_validator("method")
    @classmethod
    def validate_method(cls, value: str) -> str:
        return value.lower()


class ReferenceDataLoadEvent(BaseModel):
    type: Literal["triagecode"]
