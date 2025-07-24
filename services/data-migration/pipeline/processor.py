from time import perf_counter
from typing import Iterable
from uuid import uuid4

from ftrs_common.logger import Logger
from ftrs_data_layer import models
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.logbase import DataMigrationLogBase
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository, ModelType
from pydantic import BaseModel
from sqlmodel import Session, create_engine, select

from pipeline.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
    ServiceTransformOutput,
)


class DataMigrationProcessor:
    """
    This class is responsible for managing the data migration process.
    It includes methods to transform legacy service data into the new format.
    """

    class Metrics(BaseModel):
        total_records: int = 0
        supported_records: int = 0
        unsupported_records: int = 0
        transformed_records: int = 0
        migrated_records: int = 0
        skipped_records: int = 0
        errors: int = 0

    def __init__(
        self,
        db_uri: str,
        env: str,
        workspace: str | None = None,
        dynamodb_endpoint: str | None = None,
    ) -> None:
        self.logger = Logger.get(service="data-migration")
        self.logger.append_keys(
            run_id=str(uuid4()),
            env=env,
            workspace=workspace,
        )

        self.engine = create_engine(db_uri, echo=False)
        self.metrics = self.Metrics()

        self.env = env
        self.workspace = workspace
        self.dynamodb_endpoint = dynamodb_endpoint
        self._repository_cache: dict[str, AttributeLevelRepository] = {}

    def get_repository(
        self, entity_type: str, model_cls: ModelType
    ) -> AttributeLevelRepository[ModelType]:
        """
        Get a DynamoDB repository for the specified table and model class.
        Caches the repository to avoid creating multiple instances for the same table.
        """
        table_name = f"ftrs-dos-{self.env}-database-{entity_type}"
        if self.workspace:
            table_name = f"{table_name}-{self.workspace}"

        if table_name not in self._repository_cache:
            self._repository_cache[table_name] = AttributeLevelRepository[ModelType](
                table_name=table_name,
                model_cls=model_cls,
                endpoint_url=self.dynamodb_endpoint,
                logger=self.logger,
            )
        return self._repository_cache[table_name]

    @classmethod
    def is_full_sync(cls, event: dict) -> bool:
        """
        Check if the event indicates a full sync.
        TODO: Implement logic to determine if the event is a full sync
        """
        return True

    def run_full_sync(self, event: dict, context: dict) -> None:
        """
        Run the full sync process.
        """
        self.logger.log(DataMigrationLogBase.DM_ETL_000, mode="full_sync")

        for record in self._iter_records():
            self._process_service(record)

        self.logger.log(
            DataMigrationLogBase.DM_ETL_999,
            mode="full_sync",
            metrics=self.metrics.model_dump(),
        )

    def run_single_service_sync(self, event: dict) -> None:
        """
        Run the single record sync process.
        """
        self.logger.log(DataMigrationLogBase.DM_ETL_000, mode="single_record_sync")

        record_id = event.get("record_id")
        if not record_id:
            raise ValueError("No record_id provided in the event")

        with Session(self.engine) as session:
            record = session.get(legacy_model.Service, record_id)
            if not record:
                self.logger.error(f"Record with ID {record_id} not found.")
                return

            self._process_service(record)

        self.logger.log(
            DataMigrationLogBase.DM_ETL_999,
            mode="single_record_sync",
            metrics=self.metrics.model_dump(),
        )

    def _process_service(self, service: legacy_model.Service) -> None:
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
                    record_id=service.id,
                    reason="No suitable transformer found",
                )
                return

            self.metrics.supported_records += 1
            should_include, reason = transformer.should_include_service(service)
            if not should_include:
                self.metrics.skipped_records += 1
                self.logger.log(
                    DataMigrationLogBase.DM_ETL_004,
                    record_id=service.id,
                    reason=f"Transformer indicated to skip this record - {reason}",
                )
                return

            result = transformer.transform(service)
            self.metrics.transformed_records += 1

            self.logger.log(
                DataMigrationLogBase.DM_ETL_005,
                record_id=service.id,
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
                DataMigrationLogBase.DM_ETL_006,
                record_id=service.id,
                elapsed_time=elapsed_time,
                transformer_name=transformer.__class__.__name__,
                healthcare_service_id=result.healthcare_service.id,
                organisation_id=result.organisation.id,
                location_id=result.location.id,
            )

        except Exception as e:
            self.metrics.errors += 1
            self.logger.exception(
                "Unexpected error encountered whilst processing service record"
            )
            self.logger.log(
                DataMigrationLogBase.DM_ETL_007,
                record_id=service.id,
                error=str(e),
            )
            return

        finally:
            self.logger.remove_keys(["record_id"])

    def get_transformer(
        self, service: legacy_model.Service
    ) -> ServiceTransformer | None:
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
            return TransformerClass(
                reference_data=self.reference_data,
                logger=self.logger,
            )

    def _iter_records(self) -> Iterable[legacy_model.Service]:
        """
        Iterate over records in the database.
        """
        with Session(self.engine) as session:
            yield from session.exec(select(legacy_model.Service)).all()

    def _save(self, result: ServiceTransformOutput) -> None:
        """
        Save the transformed result to DynamoDB.
        """
        org_repo = self.get_repository("organisation", models.Organisation)
        org_repo.upsert(result.organisation)

        location_repo = self.get_repository("location", models.Location)
        location_repo.upsert(result.location)

        service_repo = self.get_repository(
            "healthcare-service", models.HealthcareService
        )
        service_repo.upsert(result.healthcare_service)
