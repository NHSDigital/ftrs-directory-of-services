from decimal import Decimal
from uuid import UUID

from ftrs_data_layer.domain.base import DBModel
from pydantic import BaseModel


class Address(BaseModel):
    line1: str | None
    line2: str | None
    county: str | None
    town: str | None
    postcode: str | None


class PositionGCS(BaseModel):
    latitude: Decimal
    longitude: Decimal


class Location(DBModel):
    identifier_oldDoS_uid: str | None = None
    active: bool
    address: Address # NOTE: FTRS-1623 - cannot set to none as has cardinality of 1, is needed to create location
    managingOrganisation: UUID
    name: str | None = None
    positionGCS: PositionGCS | None = None
    positionReferenceNumber_UPRN: int | None = None
    positionReferenceNumber_UBRN: int | None = None
    primaryAddress: bool
    partOf: UUID | None = None
