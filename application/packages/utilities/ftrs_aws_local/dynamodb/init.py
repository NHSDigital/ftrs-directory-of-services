from ftrs_common.logger import Logger
from ftrs_aws_local.dynamodb.utils import ClearableEntityTypes, TargetEnvironment
from ftrs_common.utils.db_service import format_table_name, get_dynamodb_client
import rich
from typing import Annotated
from typer import Option

console = rich.get_console()


def init_tables(
    endpoint_url: Annotated[str, Option(help="URL to connect to local DynamoDB")],
    env: Annotated[
        TargetEnvironment, Option(help="Environment name")
    ] = TargetEnvironment.local,
    workspace: Annotated[str | None, Option(help="Workspace name")] = None,
) -> None:
    """
    Initialise DynamoDB tables in a local environment.
    """
    # logger.log(DataMigrationLogBase.ETL_RESET_001)

    # reset_logger.log(DataMigrationLogBase.ETL_RESET_002)
    # raise ValueError(DataMigrationLogBase.ETL_RESET_002.value.message)

    client = get_dynamodb_client(endpoint_url)

    for entity_name, table_definition in get_entity_config().items():
        table_name = format_table_name(
            entity_name,
            env.value,
            workspace,
            stack="database" if entity_name != "state" else "data-migration",
        )

        try:
            client.create_table(
                TableName=table_name,
                BillingMode="PAY_PER_REQUEST",
                **table_definition,
            )

        except client.exceptions.ResourceInUseException:
            console.log(f"Table {table_name} already exists, skipping creation.")


def get_entity_config() -> dict:
    return {
        "organisation": {
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {
                    "AttributeName": "identifier_ODS_ODSCode",
                    "AttributeType": "S",
                },
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "OdsCodeValueIndex",
                    "KeySchema": [
                        {
                            "AttributeName": "identifier_ODS_ODSCode",
                            "KeyType": "HASH",
                        },
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
        "healthcare-service": {
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "providedBy", "AttributeType": "S"},
                {"AttributeName": "location", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "ProvidedByValueIndex",
                    "KeySchema": [
                        {
                            "AttributeName": "providedBy",
                            "KeyType": "HASH",
                        },
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
                {
                    "IndexName": "LocationIndex",
                    "KeySchema": [
                        {
                            "AttributeName": "location",
                            "KeyType": "HASH",
                        },
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],
        },
        "location": {
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "managingOrganisation", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "ManagingOrganisationIndex",
                    "KeySchema": [
                        {
                            "AttributeName": "managingOrganisation",
                            "KeyType": "HASH",
                        },
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
        "triage-code": {
            "KeySchema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "codeType", "AttributeType": "S"},
                {"AttributeName": "codeID", "AttributeType": "S"},
            ],
            "GlobalSecondaryIndexes": [
                {
                    "IndexName": "CodeTypeIndex",
                    "KeySchema": [
                        {
                            "AttributeName": "codeType",
                            "KeyType": "HASH",
                        },
                        {
                            "AttributeName": "id",
                            "KeyType": "RANGE",
                        },
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
        },
        "state": {
            "KeySchema": [
                {"AttributeName": "source_record_id", "KeyType": "HASH"},
            ],
            "AttributeDefinitions": [
                {"AttributeName": "source_record_id", "AttributeType": "S"}
            ],
        },
    }
