from typing import TypeVar

from ftrs_common.logger import Logger
from ftrs_common.utils.config import Settings
from ftrs_data_layer.client import get_dynamodb_client
from ftrs_data_layer.domain import DBModel
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository

# Lazy initialization - Settings is created on first access, not at import time
_settings: Settings | None = None


def _get_settings() -> Settings:
    """Get or create the Settings instance lazily.
    
    This allows tests to set environment variables before Settings is created.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the cached Settings instance.
    
    This is primarily for testing - allows re-initializing Settings
    after environment variables have been changed.
    """
    global _settings
    _settings = None


DBModelT = TypeVar("DBModelT", bound=DBModel)


def get_service_repository(
    model_cls: type[DBModelT],
    entity_name: str,
    logger: Logger | None = None,
    endpoint_url: str | None = None,
) -> AttributeLevelRepository[DBModelT]:
    """
    Get a repository for the specified model and entity name.

    Args:
        model_cls: The model class (e.g., Organisation, HealthcareService).
        entity_name: The type of entity for the table name.

    Returns:
        AttributeLevelRepository[DBModelT]: The repository for the specified model.
    """
    settings = _get_settings()
    return AttributeLevelRepository[DBModelT](
        table_name=get_table_name(entity_name),
        model_cls=model_cls,
        endpoint_url=endpoint_url or settings.endpoint_url or None,
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
    settings = _get_settings()
    return format_table_name(
        entity_name=entity_name,
        env=settings.env,
        workspace=settings.workspace,
    )


def format_table_name(entity_name: str, env: str, workspace: str | None = None) -> str:
    """
    Format the DynamoDB table name based on the entity name, environment, and optional workspace.
    Data migration state tables don't use the -database- prefix

    Args:
        entity_name: The type of entity for the table name
        env: The environment (e.g., dev, test)
        workspace: The workspace (if any)

    Returns:
        str: The formatted table name
    """
    if entity_name.startswith("data-migration-"):
        table_name = f"ftrs-dos-{env}-{entity_name}"
    else:
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
