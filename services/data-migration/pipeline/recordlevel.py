from typing import Any

from pipeline.utils.db_config import DatabaseConfig
from aws_lambda_powertools.utilities.parameters import get_secret
from sqlalchemy import Engine
from sqlmodel import create_engine, Session, select, func, col
from ftrs_data_layer import legacy_model, models
from pipeline.transformer import (
    SUPPORTED_TRANSFORMERS,
    ServiceTransformer,
    ServiceTransformOutput,
)
from pydantic import BaseModel
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from pipeline.load import get_table_name
from typing import TypeVar, Iterable, Annotated
from ftrs_common.logger import Logger
import os
from typer import Option


T = TypeVar("T", bound=BaseModel)


def track(iterable: Iterable[T], total: int = None) -> Iterable[T]:
    """
    Track the progress of an iterable.
    """
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME", None):
        return iterable  # No tracking in Lambda

    from rich.progress import (
        Progress,
        TextColumn,
        TimeElapsedColumn,
    )

    with Progress(
        *Progress.get_default_columns(),
        TimeElapsedColumn(),
        TextColumn("({task.completed}/{task.total})"),
    ) as progress:
        task = progress.add_task("Transforming Records", total=total)
        for item in iterable:
            yield item
            progress.update(task, advance=1)


class DataMigrationApplication:
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
        self.engine = create_engine(db_uri, echo=False)
        self.metrics = self.Metrics()
        self.logger = Logger.get(service="data-migration")

        self.env = env
        self.workspace = workspace
        self.dynamodb_endpoint = dynamodb_endpoint
        self._repository_cache: dict[str, AttributeLevelRepository] = {}

    def get_repository(
        self, entity_type: str, model_cls: T
    ) -> AttributeLevelRepository[T]:
        """
        Get a DynamoDB repository for the specified table and model class.
        Caches the repository to avoid creating multiple instances for the same table.
        """
        table_name = get_table_name(
            entity_type=entity_type, env=self.env, workspace=self.workspace
        )
        if table_name not in self._repository_cache:
            self._repository_cache[table_name] = AttributeLevelRepository[T](
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

    def run_full_sync(self, event: dict, context: Any) -> None:
        """
        Run the full sync process.
        """
        total_record_count = self.get_total_record_count()
        self.logger.setLevel("WARNING")
        for record in track(self._iter_records(), total=total_record_count):
            self._process_record(record)

        print(self.metrics.model_dump_json(indent=2))

    def run_single_record_sync(self, event: dict) -> None:
        """
        Run the single record sync process.
        """
        record_id = event.get("record_id")
        if not record_id:
            raise ValueError("No record_id provided in the event")

        with Session(self.engine) as session:
            record = session.get(legacy_model.Service, record_id)
            if not record:
                self.logger.error(f"Record with ID {record_id} not found.")
                return

        self._process_record(record)

    def get_total_record_count(self) -> int:
        """
        Get the total number of records in the legacy service table.
        """
        with Session(self.engine) as session:
            return session.exec(select(func.count(col(legacy_model.Service.id)))).one()

    def _process_record(self, record: legacy_model.Service) -> None:
        """
        Process a single record by transforming it using the appropriate transformer.
        """
        try:
            self.metrics.total_records += 1

            transformer = self.get_transformer(record)
            if not transformer:
                self.metrics.unsupported_records += 1
                return

            self.metrics.supported_records += 1
            if not transformer.should_include_service(record):
                self.metrics.skipped_records += 1
                return

            result = transformer.transform(record)
            self.metrics.transformed_records += 1

            self._save_to_dynamo(result)
            self.metrics.migrated_records += 1

        except Exception as e:
            self.metrics.errors += 1
            return

    def get_transformer(
        self, service: legacy_model.Service
    ) -> ServiceTransformer | None:
        """
        Get the appropriate transformer for the service.
        """
        for TransformerClass in SUPPORTED_TRANSFORMERS:
            is_supported, reason = TransformerClass.is_service_supported(service)
            if is_supported:
                return TransformerClass()

    def _iter_records(self):
        """
        Iterate over records in the database.
        """
        with Session(self.engine) as session:
            records = session.exec(select(legacy_model.Service)).all()
            for record in records:
                yield record

    def _save_to_dynamo(self, result: ServiceTransformOutput) -> None:
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


def lambda_handler(event: dict, context: Any) -> None:
    """
    AWS Lambda entrypoint for transforming data.
    This function will be triggered by an S3 event.
    """
    db_config = DatabaseConfig.from_secretsmanager()
    app = DataMigrationApplication(
        db_uri=db_config.connection_string,
        env=os.getenv("ENVIRONMENT"),
        workspace=os.getenv("WORKSPACE", None),
    )
    if app.is_full_sync(event):
        return app.run_full_sync(event, context)

    return app.run_single_record_sync(event, context)


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
) -> None:
    """
    Local entrypoint for testing the data migration.
    This function can be used to run the full or single sync process locally.
    """
    app = DataMigrationApplication(
        db_uri=db_uri,
        env=env,
        workspace=workspace,
        dynamodb_endpoint=ddb_endpoint_url,
    )

    if service_id:
        event = {"record_id": service_id}
        return app.run_single_record_sync(event)

    event = {"full_sync": True}
    return app.run_full_sync(event, None)
