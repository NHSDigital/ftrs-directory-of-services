from contextlib import contextmanager
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Generator, List

from typer import Option, Typer

from pipeline.application import DataMigrationApplication
from pipeline.queue_populator import populate_sqs_queue
from pipeline.utils.config import (
    DatabaseConfig,
    DataMigrationConfig,
    QueuePopulatorConfig,
)


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"
    test = "test"
    int = "int"
    sandpit = "sandpit"
    ref = "ref"


typer_app = Typer(
    name="dos-etl",
    help="DoS Data Migration Pipeline CLI",
)


@typer_app.command("migrate")
def migrate_handler(  # noqa: PLR0913
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
        Path | None, Option(help="Directory to save transformed records (dry run only)")
    ] = None,
) -> None:
    """
    Local entrypoint for testing the data migration.
    This function can be used to run the full or single sync process locally.
    """
    app = DataMigrationApplication(
        config=DataMigrationConfig(
            db_config=DatabaseConfig.from_uri(db_uri),
            ENVIRONMENT=env,
            WORKSPACE=workspace,
            ENDPOINT_URL=ddb_endpoint_url,
        ),
    )

    with patch_local_save_method(app, output_dir):
        if service_id:
            event = {
                "type": "dms_event",
                "record_id": service_id,
                "method": "insert",
                "table_name": "services",
            }
            app.handle_event(event)
        else:
            event = {"type": "full_sync"}
            app.handle_event(event)


@typer_app.command("populate-queue")
def populate_queue_handler(
    db_uri: Annotated[str, Option(..., help="URI to connect to the source database")],
    sqs_queue_url: Annotated[
        str, Option(..., help="SQS queue URL to populate with legacy services")
    ],
    type_ids: Annotated[
        List[int] | None, Option(help="List of type IDs to filter services by")
    ] = None,
    status_ids: Annotated[
        List[int] | None, Option(help="List of status IDs to filter services by")
    ] = None,
) -> None:
    """
    Local entrypoint for populating the queue with legacy services.
    This function can be used to test the queue population logic.
    """
    config = QueuePopulatorConfig(
        db_config=DatabaseConfig.from_uri(db_uri),
        SQS_QUEUE_URL=sqs_queue_url,
        type_ids=type_ids,
        status_ids=status_ids,
    )
    populate_sqs_queue(config)


@contextmanager
def patch_local_save_method(
    app: DataMigrationApplication, output_dir: Path | None
) -> Generator:
    """
    Patch the application to save transformed records to a local directory.
    This is useful for testing without affecting the database.
    """
    if output_dir is None:
        yield
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    organisation_path = output_dir / "organisation.jsonl"
    location_path = output_dir / "location.jsonl"
    healthcare_path = output_dir / "healthcare-service.jsonl"

    organisation_file = open(organisation_path, "w")
    location_file = open(location_path, "w")
    healthcare_file = open(healthcare_path, "w")

    app.processor._save = lambda out: (
        organisation_file.write(
            out.organisation.model_dump_json(exclude_none=True) + "\n"
        ),
        location_file.write(out.location.model_dump_json(exclude_none=True) + "\n"),
        healthcare_file.write(
            out.healthcare_service.model_dump_json(exclude_none=True) + "\n"
        ),
    )

    yield

    organisation_file.close()
    location_file.close()
    healthcare_file.close()
