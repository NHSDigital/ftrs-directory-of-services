from uuid import UUID

from ftrs_data_layer.domain import Location, PositionGCS
from ftrs_data_layer.domain.legacy.data_models import ServiceData

from common.logbase import ServiceMigrationLogBase
from common.mapping.base import BaseMapper
from common.uuid_utils import generate_uuid
from service_migration.constants import SERVICE_MIGRATION_USER
from service_migration.formatting.address_formatter import format_address


class LocationMapper(BaseMapper[ServiceData, Location]):
    def map(self, service: ServiceData, organisation_id: UUID) -> Location:
        position = (
            PositionGCS(
                latitude=service.latitude,
                longitude=service.longitude,
            )
            if service.latitude and service.longitude
            else None
        )
        if service.address and service.address != "Not Available":
            formatted_address = format_address(
                service.address, service.town, service.postcode
            )
            self.logger.log(
                ServiceMigrationLogBase.DM_ETL_015,
                organisation=organisation_id,
                address=formatted_address,
            )

        else:
            formatted_address = None
            self.logger.log(
                ServiceMigrationLogBase.DM_ETL_016, organisation=organisation_id
            )

        return Location(
            id=generate_uuid(service.id, "location"),
            identifier_oldDoS_uid=service.uid,
            active=True,
            managingOrganisation=organisation_id,
            address=formatted_address,
            name=None,
            positionGCS=position,
            # TODO: defaulting will consider how to define for Fhir schema in future.
            #   but since this has the main ODSCode happy with this being set as True
            primaryAddress=True,
            createdBy=SERVICE_MIGRATION_USER,
            createdDateTime=self.start_time,
            modifiedBy=SERVICE_MIGRATION_USER,
            modifiedDateTime=self.start_time,
        )
