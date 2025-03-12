from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Organisation(BaseModel):
    id: UUID
    identifier_ODS_ODSCode: str | None
    active: bool
    createdBy: str
    createdDateTime: datetime
    modifiedBy: str
    modifiedDateTime: datetime
    name: str
    telecom: str | None
    type: str


class Location(BaseModel):
    id: UUID
    active: bool
    address_street: str
    address_postcode: str
    address_town: str
    createdBy: str
    createdDateTime: datetime
    managingOrganisation: UUID
    modifiedBy: str
    modifiedDateTime: datetime
    name: str
    positionGCS_latitude: float
    positionGCS_longitude: float
    positionGCS_easting: float
    positionGCS_northing: float
    positionReferenceNumber_UPRN: int | None
    positionReferenceNumber_UBRN: int | None
    primaryAddress: bool
    partOf: UUID | None


class HealthcareService(BaseModel):
    id: UUID
    identifier_oldDoS_uid: str
    active: bool
    category: str
    createdBy: str
    createdDateTime: datetime
    providedBy: UUID
    location: UUID
    modifiedBy: str
    modifiedDateTime: datetime
    name: str
    telecom_phone_public: str | None
    telecom_phone_private: str | None
    telecom_email: str | None
    telecom_web: str | None
    type: str


class Endpoints(BaseModel):
    id: UUID
    identifier_oldDoS_id: int | None
    status: str
    connectionType: str
    name: str | None
    description: str
    payloadType: str | None
    address: str
    managedByOrganisation: UUID
    service: UUID | None
    order: int
    isCompressionEnabled: bool
    format: str | None
    createdBy: str
    createdDateTime: datetime
    modifiedBy: str
    modifiedDateTime: datetime
