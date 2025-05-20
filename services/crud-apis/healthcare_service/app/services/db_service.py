from ftrs_data_layer.models import HealthcareService
from ftrs_data_layer.repository.dynamodb import DocumentLevelRepository

from healthcare_service.app.config import get_env_variables


def get_healthcare_service_repository() -> DocumentLevelRepository[HealthcareService]:
    env_vars = get_env_variables()
    return DocumentLevelRepository[HealthcareService](
        table_name=get_table_name(env_vars["entity_name"]),
        model_cls=HealthcareService,
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
    print(table_name)

    return table_name
