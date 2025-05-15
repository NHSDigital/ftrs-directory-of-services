from pydantic import field_validator

from organisations.models import OrganisationPayload

NAME_EMPTY_ERROR = "Name cannot be empty."


class UpdatePayloadValidator(OrganisationPayload):
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validates the name field to ensure it is not empty or whitespace."""
        if not v.strip():
            raise ValueError(NAME_EMPTY_ERROR)
        return v
