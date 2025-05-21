from ftrs_data_layer.models import HealthcareService, DBModel
from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository

from utils.config import get_env_variables


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
    env_vars = get_env_variables()
    return DocumentLevelRepository[DBModel](
        table_name=get_table_name(entity_name),
        model_cls=model_cls,
        endpoint_url=env_vars["endpoint_url"],
    )


def get_table_name(entity_name: str) -> str:
    """
    Build a DynamoDB table name based on the entity name, environment, and optional workspace.

    Args:
        entity_name: The type of entity for the table name

    Returns:
        str: The constructed table name
    """
    env_vars = get_env_variables()

    table_name = f"ftrs-dos-{env_vars['env']}-database-{entity_name}"
    if env_vars.get("workspace"):
        table_name = f"{table_name}-{env_vars['workspace']}"
    return table_name
