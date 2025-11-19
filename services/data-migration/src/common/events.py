from typing import Literal

from pydantic import BaseModel


class DMSEvent(BaseModel):
    type: Literal["dms_event"] = "dms_event"
    record_id: int
    table_name: str
    method: str


class ReferenceDataLoadEvent(BaseModel):
    type: Literal["triagecode"]
