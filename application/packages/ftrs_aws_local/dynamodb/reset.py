from enum import StrEnum
from typing import Annotated, List

import boto3
from ftrs_common.logger import Logger
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import HealthcareService, Location, Organisation
from ftrs_data_layer.domain.triage_code import TriageCode
from ftrs_data_layer.logbase import DataMigrationLogBase
from ftrs_data_layer.repository.dynamodb import (
    AttributeLevelRepository,
    ModelType,
)
from rich.progress import track
from typer import Option, confirm

from dynamodb.utils import TargetEnvironment, get_table_name

reset_logger = Logger.get(service="reset")


class ClearableEntityTypes(StrEnum):
    organisation = "organisation"
    healthcare_service = "healthcare-service"
    location = "location"
    triage_code = "triage-code"


class RepositoryTypes(StrEnum):
    document = "document"
    field = "field"


DEFAULT_CLEARABLE_ENTITY_TYPES = [
    ClearableEntityTypes.organisation,
    ClearableEntityTypes.healthcare_service,
    ClearableEntityTypes.location,
    ClearableEntityTypes.triage_code,
]


def get_entity_cls(entity_type: ClearableEntityTypes) -> ModelType:
    """
    Map entity types to their corresponding classes.
    """
    match entity_type:
        case ClearableEntityTypes.organisation:
            return Organisation
        case ClearableEntityTypes.healthcare_service:
            return HealthcareService
        case ClearableEntityTypes.location:
            return Location
        case ClearableEntityTypes.triage_code:
            return TriageCode
        case _:
            reset_logger.log(
                DataMigrationLogBase.ETL_RESET_007, entity_type=entity_type
            )
            err_msg = reset_logger.format_message(
                DataMigrationLogBase.ETL_RESET_007, entity_type=entity_type
            )
            raise ValueError(err_msg)


def create_table(
    client: boto3.client,
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
    reset_logger.log(DataMigrationLogBase.ETL_RESET_003, table_name=table_name)


def init_tables(
    endpoint_url: str | None,
    env: TargetEnvironment,
    workspace: str | None,
    entity_type: List[ClearableEntityTypes],
) -> None:
    reset_logger.log(DataMigrationLogBase.ETL_RESET_001)

    if env != TargetEnvironment.local:
        reset_logger.log(DataMigrationLogBase.ETL_RESET_002)
        raise ValueError(DataMigrationLogBase.ETL_RESET_002.value.message)

    client = get_dynamodb_client(endpoint_url)
    for entity_name in entity_type:
        table_name = get_table_name(entity_name, env.value, workspace)
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
            reset_logger.log(DataMigrationLogBase.ETL_RESET_004, table_name=table_name)


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
    init: Annotated[
        bool | None,
        Option(help="Create tables if they do not exist (only for local env)"),
    ] = None,
    entity_type: Annotated[
        List[ClearableEntityTypes] | None,
        Option(help="Types of entities to clear from the database"),
    ] = None,
) -> None:
    """
    Reset the database by deleting all items in the specified table(s).
    This function is intended for use in development and local environments only.
    """
    if entity_type is None:
        entity_type = DEFAULT_CLEARABLE_ENTITY_TYPES

    if env not in [TargetEnvironment.dev, TargetEnvironment.local]:
        reset_logger.log(DataMigrationLogBase.ETL_RESET_005, env=env)
        raise ValueError()

    if init:
        init_tables(
            endpoint_url=endpoint_url,
            env=env,
            workspace=workspace,
            entity_type=entity_type,
        )

    confirm(
        f"Are you sure you want to reset the {env} environment (workspace: {workspace or 'default'})? This action cannot be undone.",
        abort=True,
    )

    for entity_name in entity_type:
        entity_cls = get_entity_cls(entity_name)
        table_name = get_table_name(entity_name, env.value, workspace)

        repository = AttributeLevelRepository(
            table_name=table_name,
            model_cls=entity_cls,
            endpoint_url=endpoint_url,
        )

        count = 0
        for item in track(
            repository.iter_records(max_results=None),
            description=f"Deleting items from {entity_name}",
            transient=True,
        ):
            repository.delete(item.id)
            count += 1

        reset_logger.log(
            DataMigrationLogBase.ETL_RESET_006, count=count, table_name=table_name
        )


def get_entity_config(entity_name: ClearableEntityTypes) -> dict:
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
