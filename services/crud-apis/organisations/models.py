from pydantic import BaseModel, Field


class OrganisationPayload(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra={
            "example": "Test Organisation",
            "description": "The name of the organisation",
        },
    )
