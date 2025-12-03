from datetime import date

from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.endpoint import Endpoint
from ftrs_data_layer.domain.enums import OrganisationType, OrganisationTypeCode
from pydantic import Field
from pydantic import BaseModel, Field


class LegalDates(BaseModel):
    start: date | None = None
    end: date | None = None


class Organisation(DBModel):
    identifier_ODS_ODSCode: str
    active: bool
    name: str
    telecom: str | None = None
    type: OrganisationType | str | None = None
    primary_role_code: OrganisationTypeCode | str | None = None
    non_primary_role_codes: list[OrganisationTypeCode | str] = Field(
        default_factory=list
    )
    endpoints: list["Endpoint"] = Field(default_factory=list)
    legalDates: LegalDates | None = None
