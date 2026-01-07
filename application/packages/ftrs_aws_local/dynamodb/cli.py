import logging

from typer import Typer

from dynamodb.constants import ALL_ENTITY_TYPES, ClearableEntityType, TargetEnvironment
from dynamodb.init import init_tables
from dynamodb.reset import reset

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

typer_app = Typer(
    name="ftrs-aws-local",
    help="AWS Local CLI for managing local AWS services",
)

typer_app.command("reset")(reset)


@typer_app.command("init")
def init_tables_command(
    endpoint_url: str | None = None,
    env: TargetEnvironment = TargetEnvironment.local,
    workspace: str | None = None,
    entity_type: list[ClearableEntityType] | None = None,
) -> None:
    if entity_type is None:
        entity_type = list(ALL_ENTITY_TYPES)

    init_tables(
        endpoint_url=endpoint_url,
        env=env,
        workspace=workspace,
        entity_type=entity_type,
    )
