from typing import Optional
from uuid import UUID

from ftrs_data_layer.enums import HealthcareServiceCategory, HealthcareServiceType
from pydantic import BaseModel, EmailStr, Field


class TelecomDict(BaseModel):
    phone_private: Optional[str] = Field(
        None,
        pattern=r"^\+?[\d\s-]+$",  # Allows digits, spaces, hyphens, and optional + prefix
        min_length=6,
        max_length=20,
        example="99999 000000",
    )
    web: Optional[str] = Field(None, example="https://www.example.com/")
    email: Optional[EmailStr] = Field(None, example="testmail@example.com")
    phone_public: Optional[str] = Field(
        None,
        pattern=r"^\+?[\d\s-]+$",  # Allows digits, spaces, hyphens, and optional + prefix
        min_length=6,
        max_length=20,
        example="0208 883 5555",
    )


class HealthCareService(BaseModel):
    name: str = Field(min_length=1, max_length=100, example="GP Practice")
    active: bool = Field(..., example=True)
    telecom: TelecomDict = Field(
        default_factory=TelecomDict,
        example={
            "phone_private": "99999 000000",
            "web": "https://www.example.com/",
            "email": "testmail@example.com",
            "phone_public": "0208 883 5555",
        },
    )
    type: HealthcareServiceType = Field(
        examples=["Primary Care Network Enhanced Access Service"]
    )
    category: HealthcareServiceCategory = Field(examples=["GP Services"])
    identifier_oldDoS_id: Optional[int] = Field(
        None, min_length=1, max_length=12, example=161799
    )
    providedBy: Optional[UUID] = Field(
        None, example="96602abd-f265-4803-b4fb-413692279b5c"
    )
    location: Optional[UUID] = Field(
        None, example="e13b21b1-8859-4364-9efb-951d43cc8264"
    )
    openingTime: Optional[list[dict]] = Field(
        default_factory=list,
        example=[
            {
                "allDay": False,
                "startTime": "08:00:00",
                "id": "d3d11647-87a5-43f3-a602-62585b852875",
                "dayOfWeek": "mon",
                "endTime": "18:30:00",
                "category": "availableTime",
            }
        ],
    )


class HealthcareServiceCreatePayload(HealthCareService):
    id: Optional[UUID] = Field(None, example="d5a852ef-12c7-4014-b398-661716a63027")
    createdBy: str = Field(max_length=100, min_length=1, example="ROBOT")
