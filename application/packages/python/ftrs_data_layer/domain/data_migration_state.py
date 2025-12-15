from uuid import uuid4

from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.base import DBModel


class DataMigrationState(DBModel):
    source_record_id: str
    version: int
    organisation_id: uuid4
    organisation: Organisation
    location_id: uuid4
    location: Location
    healthcare_service_id: uuid4
    healthcare_service: HealthcareService
