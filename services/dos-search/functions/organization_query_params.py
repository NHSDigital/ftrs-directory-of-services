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


class InvalidRevincludeError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
        )


IDENTIFIER_SYSTEM = "odsOrganisationCode"
IDENTIFIER_SEPERATOR = "|"
ODS_REGEX = r"^[A-Za-z0-9]{5,12}$"
REVINCLUDE_VALUE = "Endpoint:organization"


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


class OrganizationQueryParams(BaseModel):
    identifier: str = Field(
        description="Organization identifier in format 'odsOrganisationCode|{code}'",
    )
    revinclude: str = Field(alias="_revinclude")

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

    # noinspection PyNestedDecorators
    @field_validator("revinclude")
    @classmethod
    def validate_revinclude(cls, v: str) -> str:
        if v != REVINCLUDE_VALUE:
            raise InvalidRevincludeError
        return v
