from time import perf_counter
from typing import Iterable

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import HealthcareService, Location, Organisation, legacy
from ftrs_data_layer.logbase import DataMigrationLogBase
from pydantic import BaseModel
from sqlmodel import Session, create_engine, select

from pipeline.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
    ServiceTransformOutput,
)
from pipeline.utils.cache import DoSMetadataCache
from pipeline.utils.config import DataMigrationConfig
from pipeline.utils.dbutil import get_repository
from pipeline.validation.types import ValidationIssue


class DataMigrationMetrics(BaseModel):
    total_records: int = 0
    supported_records: int = 0
    unsupported_records: int = 0
    transformed_records: int = 0
    migrated_records: int = 0
    skipped_records: int = 0
    invalid_records: int = 0
    errors: int = 0

    def reset(self) -> None:
        """
        Reset all metrics to zero.
        """
        self.total_records = 0
        self.supported_records = 0
        self.unsupported_records = 0
        self.transformed_records = 0
        self.migrated_records = 0
        self.skipped_records = 0
        self.invalid_records = 0
        self.errors = 0


class DataMigrationProcessor:
    """
    This class is responsible for managing the data migration process.
    It includes methods to transform legacy service data into the new format.
    """

    def __init__(
        self,
        config: DataMigrationConfig,
        logger: Logger,
    ) -> None:
        self.logger = logger
        self.config = config
        # Validate the presence of a real connection string to avoid confusing errors when given mocks
        connection_string = getattr(
            getattr(config, "db_config", None), "connection_string", None
        )
        if not isinstance(connection_string, str) or not connection_string.strip():
            raise ValueError(
                "Invalid DataMigrationConfig: db_config.connection_string must be a non-empty string"
            )
        self.engine = create_engine(connection_string, echo=False)
        self.metrics = DataMigrationMetrics()
        self.metadata = DoSMetadataCache(self.engine)

    # TODO: FDOS-383 - legacy data imported here
    def sync_all_services(self) -> None:
        """
        Run the full sync process.
        """
        for record in self._iter_records():
            self._process_service(record)

    def sync_service(self, record_id: int, method: str) -> None:
        """
        Run the single record sync process.
        """
        with Session(self.engine) as session:
            record = session.get(legacy.Service, record_id)
            if not record:
                raise ValueError(f"Service with ID {record_id} not found")

            self._process_service(record)

    def _process_service(self, service: legacy.Service) -> None:
        """
        Process a single record by transforming it using the appropriate transformer.
        """

        self.logger.append_keys(record_id=service.id)
        self.logger.log(
            DataMigrationLogBase.DM_ETL_001,
            record=service.model_dump(exclude_none=True, mode="json", warnings=False),
        )

        try:
            start_time = perf_counter()
            self.metrics.total_records += 1

            transformer = self.get_transformer(service)
            if not transformer:
                self.metrics.unsupported_records += 1
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_004,
                    reason="No suitable transformer found",
                )
                return

            self.metrics.supported_records += 1
            should_include, reason = transformer.should_include_service(service)
            if not should_include:
                self.metrics.skipped_records += 1
                self.logger.log(DataMigrationLogBase.DM_ETL_005, reason=reason)
                return

            validation_result = transformer.validator.validate(service)
            if not validation_result.is_valid:
                issues = [
                    issue.model_dump(mode="json") for issue in validation_result.issues
                ]
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_013,
                    record_id=service.id,
                    issue_count=len(issues),
                    issues=issues,
                )

            if not validation_result.should_continue:
                self.metrics.invalid_records += 1
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_014,
                    record_id=service.id,
                )
                return

            issues = self._convert_validation_issues(validation_result.issues)
            result = transformer.transform(validation_result.sanitised, issues)
            self.metrics.transformed_records += 1

            self.logger.log(
                DataMigrationLogBase.DM_ETL_006,
                transformer_name=transformer.__class__.__name__,
                original_record=service.model_dump(
                    exclude_none=True, mode="json", warnings=False
                ),
                transformed_record=result.model_dump(
                    exclude_none=True, mode="json", warnings=False
                ),
            )

            self._save(result)
            self.metrics.migrated_records += 1

            elapsed_time = perf_counter() - start_time

            self.logger.log(
                DataMigrationLogBase.DM_ETL_007,
                elapsed_time=elapsed_time,
                transformer_name=transformer.__class__.__name__,
                healthcare_service_count=len(result.healthcare_service),
                location_count=len(result.location),
                organisation_count=len(result.organisation),
                healthcare_service_ids=[hs.id for hs in result.healthcare_service],
                location_ids=[loc.id for loc in result.location],
                organisation_ids=[org.id for org in result.organisation],
            )

        except Exception as e:
            self.metrics.errors += 1
            self.logger.exception(
                "Unexpected error encountered whilst processing service record"
            )
            self.logger.log(DataMigrationLogBase.DM_ETL_008, error=str(e))
            return

        finally:
            self.logger.remove_keys(["record_id"])

    def get_transformer(self, service: legacy.Service) -> ServiceTransformer | None:
        """
        Get the appropriate transformer for the service.
        """
        for TransformerClass in SUPPORTED_TRANSFORMERS:
            is_supported, reason = TransformerClass.is_service_supported(service)

            if not is_supported:
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_002,
                    transformer_name=TransformerClass.__name__,
                    reason=reason,
                )
                continue

            self.logger.log(
                DataMigrationLogBase.DM_ETL_003,
                transformer_name=TransformerClass.__name__,
            )
            return TransformerClass(logger=self.logger, metadata=self.metadata)

    def _iter_records(self, batch_size: int = 1000) -> Iterable[legacy.Service]:
        """
        Iterate over records in the database.
        """
        stmt = select(legacy.Service).execution_options(yield_per=batch_size)
        with Session(self.engine) as session:
            yield from session.scalars(stmt)

    # TODO: FDOS-383 - save as expected here
    def _save(self, result: ServiceTransformOutput) -> None:
        """
        Save the transformed result to DynamoDB.
        """
        org_repo = get_repository(
            self.config, "organisation", Organisation, self.logger
        )
        location_repo = get_repository(self.config, "location", Location, self.logger)
        service_repo = get_repository(
            self.config, "healthcare-service", HealthcareService, self.logger
        )

        for org in result.organisation:
            org_repo.upsert(org)

        for loc in result.location:
            location_repo.upsert(loc)

        for hc in result.healthcare_service:
            service_repo.upsert(hc)

    def _convert_validation_issues(self, issues: list[ValidationIssue]) -> list[str]:
        """
        Convert validation issues to a list of strings.
        """
        return [
            f"field:{issue.expression} ,error: {issue.code},message:{issue.diagnostics},value:{issue.value}"
            for issue in issues
        ]
