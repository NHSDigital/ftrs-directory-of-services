from uuid import UUID

from ftrs_data_layer.domain import HealthcareService, Location, Organisation
<<<<<<< HEAD
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
=======
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
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682))
