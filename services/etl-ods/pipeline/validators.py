import logging
from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, ValidationError, model_validator

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MAX_ODS_TEL_LENGTH = 20


class StatusEnum(str, Enum):
    active = "Active"
    inactive = "Inactive"


class ContactTypeEnum(str, Enum):
    tel = "tel"


class ContactItem(BaseModel):
    """
    Validator class for ODS contact item data
    """

    type: ContactTypeEnum = Field(..., description="Type of contact (e.g., 'tel').")
    value: str = Field(
        ..., description="Value of the contact (e.g., telephone number)."
    )

    @model_validator(mode="before")
    def strip_whitespace(cls, values: dict) -> dict:
        if isinstance(values, dict) and "value" in values:
            values["value"] = values["value"].replace(" ", "")
        return values

    @model_validator(mode="after")
    def validate_value_length(self) -> Self:
        if self.type == "tel" and len(self.value) > MAX_ODS_TEL_LENGTH:
            raise ValueError("20")
        return self


class RoleItem(BaseModel):
    """
    Validator class for Role item data
    """

    id: str = Field(
        max_length=10, description="Role ID from lookup via OrganisationRole CodeSystem"
    )
    primaryRole: bool = Field(
        default=False,
        description="If the role is the primary one for the organisation.",
    )


class RoleList(BaseModel):
    Role: list[RoleItem] = Field(
        None, description="List of roles associated with the organisation."
    )


class OrganisationValidator(BaseModel):
    """
    Validator class for ingested organisation data.
    """

    Name: str = Field(max_length=100, description="The name of the organisation.")
    Status: StatusEnum = Field(..., description="If the service is active or not.")
    Roles: RoleList = Field(
        ..., description="List of roles associated with the organisation."
    )
    Contact: ContactItem | None = Field(
        ..., description="Telephone contact associated with the organisation."
    )


class RolesValidator(BaseModel):
    """
    Validator class for ingested roles data.
    """

    displayName: str = Field(max_length=100, description="Display name of the role.")


def validate_payload(payload: dict, model: BaseModel) -> dict:
    try:
        return model(**payload)
    except ValidationError as e:
        logger.warning(f"Payload validation failed: {e}")
        raise
