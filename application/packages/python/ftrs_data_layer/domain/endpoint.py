from uuid import UUID, uuid4

from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
    EndpointStatus,
)
from pydantic import BaseModel, Field

PAYLOAD_MIMETYPE_MAPPING = {
    "PDF": "application/pdf",
    "HTML": "text/html",
    "FHIR": "application/fhir",
    "email": "message/rfc822",
    "telno": "text/vcard",
    "xml": "xml",
    "CDA": "application/hl7-cda+xml",
}


class Endpoint(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    identifier_oldDoS_id: int | None
    status: EndpointStatus
    connectionType: EndpointConnectionType
    name: str | None
    payloadMimeType: EndpointPayloadMimeType | None
    businessScenario: EndpointBusinessScenario
    payloadType: str | None
    address: str
    managedByOrganisation: UUID
    service: UUID | None
    order: int
    isCompressionEnabled: bool
    comment: str | None = None
