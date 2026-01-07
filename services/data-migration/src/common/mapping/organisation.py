from ftrs_data_layer.domain.legacy.data_models import ServiceData
from ftrs_data_layer.domain.organisation import Organisation

from common.mapping.base import BaseMapper
from common.mapping.endpoint import EndpointMapper
from common.uuid_utils import generate_uuid
from service_migration.constants import SERVICE_MIGRATION_USER


class OrganisationMapper(BaseMapper[ServiceData, Organisation]):
    def __init__(self, *args: tuple, **kwargs: dict) -> None:
        super().__init__(*args, **kwargs)
        self.endpoint_mapper = EndpointMapper(*args, **kwargs)

    def map(self, service: ServiceData) -> Organisation:
        """
        Create an Organisation instance from the source DoS service data.
        """
        organisation_id = generate_uuid(service.id, "organisation")
        service_type = self.metadata.service_types.get(service.typeid)

        return Organisation(
            id=organisation_id,
            identifier_oldDoS_uid=service.uid,
            identifier_ODS_ODSCode=service.odscode,
            active=True,
            name=service.publicname,
            telecom=[],
            type=service_type.name,
            createdBy=SERVICE_MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=SERVICE_MIGRATION_USER,
            modifiedDateTime=self.start_time,
            endpoints=[
                self.endpoint_mapper.map(endpoint, organisation_id)
                for endpoint in service.endpoints
            ],
        )
