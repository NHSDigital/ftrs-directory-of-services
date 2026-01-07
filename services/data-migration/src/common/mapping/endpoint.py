from uuid import UUID

from ftrs_data_layer.domain import (
    PAYLOAD_MIMETYPE_MAPPING,
    Endpoint,
    EndpointStatus,
)
from ftrs_data_layer.domain.legacy.data_models import ServiceEndpointData

from common.mapping.base import BaseMapper
from common.uuid_utils import generate_uuid
from service_migration.constants import SERVICE_MIGRATION_USER


class EndpointMapper(BaseMapper[ServiceEndpointData, Endpoint]):
    def map(
        self,
        endpoint: ServiceEndpointData,
        organisation_id: UUID,
        service_id: UUID | None = None,
    ) -> Endpoint:
        """
        Create an Endpoint instance from the source DoS endpoint data.
        """
        payload_type = endpoint.interaction
        payload_mime_type = PAYLOAD_MIMETYPE_MAPPING.get(
            endpoint.format, endpoint.format
        )

        if endpoint.transport == "telno":
            payload_type = None
            payload_mime_type = None

        return Endpoint(
            id=generate_uuid(endpoint.id, "endpoint"),
            identifier_oldDoS_id=endpoint.id,
            status=EndpointStatus.ACTIVE,
            connectionType=endpoint.transport,
            name=None,
            description=endpoint.businessscenario,
            payloadType=payload_type,
            payloadMimeType=payload_mime_type,
            address=endpoint.address,
            managedByOrganisation=organisation_id,
            service=service_id,
            order=endpoint.endpointorder,
            isCompressionEnabled=endpoint.iscompressionenabled == "compressed",
            createdBy=SERVICE_MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=SERVICE_MIGRATION_USER,
            modifiedDateTime=self.start_time,
        )
