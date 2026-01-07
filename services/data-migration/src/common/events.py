from typing import Annotated, Literal

from pydantic import BaseModel, StringConstraints


class DMSEvent(BaseModel):
    record_id: int
    service_id: int
    table_name: str
    method: Annotated[
        Literal["insert", "update", "delete"],
        StringConstraints(to_lower=True),
    ]


class ReferenceDataLoadEvent(BaseModel):
    type: Literal["triagecode"]
