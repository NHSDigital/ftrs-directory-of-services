from uuid import UUID

from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.base import DBModel


class DataMigrationState(DBModel):
    source_record_id: str
    version: int
    organisation_id: UUID
    organisation: Organisation
    location_id: UUID
    location: Location
    healthcare_service_id: UUID
    healthcare_service: HealthcareService
