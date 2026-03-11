from datetime import datetime
from uuid import UUID

from ftrs_data_layer.domain.auditevent import AuditEvent
from ftrs_data_layer.domain.base import DBModel
from ftrs_data_layer.domain.enums import (
    EndpointBusinessScenario,
    EndpointConnectionType,
    EndpointPayloadMimeType,
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
    # Endpoints doesn't need to be audited, healtcare services and organization have audit event fields
    created: datetime | None = None
    lastUpdated: datetime | None = None
    createdBy: AuditEvent | None = None
    lastUpdatedBy: AuditEvent | None = None

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
