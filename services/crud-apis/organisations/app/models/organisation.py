import re
from enum import Enum
from typing import Literal

from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.identifier import Identifier
from ftrs_common.fhir.operation_outcome import (
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.enums import OrganisationTypeCode
from ftrs_data_layer.logbase import CrudApisLogBase
from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

# Constants
IDENTIFIER_SYSTEM = "odsOrganisationCode"
IDENTIFIER_SEPARATOR = "|"
ODS_REGEX = r"^[A-Za-z0-9]{5,12}$"
ODS_SYSTEM_URL = "https://fhir.nhs.uk/Id/ods-organization-code"

# FHIR Extension URLs
TYPED_PERIOD_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
)
ORGANISATION_ROLE_URL = (
    "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
)
PERIOD_TYPE_SYSTEM = "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType"
LEGAL_PERIOD_CODE = "Legal"

# Error Messages
ERROR_IDENTIFIER_EMPTY = "at least one identifier must be provided"
ERROR_IDENTIFIER_NO_ODS_SYSTEM = (
    f"at least one identifier must have system '{ODS_SYSTEM_URL}'"
)
ERROR_IDENTIFIER_EMPTY_VALUE = "ODS identifier must have a non-empty value"
ERROR_IDENTIFIER_INVALID_FORMAT = (
    "invalid ODS code format: '{ods_code}' must follow format {ODS_REGEX}"
)
ACTIVE_EMPTY_ERROR = "Active field is required and cannot be null."

# Valid primary types (only these can be primary)
VALID_PRIMARY_TYPE_CODES = {
    OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
    OrganisationTypeCode.PHARMACY_ROLE_CODE,
}


PERMITTED_ROLE_COMBINATIONS = [
    {
        "primary": OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        "non_primary": [
            OrganisationTypeCode.GP_PRACTICE_ROLE_CODE,
            OrganisationTypeCode.OUT_OF_HOURS_ROLE_CODE,
            OrganisationTypeCode.WALK_IN_CENTRE_ROLE_CODE,
        ],
    },
    {"primary": OrganisationTypeCode.PHARMACY_ROLE_CODE, "non_primary": []},
]


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
    def validate_extensions(self) -> "OrganisationUpdatePayload":
        """Validate that extensions follow the required structure for various extensions."""
        if self.extension:
            role_codes: list[OrganisationTypeCode] = []

            for ext in self.extension:
                extracted_codes = _validate_organisation_extension(ext)
                role_codes.extend(extracted_codes)

            if role_codes:
                _validate_type_combination(role_codes)

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


def _validate_organisation_extension(ext: Extension) -> list[OrganisationTypeCode]:
    """
    Validate OrganisationRole extension contains required roleCode and TypedPeriod extensions.
    Returns list of role codes found in this extension.
    """
    if not ext.url or ext.url.strip() == "":
        _raise_validation_error(
            "Extension URL must be present and cannot be empty or None"
        )

    if ext.url != ORGANISATION_ROLE_URL:
        _raise_validation_error(f"Invalid extension URL: {ext.url}")

    if not ext.extension or len(ext.extension) == 0:
        _raise_validation_error(
            f"OrganisationRole extension with URL '{ORGANISATION_ROLE_URL}' must include a nested 'extension' array"
        )

    # Get roleCode and TypedPeriod extensions
    role_code_extensions = [
        e for e in ext.extension if hasattr(e, "url") and e.url and "roleCode" in e.url
    ]
    typed_period_extensions = [
        e
        for e in ext.extension
        if hasattr(e, "url") and e.url and TYPED_PERIOD_URL in e.url
    ]

    role_codes = _validate_role_code_extensions_present(role_code_extensions)

    if not typed_period_extensions:
        _raise_validation_error(
            "OrganisationRole extension must contain at least one TypedPeriod extension containing legal dates"
        )

    for typed_ext in typed_period_extensions:
        if _validate_typed_period_extension(typed_ext):
            break
        else:
            _raise_validation_error(
                "At least one Typed Period extension should have dateType as Legal"
            )

    return role_codes


def _validate_role_code_extensions_present(
    role_code_extensions: list[Extension],
) -> list[OrganisationTypeCode]:
    """
    Validate role code extensions are present and return the validated codes.
    """
    if not role_code_extensions:
        _raise_validation_error(
            "OrganisationRole extension must contain at least one roleCode extension"
        )

    role_codes: list[OrganisationTypeCode] = []
    for ext in role_code_extensions:
        role_code = _validate_role_code(ext)
        role_codes.append(role_code)

    return role_codes


def _validate_role_code(ext: Extension) -> OrganisationTypeCode:
    """
    Validate roleCode extension contains valid OrganisationTypeCode.
    Returns the validated OrganisationTypeCode.
    """
    if not ext.valueCodeableConcept:
        _raise_validation_error("roleCode must have a valueCodeableConcept")

    if not ext.valueCodeableConcept.coding:
        _raise_validation_error(
            "roleCode valueCodeableConcept must contain at least one coding"
        )

    role_code = ext.valueCodeableConcept.coding[0].code

    if not role_code:
        _raise_validation_error("roleCode coding must have a code value")

    try:
        return OrganisationTypeCode(role_code)
    except ValueError:
        _raise_validation_error(
            f"Invalid role code: '{role_code}'. Incorrect enum value"
        )


def _validate_typed_period_structure(ext: Extension) -> tuple[Extension, Extension]:
    """
    Validate basic TypedPeriod structure and return dateType and period extensions.
    """
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

    return date_type_ext, period_ext


def _validate_date_type_coding(date_type_ext: Extension) -> bool:
    """
    Validate dateType extension has correct coding system.
    """
    if not date_type_ext.valueCoding:
        _raise_validation_error("dateType must have a valueCoding")

    if date_type_ext.valueCoding.system != PERIOD_TYPE_SYSTEM:
        _raise_validation_error(f"dateType system must be '{PERIOD_TYPE_SYSTEM}'")

    return date_type_ext.valueCoding.code == LEGAL_PERIOD_CODE


def _validate_period_dates(period_ext: Extension, is_legal: bool) -> None:
    if not period_ext.valuePeriod:
        _raise_validation_error("TypedPeriod extension must have a valuePeriod")

    if is_legal:
        start = getattr(period_ext.valuePeriod, "start", None)
        end = getattr(period_ext.valuePeriod, "end", None)

        if not start:
            _raise_validation_error(
                "Legal period start date is required when TypedPeriod extension is present"
            )

        if start and end and start == end:
            logger = Logger.get(service="crud_organisation_logger")
            logger.log(
                CrudApisLogBase.ORGANISATION_023,
                date=start,
            )
            _raise_validation_error(
                "Legal period start and end dates must not be equal"
            )


def _validate_typed_period_extension(ext: Extension) -> bool:
    """
    Validate TypedPeriod extension structure and dates.
    """
    date_type_ext, period_ext = _validate_typed_period_structure(ext)
    is_legal = _validate_date_type_coding(date_type_ext)
    _validate_period_dates(period_ext, is_legal)
    return is_legal


def _validate_type_combination(codes: list[OrganisationTypeCode]) -> None:
    """
    Validate that a primary type and non-primary roles combination is permitted.

    Args:
        codes: List of all organization role codes to validate

    Raises:
        OperationOutcomeException if validation fails
    """
    # Separate primary and non-primary roles in a single pass
    primary_roles = [code for code in codes if code in VALID_PRIMARY_TYPE_CODES]
    non_primary_role_codes = [
        code for code in codes if code not in VALID_PRIMARY_TYPE_CODES
    ]

    # Validate primary role constraints
    if not primary_roles:
        _raise_validation_error("Primary role code must be provided")

    if len(primary_roles) > 1:
        _raise_validation_error("Only one primary role is allowed per organisation")

    primary_role_code = primary_roles[0]

    # Check for duplicate non-primary roles using set comparison
    if len(non_primary_role_codes) != len(set(non_primary_role_codes)):
        _raise_validation_error("Duplicate non-primary roles are not allowed")

    # Find permitted combination (cached lookup)
    permitted_combination = next(
        (
            combo
            for combo in PERMITTED_ROLE_COMBINATIONS
            if combo["primary"] == primary_role_code
        ),
        None,
    )

    if not permitted_combination:
        _raise_validation_error(
            f"Invalid primary role code: '{primary_role_code.value}'"
        )

    allowed_non_primary = set(permitted_combination["non_primary"])

    # Validate non-primary role requirements
    if allowed_non_primary:
        if not non_primary_role_codes:
            _raise_validation_error(
                f"{primary_role_code.value} must have at least one non-primary role"
            )

        # Check for invalid roles using set difference
        invalid_roles = set(non_primary_role_codes) - allowed_non_primary
        if invalid_roles:
            _raise_validation_error(
                f"Non-primary role '{next(iter(invalid_roles)).value}' is not permitted for primary type '{primary_role_code.value}'"
            )
    elif non_primary_role_codes:
        _raise_validation_error(
            f"{primary_role_code.value} cannot have non-primary roles"
        )
