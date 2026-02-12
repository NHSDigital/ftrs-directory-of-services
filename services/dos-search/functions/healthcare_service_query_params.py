import re

from pydantic import BaseModel, Field, computed_field, field_validator


class InvalidIdentifierSystem(ValueError):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            f"Invalid identifier system '{identifier}' - expected '{IDENTIFIER_SYSTEM}'"
        )


class ODSCodeInvalidFormatError(ValueError):
    def __init__(self, ods_code: str) -> None:
        super().__init__(
            f"Invalid identifier value: ODS code '{ods_code}' must follow format {ODS_REGEX}"
        )


IDENTIFIER_SYSTEM = "odsOrganisationCode"
IDENTIFIER_SEPERATOR = "|"
ODS_REGEX = r"^[A-Za-z0-9]{5,12}$"


def _extract_identifier_system(identifier: str) -> str:
    return (
        identifier.split(IDENTIFIER_SEPERATOR, 1)[0]
        if IDENTIFIER_SEPERATOR in identifier
        else ""
    )


def _extract_identifier_value(identifier: str) -> str:
    return (
        identifier.split(IDENTIFIER_SEPERATOR, 1)[1].upper()
        if IDENTIFIER_SEPERATOR in identifier
        else ""
    )


class HealthcareServiceQueryParams(BaseModel):
    identifier: str = Field(
        description="HealthcareService identifier in format 'odsOrganisationCode|{code}'",
    )

    model_config = {"extra": "forbid"}

    @computed_field
    @property
    def ods_code(self) -> str:
        return _extract_identifier_value(self.identifier)

    # noinspection PyNestedDecorators
    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        identifier_system = _extract_identifier_system(v)

        if identifier_system != IDENTIFIER_SYSTEM:
            raise InvalidIdentifierSystem(identifier_system)

        identifier_value = _extract_identifier_value(v)

        if not re.match(ODS_REGEX, identifier_value):
            raise ODSCodeInvalidFormatError(identifier_value)

        return v
