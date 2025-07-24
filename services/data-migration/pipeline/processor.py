import os
from typing import Annotated, Iterable, TypeVar
from uuid import uuid4

from ftrs_common.logger import Logger
from ftrs_data_layer import models
from ftrs_data_layer.domain import legacy as legacy_model
from ftrs_data_layer.logbase import DataMigrationLogBase
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository, ModelType
from pydantic import BaseModel
from sqlmodel import Session, create_engine, select
from typer import Option
from time import perf_counter
from pipeline.utils.metadata import DoSReferenceData

from pipeline.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
    ServiceTransformOutput,
)
from pipeline.utils.db_config import DatabaseConfig


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
        self.reference_data = DoSReferenceData(self.engine, self.logger)

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


def lambda_handler(event: dict, context: dict) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an S3 event.
    """
    db_config = DatabaseConfig.from_secretsmanager()
    app = DataMigrationProcessor(
        db_uri=db_config.connection_string,
        env=os.getenv("ENVIRONMENT"),
        workspace=os.getenv("WORKSPACE", None),
    )
    if app.is_full_sync(event):
        return app.run_full_sync(event, context)

    return app.run_single_service_sync(event, context)


def local_handler(
    db_uri: Annotated[
        str | None, Option(..., help="URI to connect to the source database")
    ],
    env: Annotated[str, Option(..., help="Environment to run the migration in")],
    workspace: Annotated[
        str | None, Option(help="Workspace to run the migration in")
    ] = None,
    ddb_endpoint_url: Annotated[
        str | None, Option(help="URL to connect to local DynamoDB")
    ] = None,
    service_id: Annotated[
        str | None, Option(help="Service ID to migrate (for single record sync)")
    ] = None,
    output_dir: Annotated[
        str | None, Option(help="Directory to save transformed records (dry run only)")
    ] = None,
) -> None:
    """
    Local entrypoint for testing the data migration.
    This function can be used to run the full or single sync process locally.
    """
    app = DataMigrationProcessor(
        db_uri=db_uri,
        env=env,
        workspace=workspace,
        dynamodb_endpoint=ddb_endpoint_url,
    )

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        hs_file = open(os.path.join(output_dir, "healthcare_service.jsonl"), "w")
        org_file = open(os.path.join(output_dir, "organisation.jsonl"), "w")
        loc_file = open(os.path.join(output_dir, "location.jsonl"), "w")

        def _local_save(result: ServiceTransformOutput) -> None:
            """
            Save the transformed result to local files instead of DynamoDB.
            """
            hs_file.write(result.healthcare_service.model_dump_json(exclude_none=True))
            hs_file.write("\n")

            org_file.write(result.organisation.model_dump_json(exclude_none=True))
            org_file.write("\n")

            loc_file.write(result.location.model_dump_json(exclude_none=True))
            loc_file.write("\n")

        app._save = _local_save  # Override save method to prevent actual saving

    if service_id:
        event = {"record_id": service_id}
        app.run_single_service_sync(event)

    else:
        event = {"full_sync": True}
        app.run_full_sync(event, None)

    if output_dir:
        hs_file.close()
        org_file.close()
        loc_file.close()
        print(f"Transformed records saved to {output_dir}")
