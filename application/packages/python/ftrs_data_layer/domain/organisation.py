from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import OrganisationType
from pydantic import Field


class Organisation(DBModel):
    identifier_ODS_ODSCode: str
    active: bool
    name: str
    telecom: str | None = None
    type: OrganisationType | str
    endpoints: list["Endpoint"] = Field(default_factory=list)
    legal_start_date: str | None = None
    legal_end_date: str | None = None
