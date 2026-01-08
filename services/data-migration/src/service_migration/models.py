from uuid import UUID

from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.base import DBModel

from service_migration.validation.types import ValidationIssue


class DataMigrationState(DBModel):
    source_record_id: str
    version: int
    organisation_id: UUID | None
    organisation: Organisation | None
    location_id: UUID | None
    location: Location | None
    healthcare_service_id: UUID | None
    healthcare_service: HealthcareService | None
    validation_issues: list[ValidationIssue]
