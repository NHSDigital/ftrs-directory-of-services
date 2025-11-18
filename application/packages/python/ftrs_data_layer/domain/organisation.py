from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import OrganisationType
from pydantic import Field


class Organisation(DBModel):
    identifier_ODS_ODSCode: str
    active: bool | None = None
    name: str
    telecom: str | None = None
    type: OrganisationType | str
    endpoints: list["Endpoint"] = Field(default_factory=list)
