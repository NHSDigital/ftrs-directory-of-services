from uuid import UUID

from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from pydantic import BaseModel

from service_migration.validation.types import ValidationIssue


class ServiceMigrationState(BaseModel):
    source_record_id: str
    version: int
    organisation_id: UUID | None
    organisation: Organisation | None
    location_id: UUID | None
    location: Location | None
    healthcare_service_id: UUID | None
    healthcare_service: HealthcareService | None
    validation_issues: list[ValidationIssue]

    @classmethod
    def format_source_record_id(cls, service_id: int) -> str:
        return f"services#{service_id}"

    @classmethod
    def init(
        cls,
        service_id: int,
        validation_issues: list[ValidationIssue] = [],
    ) -> "ServiceMigrationState":
        return cls(
            source_record_id=cls.format_source_record_id(service_id),
            version=0,
            organisation_id=None,
            organisation=None,
            location_id=None,
            location=None,
            healthcare_service_id=None,
            healthcare_service=None,
            validation_issues=validation_issues,
        )
