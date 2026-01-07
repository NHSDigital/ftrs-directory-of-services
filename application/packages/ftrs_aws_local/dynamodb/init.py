from ftrs_common.utils.db_service import format_table_name, get_dynamodb_client
from mypy_boto3_dynamodb import DynamoDBClient

from dynamodb.constants import ClearableEntityType, TargetEnvironment
from dynamodb.logger import LOGGER, ResetLogBase


def create_table(
    client: DynamoDBClient,
    table_name: str,
    key_schema: list[dict],
    attribute_definitions: list[dict],
    global_secondary_indexes: list[dict] | None,
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
    LOGGER.log(ResetLogBase.ETL_RESET_003, table_name=table_name)


def init_tables(
    endpoint_url: str | None,
    env: TargetEnvironment,
    workspace: str | None,
    entity_type: list[ClearableEntityType],
) -> None:
    LOGGER.log(ResetLogBase.ETL_RESET_001)

    if env != TargetEnvironment.local:
        LOGGER.log(ResetLogBase.ETL_RESET_002)
        raise ValueError(ResetLogBase.ETL_RESET_002.value.message)

    client = get_dynamodb_client(endpoint_url)
    for entity_name in entity_type:
        table_name = format_table_name(entity_name, env.value, workspace)
        entity_config = get_entity_config(entity_name)
        try:
            create_table(
                client=client,
                table_name=table_name,
                key_schema=entity_config["key_schema"],
                attribute_definitions=entity_config["attribute_definitions"],
                global_secondary_indexes=entity_config["global_secondary_indexes"],
            )
        except client.exceptions.ResourceInUseException:
            LOGGER.log(ResetLogBase.ETL_RESET_004, table_name=table_name)


def get_entity_config(entity_name: ClearableEntityType) -> dict:
    table_entity = {
        "organisation": {
            "key_schema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "attribute_definitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {
                    "AttributeName": "identifier_ODS_ODSCode",
                    "AttributeType": "S",
                },
            ],
            "global_secondary_indexes": [
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
            "key_schema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "attribute_definitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "providedBy", "AttributeType": "S"},
                {"AttributeName": "location", "AttributeType": "S"},
            ],
            "global_secondary_indexes": [
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
            "key_schema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "attribute_definitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "managingOrganisation", "AttributeType": "S"},
            ],
            "global_secondary_indexes": [
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
            "key_schema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "attribute_definitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
                {"AttributeName": "codeType", "AttributeType": "S"},
                {"AttributeName": "codeID", "AttributeType": "S"},
            ],
            "global_secondary_indexes": [
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
        "data-migration-state": {
            "key_schema": [
                {"AttributeName": "source_record_id", "KeyType": "HASH"},
            ],
            "attribute_definitions": [
                {"AttributeName": "source_record_id", "AttributeType": "S"}
            ],
            "global_secondary_indexes": None,
        },
        "default": {
            "key_schema": [
                {"AttributeName": "id", "KeyType": "HASH"},
                {"AttributeName": "field", "KeyType": "RANGE"},
            ],
            "attribute_definitions": [
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "field", "AttributeType": "S"},
            ],
            "global_secondary_indexes": None,
        },
    }
    return table_entity.get(entity_name, table_entity["default"])
