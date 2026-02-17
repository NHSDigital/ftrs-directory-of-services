from uuid import UUID

from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from pydantic import BaseModel, EmailStr, Field


class TelecomDict(BaseModel):
    phone_private: str | None = Field(
        None,
        pattern=r"^\+?[\d\s-]+$",  # Allows digits, spaces, hyphens, and optional + prefix
        min_length=6,
        max_length=20,
        json_schema_extra={
            "example": "99999 000000",
        },
    )
    web: str | None = Field(
        None, json_schema_extra={"example": "https://www.example.com/"}
    )
    email: EmailStr | None = Field(
        None, json_schema_extra={"example": "testmail@example.com"}
    )
    phone_public: str | None = Field(
        None,
        pattern=r"^\+?[\d\s-]+$",  # Allows digits, spaces, hyphens, and optional + prefix
        min_length=6,
        max_length=20,
        json_schema_extra={
            "example": "0208 883 5555",
        },
    )


class HealthCareService(BaseModel):
    name: str = Field(
        min_length=1, max_length=100, json_schema_extra={"example": "GP Practice"}
    )
    active: bool = Field(..., json_schema_extra={"example": True})
    telecom: TelecomDict = Field(
        default_factory=TelecomDict,
        json_schema_extra={
            "example": {
                "phone_private": "99999 000000",
                "web": "https://www.example.com/",
                "email": "testmail@example.com",
                "phone_public": "0208 883 5555",
            },
        },
    )
    type: HealthcareServiceType = Field(
        json_schema_extra={"examples": ["Primary Care Network Enhanced Access Service"]}
    )
    category: HealthcareServiceCategory = Field(
        json_schema_extra={"examples": ["GP Services"]}
    )
    identifier_oldDoS_id: int | None = Field(
        None,
        min_length=1,
        max_length=12,
        json_schema_extra={"example": 161799},
    )
    providedBy: UUID | None = Field(
        None, json_schema_extra={"example": "96602abd-f265-4803-b4fb-413692279b5c"}
    )
    location: UUID | None = Field(
        None, json_schema_extra={"example": "e13b21b1-8859-4364-9efb-951d43cc8264"}
    )
    openingTime: list[dict] | None = Field(
        default_factory=list,
        json_schema_extra={
            "example": [
                {
                    "allDay": False,
                    "startTime": "08:00:00",
                    "id": "d3d11647-87a5-43f3-a602-62585b852875",
                    "dayOfWeek": "mon",
                    "endTime": "18:30:00",
                    "category": "availableTime",
                }
            ]
        },
    )
    symptomGroupSymptomDiscriminators: list[dict] | None = Field(
        default_factory=list,
        json_schema_extra={"example": []},
    )
    dispositions: list[dict] | None = Field(
        default_factory=list,
        json_schema_extra={"example": []},
    )


class HealthcareServiceCreatePayload(HealthCareService):
    id: UUID | None = Field(
        None, json_schema_extra={"example": "d5a852ef-12c7-4014-b398-661716a63027"}
    )
