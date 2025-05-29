from pydantic import BaseModel, Field


class OrganisationPayload(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "The name of the organisation",
        },
    )
    active: bool = Field(
        ...,
        json_schema_extra={
            "example": "false",
            "description": "If the service is active or not",
        },
    )
    telecom: str | None = Field(
        max_length=20,
        json_schema_extra={
            "example": "0123456789",
            "description": "The telecom number of the organisation",
        },
    )
    type: str = Field(
        min_length=1,
        max_length=100,
        json_schema_extra={
            "example": "GP Practice",
            "description": "The type of the organisation",
        },
    )
    modified_by: str = Field(
        max_length=100,
        min_length=1,
        json_schema_extra={
            "example": "ODS_ETL_PIPELINE",
            "description": "Who modified the record",
        },
    )

    class Config:
        extra = "forbid"
