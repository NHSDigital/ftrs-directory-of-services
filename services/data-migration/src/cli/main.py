import asyncio
from enum import StrEnum
from typing import Annotated, List

import rich
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from typer import Option, Typer

from common.config import DatabaseConfig
from queue_populator.config import QueuePopulatorConfig
from queue_populator.lambda_handler import populate_sqs_queue
from seeding.export_to_s3 import run_s3_export
from seeding.restore import run_s3_restore
from service_migration.application import DataMigrationApplication, DMSEvent
from service_migration.config import DataMigrationConfig

CONSOLE = rich.get_console()


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

    if service_id:
        event = DMSEvent(
            type="dms_event",
            record_id=int(service_id),
            service_id=int(service_id),
            method="insert",
            table_name="services",
        )
        record = SQSRecord(
            data={
                "messageId": f"service-{service_id}",
                "body": event.model_dump_json(),
            }
        )
        app.handle_sqs_record(record)
    else:
        app.handle_full_sync_event()


@typer_app.command("populate-queue")
def populate_queue_handler(
    db_uri: Annotated[str, Option(..., help="URI to connect to the source database")],
    sqs_queue_url: Annotated[
        str, Option(..., help="SQS queue URL to populate with legacy services")
    ],
    type_id: Annotated[
        List[int] | None, Option(help="List of type IDs to filter services by")
    ] = None,
    status_id: Annotated[
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
        type_ids=type_id,
        status_ids=status_id,
        service_id=None,
        record_id=None,
        full_sync=True,
        table_name="services",
    )
    populate_sqs_queue(config)


@typer_app.command("export-to-s3")
def export_to_s3_handler(
    env: Annotated[str, Option(..., help="Environment to run the export in")],
    workspace: Annotated[
        str | None, Option(..., help="Workspace to run the export in")
    ] = None,
) -> None:
    """
    Handler for exporting data from all DynamoDB tables to S3.
    """
    asyncio.run(run_s3_export(env, workspace))


@typer_app.command("restore-from-s3")
def restore_from_s3_handler(
    env: Annotated[str, Option(..., help="Environment to run the restore in")],
    workspace: Annotated[
        str | None, Option(..., help="Workspace to run the restore in")
    ] = None,
) -> None:
    """
    Handler for restoring data from S3 to all DynamoDB tables.
    """
    asyncio.run(run_s3_restore(env, workspace))


if __name__ == "__main__":
    typer_app()
