from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DBModel(BaseModel):
    """
    Base model for all database models.
    """

    id: UUID
    createdBy: str
    createdDateTime: datetime
    modifiedBy: str
    modifiedDateTime: datetime


class Organisation(DBModel):
    identifier_ODS_ODSCode: str | None
    active: bool
    name: str
    telecom: str | None
    type: str


class Location(DBModel):
    active: bool
    address_street: str
    address_postcode: str
    address_town: str
    managingOrganisation: UUID
    name: str
    positionGCS_latitude: float
    positionGCS_longitude: float
    positionGCS_easting: float
    positionGCS_northing: float
    positionReferenceNumber_UPRN: int | None
    positionReferenceNumber_UBRN: int | None
    primaryAddress: bool
    partOf: UUID | None


class HealthcareService(DBModel):
    identifier_oldDoS_uid: str
    active: bool
    category: str
    providedBy: UUID
    location: UUID
    name: str
    telecom_phone_public: str | None
    telecom_phone_private: str | None
    telecom_email: str | None
    telecom_web: str | None
    type: str


class Endpoints(DBModel):
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
