import os
from typing import Annotated

from typer import Option, Typer

from pipeline.processor import DataMigrationProcessor, ServiceTransformOutput

typer_app = Typer(
    name="dos-etl",
    help="DoS Data Migration Pipeline CLI",
)


@typer_app.command()
def local_handler(  # noqa: PLR0913
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
