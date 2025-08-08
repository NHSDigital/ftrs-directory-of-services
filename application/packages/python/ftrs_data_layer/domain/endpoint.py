from uuid import UUID

from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.enums import (
    EndpointConnectionType,
    EndpointDescription,
    EndpointPayloadMimeType,
    EndpointPayloadType,
    EndpointStatus,
)

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
