from enum import StrEnum


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"


def get_table_name(entity_type: str, env: str, workspace: str | None = None) -> str:
    """
    Build a DynamoDB table name based on the entity type, environment, and optional workspace.
    """
    if not entity_type or not env:
        raise ValueError("Entity type and environment must be provided.")

    table_name = f"ftrs-dos-{env}-database-{entity_type}"
    if workspace:
        table_name = f"{table_name}-{workspace}"

    return table_name
