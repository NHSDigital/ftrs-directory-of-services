from pydantic import BaseModel, Field


class Organisation(BaseModel):
    name: str = Field(min_length=1, max_length=100, example="Test Organisation")
    active: bool = Field(..., example=True)
    telecom: str | None = Field(max_length=20, example="0123456789")
    type: str = Field(min_length=1, max_length=100, example="GP Practice")


class OrganisationUpdatePayload(Organisation):
    modified_by: str = Field(max_length=100, min_length=1, example="ODS_ETL_PIPELINE")

    class Config:
        extra = "forbid"


class OrganisationCreatePayload(Organisation):
    id: str = Field(
        default_factory=lambda: "generated-uuid",
        example="d5a852ef-12c7-4014-b398-661716a63027",
    )
    identifier_ODS_ODSCode: str = Field(max_length=12, min_length=1, example="ABC123")
    createdBy: str = Field(
        max_length=100, min_length=1, example="ROBOT", pattern="^[a-zA-Z]+$"
    )
