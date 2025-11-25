from pydantic import field_validator

from organisations.app.models.organisation import (
    OrganisationCreatePayload,
    OrganisationUpdatePayload,
)

NAME_EMPTY_ERROR = "Name cannot be empty."
CREATED_BY_EMPTY_ERROR = "createdBy cannot be empty."
ODS_CODE_EMPTY_ERROR = "ODS code cannot be empty."
INVALID_ORG_TYPE_ERROR = "Invalid organization type: '{invalid_type}'."
INVALID_NON_PRIMARY_ROLE_ERROR = "Invalid non-primary role: '{invalid_role}'."


class UpdatePayloadValidator(OrganisationUpdatePayload):
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validates the name field to ensure it is not empty or whitespace."""
        if not v.strip():
            raise ValueError(NAME_EMPTY_ERROR)
        return v


class CreatePayloadValidator(OrganisationCreatePayload):
    @field_validator("createdBy")
    def validate_org_fields(cls, v: str) -> str:
        """Validates that created_by field is not empty."""
        if not v.strip():
            raise ValueError(CREATED_BY_EMPTY_ERROR)
        return v

    @field_validator("identifier_ODS_ODSCode")
    def validate_ods_code(cls, v: str) -> str:
        """Validates that the ODS code is not empty."""
        if not v.strip():
            raise ValueError(ODS_CODE_EMPTY_ERROR)
        return v
