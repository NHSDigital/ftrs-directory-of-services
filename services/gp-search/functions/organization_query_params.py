import re

from pydantic import BaseModel, Field, computed_field, field_validator


class InvalidIdentifierPrefixError(ValueError):
    def __init__(self) -> None:
        super().__init__("Identifier must start with 'odsOrganisationCode|'")


class ODSCodeTooShortError(ValueError):
    def __init__(self) -> None:
        super().__init__("ODS code must be at least 5 characters long")


class ODSCodeTooLongError(ValueError):
    def __init__(self) -> None:
        super().__init__("ODS code must be at most 12 characters long")


class ODSCodeInvalidFormatError(ValueError):
    def __init__(self) -> None:
        super().__init__("ODS code must contain only letters and numbers")


class InvalidRevincludeError(ValueError):
    def __init__(self) -> None:
        super().__init__("_revinclude should be 'Endpoint:organization'")


IDENTIFIER_PREFIX = "odsOrganisationCode|"
ODS_MIN_LENGTH = 5
ODS_MAX_LENGTH = 12
ODS_REGEX = r"^[A-Za-z0-9]+$"


def _extract_ods_code(identifier: str) -> str:
    return identifier.split("|", 1)[1].upper() if "|" in identifier else ""


class OrganizationQueryParams(BaseModel):
    identifier: str = Field(
        description="Organization identifier in format 'odsOrganisationCode|{code}'"
    )
    revinclude: str = Field(
        alias="_revinclude", description="Optional revinclude parameter"
    )

    @computed_field
    @property
    def ods_code(self) -> str:
        return _extract_ods_code(self.identifier)

    # noinspection PyNestedDecorators
    @field_validator("identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not v.startswith(IDENTIFIER_PREFIX):
            raise InvalidIdentifierPrefixError

        ods_code = _extract_ods_code(v)

        if len(ods_code) < ODS_MIN_LENGTH:
            raise ODSCodeTooShortError
        if len(ods_code) > ODS_MAX_LENGTH:
            raise ODSCodeTooLongError
        if not re.match(ODS_REGEX, ods_code):
            raise ODSCodeInvalidFormatError

        return v

    # noinspection PyNestedDecorators
    @field_validator("revinclude")
    @classmethod
    def validate_revinclude(cls, v: str) -> str:
        if v != "Endpoint:organization":
            raise InvalidRevincludeError
        return v
