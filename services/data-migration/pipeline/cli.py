import asyncio
import json
from contextlib import contextmanager
from enum import StrEnum
from pathlib import Path
from typing import Annotated, Generator, List

import awswrangler as wr
import rich
from aws_lambda_powertools.utilities.parameters import get_parameter, set_parameter
from ftrs_common.utils.db_service import format_table_name
from typer import Option, Typer

from pipeline.application import DataMigrationApplication, DMSEvent
from pipeline.processor import ServiceTransformOutput
from pipeline.queue_populator import populate_sqs_queue
from pipeline.seeding.bulkload import bulk_load_table
from pipeline.seeding.export import export_table, process_export
from pipeline.utils.config import (
    DatabaseConfig,
    DataMigrationConfig,
    QueuePopulatorConfig,
)

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
            event = DMSEvent(
                type="dms_event",
                record_id=service_id,
                method="insert",
                table_name="services",
            )
            app.handle_dms_event(event)
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

    def _mock_save(result: ServiceTransformOutput) -> None:
        for org in result.organisation:
            organisation_file.write(org.model_dump_json() + "\n")
        for loc in result.location:
            location_file.write(loc.model_dump_json() + "\n")
        for hc in result.healthcare_service:
            healthcare_file.write(hc.model_dump_json() + "\n")

    app.processor._save = _mock_save
    yield

    organisation_file.close()
    location_file.close()
    healthcare_file.close()


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


async def run_s3_export(env: str, workspace: str | None) -> list:
    """
    Run the actual S3 export process (async)
    """
    export_tasks = [
        export_table("location", env, workspace),
        export_table("organisation", env, workspace),
        # export_table("healthcare-service", env, workspace), TODO: FDOS-547 - Uncomment when enabling seeding of HealthcareService records
    ]
    table_uris = {}

    for task in asyncio.as_completed(export_tasks):
        export_description = await task
        table_name = export_description["TableArn"].rsplit("/")[-1]
        records_df = await process_export(export_description)

        out_key = f"backups/{table_name}.parquet"
        out_uri = f"s3://{export_description['S3Bucket']}/{out_key}"

        wr.s3.to_parquet(
            df=records_df,
            path=out_uri,
            dataset=False,
        )
        CONSOLE.log(
            f"Saved {records_df.shape[0]} items from [bright_blue]{table_name}[/bright_blue] to [bright_cyan]{out_key}[/bright_cyan]",
            style="green",
        )

        table_uris[table_name.split("database-")[-1]] = out_uri

    set_parameter(
        name=f"/ftrs/dos/{env}/dynamodb-backup-arns",
        value=json.dumps(table_uris),
        overwrite=True,
    )
    CONSOLE.log(
        f"DynamoDB backup ARNs parameter for environment [bright_blue]{env}[/bright_blue] saved successfully",
        style="green",
    )


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


async def run_s3_restore(env: str, workspace: str | None) -> None:
    """
    Run the actual S3 restore process (async)
    """
    CONSOLE.log(
        f"Restoring data from S3 for environment [bright_blue]{env}[/bright_blue] and workspace [bright_blue]{workspace}[/bright_blue]"
    )

    CONSOLE.log("Downloading backup files from S3", style="bright_black")
    backup_uris = get_parameter(
        name=f"/ftrs/dos/{env}/dynamodb-backup-arns",
        transform="json",
    )
    data = {
        entity_type: wr.s3.read_parquet(path=path)
        for entity_type, path in backup_uris.items()
    }

    CONSOLE.log("Restoring data to DynamoDB", style="bright_black")
    tasks = [
        bulk_load_table(
            format_table_name(entity_type, env, workspace), df["data"].tolist()
        )
        for entity_type, df in data.items()
    ]

    await asyncio.gather(*tasks)

    CONSOLE.log(
        f"Data restoration complete to [bright_blue]{env}[/bright_blue] and workspace [bright_blue]{workspace}[/bright_blue]",
        style="bright_green",
    )
