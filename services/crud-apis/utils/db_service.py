from ftrs_data_layer.models import DBModel
from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository

from utils.config import Settings

env_variable_settings = Settings()


def get_service_repository(
    model_cls: type[DBModel], entity_name: str
) -> DocumentLevelRepository[DBModel]:
    """
    Get a repository for the specified model and entity name.

    Args:
        model_cls: The model class (e.g., Organisation, HealthcareService).
        entity_name: The type of entity for the table name.

    Returns:
        DocumentLevelRepository[DBModel]: The repository for the specified model.
    """
    return DocumentLevelRepository[DBModel](
        table_name=get_table_name(entity_name),
        model_cls=model_cls,
        endpoint_url=env_variable_settings.endpoint_url or None,
    )


def get_table_name(entity_name: str) -> str:
    """
    Build a DynamoDB table name based on the entity name, environment, and optional workspace.

    Args:
        entity_name: The type of entity for the table name

    Returns:
        str: The constructed table name
    """

    table_name = f"ftrs-dos-{env_variable_settings.env}-database-{entity_name}"
    if env_variable_settings.workspace:
        table_name = f"{table_name}-{env_variable_settings.workspace}"
    return table_name
