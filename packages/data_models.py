from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

class Organisation(BaseModel):
  id: UUID
  identifier_ODS_ODSCode: str
  active: bool
  createdBy: str
  createdDateTime: datetime
  modifiedBy: str
  modifiedDateTime: datetime
  name: str
  telecom:str
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
  positionReferenceNumber_UPRN: int
  positionReferenceNumber_UBRN: int
  primaryAddress: bool
  partOf: UUID

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
  telecom_phone_public: str
  telecom_phone_private: str
  telecom_email: str
  telecom_web: str
  type: str

class Endpoints(BaseModel):
  id: UUID
  identifier_oldDoS_id: int
  status: str
  connectionType: str
  name: str
  description: str
  payloadType: str
  address: str
  managedByOrganisation: str
  service: str
  order: int
  isCompressionEnabled: bool
  format: str
  createdBy: str
  createdDateTime: datetime
  modifiedBy: str
  modifiedDateTime: datetime