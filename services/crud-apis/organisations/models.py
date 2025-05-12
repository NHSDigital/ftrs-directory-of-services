from pydantic import BaseModel, Field


class OrganisationPayload(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "The name of the organisation",
        },
    )
    active: bool = Field(
        ...,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "If the service is active or not",
        },
    )
    telecom: str | None = Field(
        ...,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "If the service is active or not",
        },
    )
    type: str = Field(
        ...,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "If the service is active or not",
        },
    )
    modified_by: str = Field(
        ...,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "If the service is active or not",
        },
    )
