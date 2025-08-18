# from fhir.resources.R4B.codeableconcept import CodeableConcept
from pydantic import field_validator

from organisations.app.models.organisation import (
    OrganisationCreatePayload,
    OrganisationUpdatePayload,
)

NAME_EMPTY_ERROR = "Name cannot be empty."
CREATED_BY_EMPTY_ERROR = "createdBy cannot be empty."
ODS_CODE_EMPTY_ERROR = "ODS code cannot be empty."
# ORG_TYPE_INVALID_ERROR = "Organisation type is invalid."


class UpdatePayloadValidator(OrganisationUpdatePayload):
    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        """Validates the name field to ensure it is not empty or whitespace."""
        if not v.strip():
            raise ValueError(NAME_EMPTY_ERROR)
        return v

    # @field_validator("type")
    # def validate_organisation_type(cls, v: list) -> list:
    #     """Validates the Organisation Type field to ensure it is a valid type."""
    #     if not v:
    #         raise ValueError(ORG_TYPE_INVALID_ERROR)
    #     if isinstance(v, list):
    #         if len(v) == 0:
    #             raise ValueError(ORG_TYPE_INVALID_ERROR)
    #         for item in v:
    #             if isinstance(item, CodeableConcept):
    #                 # will need to change to either codings or text eventually
    #                 display = getattr(item, "text", None)
    #                 if display:
    #                     return v
    #                 codings = getattr(item, "coding", None)
    #                 return validate_coding(codings)
    #         raise ValueError(ORG_TYPE_INVALID_ERROR)
    #     raise ValueError(ORG_TYPE_INVALID_ERROR)


# def validate_coding(codings: list)-> list:
#      if codings:
#         for coding in codings:
#             code = getattr(coding, "code", None)
#             if code:
#                 return codings


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
