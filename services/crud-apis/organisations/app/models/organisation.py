from typing import Literal

from fhir.resources.R4B.codeableconcept import CodeableConcept as Type
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from pydantic import BaseModel, Field, model_validator

ERROR_MESSAGE_TYPE = "'type' must have either 'coding' or 'text' populated."


class Organisation(BaseModel):
    """Internal organization model - simplified for database storage"""

    name: str = Field(..., example="GP Practice Name")
    active: bool = Field(..., example=True)
    telecom: str | None = Field(default=None, example="01234 567890")
    type: str = Field(default="GP Practice", example="GP Practice")


class OrganisationUpdatePayload(BaseModel):
    """FHIR-compliant Organization model for updates"""

    resourceType: Literal["Organization"] = Field(..., example="Organization")
    id: str = Field(..., example="00000000-0000-0000-0000-00000000000a")
    meta: dict = Field(
        ...,
        example={
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
    )
    identifier: list[Identifier] = Field(..., description="Organization identifiers")
    name: str = Field(max_length=100, example="GP Practice Name")
    active: bool = Field(..., example=True)
    type: list[Type] = Field(..., description="Organization type")
    telecom: list[ContactPoint] | None = None

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def check_type_coding_and_text(self) -> "OrganisationUpdatePayload":
        for t in self.type:
            if (not t.coding or len(t.coding) == 0) or (not t.text or t.text == ""):
                raise ValueError(ERROR_MESSAGE_TYPE)
        return self


class OrganisationCreatePayload(Organisation):
    id: str = Field(
        default_factory=lambda: "generated-uuid",
        example="d5a852ef-12c7-4014-b398-661716a63027",
    )
    identifier_ODS_ODSCode: str = Field(max_length=12, min_length=1, example="ABC123")
    createdBy: str = Field(
        max_length=100, min_length=1, example="ROBOT", pattern="^[a-zA-Z]+$"
    )
