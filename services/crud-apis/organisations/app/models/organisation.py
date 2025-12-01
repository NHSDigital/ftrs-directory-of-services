import re
from enum import Enum
from typing import Literal

from fhir.resources.R4B.codeableconcept import CodeableConcept as Type
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.identifier import Identifier
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import CrudApisLogBase
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

IDENTIFIER_SYSTEM = "odsOrganisationCode"
IDENTIFIER_SEPARATOR = "|"
ODS_REGEX = r"^[A-Za-z0-9]{5,12}$"

ERROR_MESSAGE_TYPE = "'type' must have either 'coding' or 'text' populated."
ERROR_IDENTIFIER_EMPTY = "at least one identifier must be provided"
ERROR_IDENTIFIER_NO_ODS_SYSTEM = "at least one identifier must have system 'https://fhir.nhs.uk/Id/ods-organization-code'"
ERROR_IDENTIFIER_EMPTY_VALUE = "ODS identifier must have a non-empty value"
ERROR_IDENTIFIER_INVALID_FORMAT = (
    "invalid ODS code format: '{ods_code}' must follow format {ODS_REGEX}"
)
ACTIVE_EMPTY_ERROR = "Active field is required and cannot be null."
TYPED_PERIOD_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
)
ORGANISATION_ROLE_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
)
PERIOD_TYPE_SYSTEM = "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType"
LEGAL_PERIOD_CODE = "Legal"


class LegalDateField(Enum):
    START = "start"
    END = "end"


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
    extension: list[Extension] | None = None

    model_config = {"extra": "forbid"}

    @field_validator("identifier", mode="before")
    @classmethod
    def validate_identifier_list(cls, v: list[dict]) -> list[dict]:
        if not v:
            raise ValueError(ERROR_IDENTIFIER_EMPTY)

        ods_identifiers = [
            identifier
            for identifier in v
            if isinstance(identifier, dict)
            and identifier.get("system")
            == "https://fhir.nhs.uk/Id/ods-organization-code"
        ]

        if not ods_identifiers:
            raise ValueError(ERROR_IDENTIFIER_NO_ODS_SYSTEM)

        for identifier in ods_identifiers:
            if not identifier.get("value") or not identifier.get("value").strip():
                raise ValueError(ERROR_IDENTIFIER_EMPTY_VALUE)

            ods_code = identifier.get("value", "").strip()
            if not re.match(ODS_REGEX, ods_code):
                raise ValueError(
                    ERROR_IDENTIFIER_INVALID_FORMAT.format(
                        ods_code=ods_code, ODS_REGEX=ODS_REGEX
                    )
                )

        return v

    @field_validator("active", mode="before")
    @classmethod
    def validate_active_not_null(cls, v: bool | None) -> bool:
        """Validates that active field is not None/null."""
        if v is None:
            Logger.get(service="crud_organisation_logger").log(
                CrudApisLogBase.ORGANISATION_022
            )
            raise ValueError(ACTIVE_EMPTY_ERROR)
        return v

    @model_validator(mode="after")
    def check_type_coding_and_text(self) -> "OrganisationUpdatePayload":
        for t in self.type:
            if (not t.coding or len(t.coding) == 0) and (not t.text or t.text == ""):
                raise ValueError(ERROR_MESSAGE_TYPE)
            if t.coding and (not t.coding[0].code or t.coding[0].code == ""):
                raise ValueError(ERROR_MESSAGE_TYPE)
        return self

    @model_validator(mode="after")
    def validate_extensions(self) -> "OrganisationUpdatePayload":
        """Validate that extensions follow the required structure for Legal dates."""
        if self.extension:
            for ext in self.extension:
                _validate_organisation_extension(ext)
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


def _raise_validation_error(message: str) -> None:
    """Helper to raise validation errors with consistent OperationOutcome formatting."""
    outcome = OperationOutcomeHandler.build(
        diagnostics=message,
        code="invalid",
        severity="error",
    )
    raise OperationOutcomeException(outcome)


def _validate_organisation_extension(ext: Extension) -> None:
    """Validate OrganisationRole extensions containing TypedPeriod extensions."""
    if not ext.url or ext.url.strip() == "":
        _raise_validation_error("Extension URL cannot be empty or None")
    elif ext.url == ORGANISATION_ROLE_URL:
        # Validate OrganisationRole extension structure
        _validate_organisation_role_extension(ext)
    elif ext.url == TYPED_PERIOD_URL:
        # Handle legacy direct TypedPeriod extensions (if still allowed)
        _validate_typed_period_extension(ext)
    else:
        _raise_validation_error(f"Invalid extension URL: {ext.url}")


def _validate_organisation_role_extension(ext: Extension) -> None:
    """Validate OrganisationRole extension containing the first Legal TypedPeriod extension."""
    if not ext.extension or len(ext.extension) == 0:
        _raise_validation_error(
            f"OrganisationRole extension with URL '{ORGANISATION_ROLE_URL}' must include a nested 'extension' array"
        )

    for nested_ext in ext.extension:
        if "TypedPeriod" in nested_ext.url:
            _validate_typed_period_extension(nested_ext)
            break  # Only validate the first TypedPeriod-like extension


def _validate_typed_period_extension(ext: Extension) -> None:
    """Validate TypedPeriod extension with Legal dateType."""
    if ext.url != TYPED_PERIOD_URL:
        _raise_validation_error(f"Invalid extension URL: {ext.url}")

    if not ext.extension or len(ext.extension) == 0:
        _raise_validation_error(
            f"TypedPeriod extension with URL '{TYPED_PERIOD_URL}' must include a nested 'extension' array with 'dateType' and 'period' fields"
        )

    date_type_ext = next((e for e in ext.extension if e.url == "dateType"), None)
    period_ext = next((e for e in ext.extension if e.url == "period"), None)

    if not date_type_ext or not period_ext:
        _raise_validation_error(
            "TypedPeriod extension must contain dateType and period"
        )

    if not date_type_ext.valueCoding:
        _raise_validation_error("dateType must have a valueCoding")

    if date_type_ext.valueCoding.system != PERIOD_TYPE_SYSTEM:
        _raise_validation_error(f"dateType system must be '{PERIOD_TYPE_SYSTEM}'")

    if date_type_ext.valueCoding.code != LEGAL_PERIOD_CODE:
        _raise_validation_error("dateType must be Legal")

    if not period_ext.valuePeriod or (
        not period_ext.valuePeriod.start and not period_ext.valuePeriod.end
    ):
        _raise_validation_error("period must contain at least start or end date")

    start = getattr(period_ext.valuePeriod, "start", None)
    end = getattr(period_ext.valuePeriod, "end", None)
    if start and end and start == end:
        logger = Logger.get(service="crud_organisation_logger")
        logger.log(
            CrudApisLogBase.ORGANISATION_023,
            date=start,
        )
        _raise_validation_error("Legal period start and end dates must not be equal")
