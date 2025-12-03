from datetime import date

from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import OrganisationType
from pydantic import BaseModel, Field


class LegalDates(BaseModel):
    start: date | None = None
    end: date | None = None


class Organisation(DBModel):
    identifier_ODS_ODSCode: str
    active: bool
    name: str
    telecom: str | None = None
    type: OrganisationType | str
    endpoints: list["Endpoint"] = Field(default_factory=list)
    legalDates: LegalDates | None = None
