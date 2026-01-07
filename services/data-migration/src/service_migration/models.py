from uuid import UUID

from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from pydantic import BaseModel, Field

from service_migration.constants import SourceDBTables
from service_migration.validation.types import ValidationIssue


class MigrationState(BaseModel):
    source_record_id: str
    version: int
    organisation_id: UUID | None = None
    organisation: Organisation | None = None
    location_id: UUID | None = None
    location: Location | None = None
    healthcare_service_id: UUID | None = None
    healthcare_service: HealthcareService | None = None
    validation_issues: list[ValidationIssue] = Field(default_factory=list)

    @classmethod
    def create(cls, record_id: int) -> "MigrationState":
        return cls(source_record_id=cls.format_source_record_id(record_id), version=0)

    @classmethod
    def format_source_record_id(
        cls,
        record_id: int,
        table_name: str = SourceDBTables.SERVICES,
    ) -> str:
        return f"{table_name}#{record_id}"


class TransformResult(BaseModel):
    organisation: Organisation | None
    location: Location | None
    healthcare_service: HealthcareService | None
    validation_issues: list[ValidationIssue] = Field(default_factory=list)


class ServiceMigrationMetrics(BaseModel):
    total: int = 0
    supported: int = 0
    unsupported: int = 0
    transformed: int = 0
    invalid: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errored: int = 0

    def reset(self) -> None:
        """
        Reset all metrics to zero.
        """
        self.total = 0
        self.supported = 0
        self.unsupported = 0
        self.transformed = 0
        self.inserted = 0
        self.updated = 0
        self.skipped = 0
        self.invalid = 0
        self.errored = 0
