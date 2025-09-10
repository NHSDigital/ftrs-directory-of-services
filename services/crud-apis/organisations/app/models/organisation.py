import re
from typing import Literal

from fhir.resources.R4B.codeableconcept import CodeableConcept as Type
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.identifier import Identifier
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

IDENTIFIER_SYSTEM = "odsOrganisationCode"
IDENTIFIER_SEPARATOR = "|"
ODS_REGEX = r"^[A-Za-z0-9]{5,12}$"
ERROR_MESSAGE_TYPE = "'type' must have either 'coding' or 'text' populated."


class OrganizationQueryParams(BaseModel):
    identifier: str = Field(
        ...,
        description="Organization identifier in format 'odsOrganisationCode|{code}'",
    )

    @computed_field
    @property
    def ods_code(self) -> str:
        """Returns the ODS code portion of the identifier."""
        return _extract_identifier_value(self.identifier)

    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if IDENTIFIER_SEPARATOR not in v:
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Invalid identifier value: missing separator '{IDENTIFIER_SEPARATOR}'. Must be in format '{IDENTIFIER_SYSTEM}|<code>' and code must follow format {ODS_REGEX}",
                code="invalid",
                severity="error",
            )
            raise OperationOutcomeException(outcome)
        identifier_system = _extract_identifier_system(v)
        if identifier_system != IDENTIFIER_SYSTEM:
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Invalid identifier system '{identifier_system}' - expected '{IDENTIFIER_SYSTEM}'",
                code="invalid",
                severity="error",
            )
            raise OperationOutcomeException(outcome)
        identifier_value = _extract_identifier_value(v)
        if not re.match(ODS_REGEX, identifier_value):
            outcome = OperationOutcomeHandler.build(
                diagnostics=f"Invalid identifier value: ODS code '{identifier_value}' must follow format {ODS_REGEX}",
                code="invalid",
                severity="error",
            )
            raise OperationOutcomeException(outcome)
        return v


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
            if (not t.coding or len(t.coding) == 0) and (not t.text or t.text == ""):
                raise ValueError(ERROR_MESSAGE_TYPE)
            if t.coding and (not t.coding[0].code or t.coding[0].code == ""):
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


def _extract_identifier_system(identifier: str) -> str:
    """Extracts the system part from an identifier string."""
    return (
        identifier.split(IDENTIFIER_SEPARATOR, 1)[0]
        if IDENTIFIER_SEPARATOR in identifier
        else ""
    )


def _extract_identifier_value(identifier: str) -> str:
    """Extracts the value part from an identifier string and uppercases it."""
    return (
        identifier.split(IDENTIFIER_SEPARATOR, 1)[1].upper()
        if IDENTIFIER_SEPARATOR in identifier
        else ""
    )
