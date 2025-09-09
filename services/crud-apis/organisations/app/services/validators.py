from pydantic import field_validator

from organisations.app.models.organisation import (
    OrganisationCreatePayload,
    OrganisationUpdatePayload,
)

NAME_EMPTY_ERROR = "Name cannot be empty."
NAME_MAX_LENGTH_ERROR = "Name cannot be longer than 100 characters."
CREATED_BY_EMPTY_ERROR = "createdBy cannot be empty."
ODS_CODE_EMPTY_ERROR = "ODS code cannot be empty."

NAME_MAX_LENGTH = 100


class UpdatePayloadValidator(OrganisationUpdatePayload):
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validates the name field to ensure it is not empty or whitespace.
        Checks the length of the field."""
        if not v.strip():
            raise ValueError(NAME_EMPTY_ERROR)
        if len(v.strip()) > NAME_MAX_LENGTH:
            raise ValueError(NAME_MAX_LENGTH_ERROR)
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
