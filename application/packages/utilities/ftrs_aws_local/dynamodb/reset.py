from typing import Annotated, Any, List

import rich
from mypy_boto3_dynamodb import DynamoDBClient
from rich.progress import track
from typer import Option, confirm

from ftrs_aws_local.dynamodb.utils import TargetEnvironment
from ftrs_common.utils.db_service import format_table_name
from ftrs_data_layer.client import get_dynamodb_resource


console = rich.get_console()


def create_table(
    client: DynamoDBClient,
    table_name: str,
    key_schema: List[dict],
    attribute_definitions: List[dict],
    global_secondary_indexes: List[dict] | None,
) -> None:
    table_params = {
        "TableName": table_name,
        "KeySchema": key_schema,
        "AttributeDefinitions": attribute_definitions,
        "BillingMode": "PAY_PER_REQUEST",
    }
    if global_secondary_indexes:
        table_params["GlobalSecondaryIndexes"] = global_secondary_indexes
    client.create_table(**table_params)
    console.log(f"Created table {table_name}")


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
) -> None:
    """
    Reset the database by deleting all items in the specified table(s).
    This function is intended for use in development and local environments only.
    """

    tables_to_clear = [
        format_table_name(
            entity_name,
            env.value,
            workspace,
            stack="database" if entity_name != "state" else "data-migration",
        )
        for entity_name in [
            "organisation",
            "healthcare-service",
            "location",
            "triage-code",
            "state",
        ]
    ]

    console.print("The following tables will be cleared:")
    for table_name in tables_to_clear:
        console.print(f"- {table_name}")

    confirm(
        "Are you sure you want to proceed? This action cannot be undone.",
        abort=True,
    )

    for table_name in tables_to_clear:
        reset_table(endpoint_url, table_name)


def get_table_keys(client: DynamoDBClient, table_name: str) -> list[dict]:
    """Helper function to get the key schema of a DynamoDB table."""
    try:
        response = client.describe_table(TableName=table_name)

    except client.exceptions.ResourceNotFoundException:
        console.print(f"Table {table_name} does not exist. Skipping.")
        return None

    else:
        key_schema = response["Table"]["KeySchema"]
        return key_schema


def reset_table(endpoint_url: str | None, table_name: str) -> None:
    """Delete all items from the specified DynamoDB table."""
    resource = get_dynamodb_resource(endpoint_url)
    table = resource.Table(table_name)

    key_attribute_names = [key["AttributeName"] for key in table.key_schema]
    scan_kwargs = {
        "ProjectionExpression": ", ".join(key_attribute_names),
    }

    keys_to_delete: list[dict[str, Any]] = []
    last_evaluated_key: dict | None = None

    while True:
        if last_evaluated_key:
            response = table.scan(
                **scan_kwargs,
                ExclusiveStartKey=last_evaluated_key,
            )
        else:
            response = table.scan(**scan_kwargs)

        for item in track(
            response.get("Items", []),
            description=f"Fetching keys from {table_name}",
            transient=True,
        ):
            keys_to_delete.append(
                {
                    attribute_name: item[attribute_name]
                    for attribute_name in key_attribute_names
                }
            )

        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:
            break

    total = 0
    with table.batch_writer() as batch:
        for key in track(
            keys_to_delete,
            description=f"Deleting items from {table_name}",
            transient=True,
        ):
            batch.delete_item(Key=key)
            total += 1

    console.print(f"Deleted {total} items from {table_name}")

    # key_schema = get_table_keys(client, table_name)
    # if not key_schema:
    #     return

    # scan_kwargs = {
    #     "TableName": table_name,
    #     "ProjectionExpression": ", ".join([key["AttributeName"] for key in key_schema]),
    # }

    # for entity_name in entity_type:
    #     entity_cls = get_entity_cls(entity_name)
    #     table_name = format_table_name(
    #         entity_name,
    #         env.value,
    #         workspace,
    #         stack="database" if entity_name != "state" else "data-migration",
    #     )

    #     repository = AttributeLevelRepository(
    #         table_name=table_name,
    #         model_cls=entity_cls,
    #         endpoint_url=endpoint_url,
    #     )

    #     count = 0
    #     for item in track(
    #         repository.iter_records(max_results=None),
    #         description=f"Deleting items from {entity_name}",
    #         transient=True,
    #     ):
    #         repository.delete(item.id)
    #         count += 1

    #     reset_logger.log(
    #         DataMigrationLogBase.ETL_RESET_006, count=count, table_name=table_name
    #     )
