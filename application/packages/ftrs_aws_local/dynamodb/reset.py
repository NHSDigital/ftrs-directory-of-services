from typing import Annotated, Generator

from boto3 import Session
from boto3.dynamodb.types import TypeDeserializer
from ftrs_common.utils.db_service import format_table_name
from mypy_boto3_dynamodb import DynamoDBClient
from rich.progress import track
from typer import Option, confirm

from dynamodb.constants import ALL_ENTITY_TYPES, ClearableEntityType, TargetEnvironment
from dynamodb.logger import LOGGER, ResetLogBase


def reset(
    env: Annotated[
        TargetEnvironment, Option(help="Environment to clear the data from")
    ],
    workspace: Annotated[
        str | None, Option(help="Workspace to clear the data from")
    ] = None,
    endpoint_url: Annotated[
        str | None, Option(help="URL to connect to local DynamoDB")
    ] = None,
    entity_type: Annotated[
        list[ClearableEntityType] | None,
        Option(help="Types of entities to clear from the database"),
    ] = None,
) -> None:
    """
    Reset the database by deleting all items in the specified table(s).
    This function is intended for use in development and local environments only.
    """
    if entity_type is None:
        entity_type = ALL_ENTITY_TYPES

    if env not in [TargetEnvironment.dev, TargetEnvironment.local]:
        LOGGER.log(ResetLogBase.ETL_RESET_005, env=env)
        raise ValueError()

    confirm(
        f"Are you sure you want to reset the {env} environment (workspace: {workspace or 'default'})? This action cannot be undone.",
        abort=True,
    )

    session = Session()

    for entity_name in entity_type:
        table_name = format_table_name(
            entity_name, TargetEnvironment(env).value, workspace
        )
        count = delete_all_table_items(table_name, session, endpoint_url)

        LOGGER.log(ResetLogBase.ETL_RESET_006, count=count, table_name=table_name)


def delete_all_table_items(
    session: Session,
    table_name: str,
    endpoint_url: str | None = None,
) -> int:
    ddb_resource = session.resource("dynamodb", endpoint_url=endpoint_url)
    ddb_client = session.client("dynamodb", endpoint_url=endpoint_url)
    table = ddb_resource.Table(table_name)

    record_keys_generator = iter_record_keys(client=ddb_client, table_name=table_name)

    count = 0
    for record_keys in track(
        record_keys_generator,
        description=f"Deleting items from {table_name}",
    ):
        table.delete_item(Key=record_keys)
        count += 1

    return count


def iter_record_keys(
    client: DynamoDBClient,
    table_name: str,
) -> Generator[dict, None, None]:
    deserialiser = TypeDeserializer()
    table = client.describe_table(TableName=table_name)["Table"]
    attributes_to_select = [key["AttributeName"] for key in table["KeySchema"]]

    paginator = client.get_paginator("scan")
    for page in paginator.paginate(
        TableName=table_name,
        ProjectionExpression=", ".join(attributes_to_select),
    ):
        for item in page.get("Items", []):
            yield {
                attr: deserialiser.deserialize(item[attr])
                for attr in attributes_to_select
                if attr in item
            }
