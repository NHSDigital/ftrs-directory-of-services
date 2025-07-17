from datetime import UTC, date, datetime, time
from decimal import Decimal
from typing import Annotated, Literal, Optional, Union
from uuid import UUID, uuid4
import ftrs_data_layer.legacy_model as legacy_model

from ftrs_data_layer.domain.clinical_code import (
    ClinicalCodeConverter,
    Disposition,
    SymptomGroupSymptomDiscriminatorPair,
)
from ftrs_data_layer.enums import (
    DayOfWeek,
    EndpointConnectionType,
    EndpointDescription,
    EndpointPayloadMimeType,
    EndpointPayloadType,
    EndpointStatus,
    HealthcareServiceCategory,
    HealthcareServiceType,
    OpeningTimeCategory,
    OrganisationType,
)
from pydantic import BaseModel, Field, ConfigDict


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID = Field(default_factory=uuid4)
    createdBy: str | None = "SYSTEM"
    createdDateTime: datetime = Field(default_factory=lambda: datetime.now(UTC))
    modifiedBy: str | None = "SYSTEM"
    modifiedDateTime: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Organisation(DBModel):
    identifier_ODS_ODSCode: str | None = None
    active: bool
    name: str
    telecom: str | None = None
    type: OrganisationType | str
    endpoints: list["Endpoint"] = Field(default_factory=list)


class Address(BaseModel):
    street: str | None
    town: str | None
    postcode: str | None


class PositionGCS(BaseModel):
    latitude: Decimal
    longitude: Decimal


class Location(DBModel):
    active: bool
    address: Address
    managingOrganisation: UUID
    name: str | None = None
    positionGCS: PositionGCS | None = None
    positionReferenceNumber_UPRN: int | None = None
    positionReferenceNumber_UBRN: int | None = None
    primaryAddress: bool
    partOf: UUID | None = None


class Telecom(BaseModel):
    phone_public: str | None
    phone_private: str | None
    email: str | None
    web: str | None


class AvailableTime(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME] = (
        OpeningTimeCategory.AVAILABLE_TIME
    )
    dayOfWeek: DayOfWeek
    startTime: time
    endTime: time
    allDay: bool = False


class AvailableTimeVariation(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS] = (
        OpeningTimeCategory.AVAILABLE_TIME_VARIATIONS
    )
    description: str | None = None
    startTime: datetime
    endTime: datetime


class AvailableTimePublicHolidays(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category: Literal[OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS] = (
        OpeningTimeCategory.AVAILABLE_TIME_PUBLIC_HOLIDAYS
    )
    startTime: time
    endTime: time


class NotAvailable(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    category: Literal[OpeningTimeCategory.NOT_AVAILABLE] = (
        OpeningTimeCategory.NOT_AVAILABLE
    )
    description: str | None = None
    startTime: datetime
    endTime: datetime


OpeningTime = Annotated[
    AvailableTime | AvailableTimeVariation | AvailableTimePublicHolidays | NotAvailable,
    Field(discriminator="category"),
]


class HealthcareService(DBModel):
    identifier_oldDoS_uid: str | None = None
    active: bool
    category: HealthcareServiceCategory
    type: HealthcareServiceType
    providedBy: UUID | None
    location: UUID | None
    name: str
    telecom: Telecom | None
    openingTime: list[OpeningTime] | None
    symptomGroupSymptomDiscriminators: SymptomGroupSymptomDiscriminatorPair | None = (
        None
    )
    dispositions: list[Disposition] | None = None


PAYLOAD_MIMETYPE_MAPPING = {
    "PDF": "application/pdf",
    "HTML": "text/html",
    "FHIR": "application/fhir",
    "email": "message/rfc822",
    "telno": "text/vcard",
    "xml": "xml",
    "CDA": "application/hl7-cda+xml",
}


class Endpoint(DBModel):
    identifier_oldDoS_id: int | None
    status: EndpointStatus
    connectionType: EndpointConnectionType
    name: str | None
    payloadMimeType: EndpointPayloadMimeType | None
    description: EndpointDescription
    payloadType: EndpointPayloadType | None
    address: str
    managedByOrganisation: UUID
    service: UUID | None
    order: int
    isCompressionEnabled: bool
