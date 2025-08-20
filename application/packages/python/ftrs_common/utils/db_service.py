from typing import TypeVar

from ftrs_common.logger import Logger
from ftrs_common.utils.config import Settings
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

env_variable_settings = Settings()


DBModelT = TypeVar("DBModelT", bound=DBModel)


def get_service_repository(
    model_cls: type[DBModelT],
    entity_name: str,
    logger: Logger | None = None,
) -> AttributeLevelRepository[DBModelT]:
    """
    Get a repository for the specified model and entity name.

    Args:
        model_cls: The model class (e.g., Organisation, HealthcareService).
        entity_name: The type of entity for the table name.

    Returns:
        AttributeLevelRepository[DBModelT]: The repository for the specified model.
    """
    return AttributeLevelRepository[DBModelT](
        table_name=get_table_name(entity_name),
        model_cls=model_cls,
        endpoint_url=env_variable_settings.endpoint_url or None,
        logger=logger,
    )


def get_table_name(entity_name: str) -> str:
    """
    Build a DynamoDB table name based on the entity name, environment, and optional workspace.

    Args:
        entity_name: The type of entity for the table name

    Returns:
        str: The constructed table name
    """
    return format_table_name(
        entity_name=entity_name,
        env=env_variable_settings.env,
        workspace=env_variable_settings.workspace,
    )


def format_table_name(entity_name: str, env: str, workspace: str | None = None) -> str:
    """
    Format the DynamoDB table name based on the entity name, environment, and optional workspace.

    Args:
        entity_name: The type of entity for the table name
        env: The environment (e.g., dev, test)
        workspace: The workspace (if any)

    Returns:
        str: The formatted table name
    """
    table_name = f"ftrs-dos-{env}-database-{entity_name}"
    if workspace:
        table_name = f"{table_name}-{workspace}"
    return table_name


def get_table_arn(table_name: str) -> str:
    """
    Get the ARN of a DynamoDB table
    """
    client = get_dynamodb_client()
    response = client.describe_table(TableName=table_name)
    return response["Table"]["TableArn"]
