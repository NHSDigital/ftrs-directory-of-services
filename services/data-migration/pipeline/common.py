from enum import StrEnum
from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache
def get_db_engine(connection_uri: str) -> Engine:
    return create_engine(connection_uri)


def get_table_name(entity_type: str, env: str, workspace: str | None = None) -> str:
    """
    Build a DynamoDB table name based on the entity type, environment, and optional workspace.
    """
    table_name = f"ftrs-dos-db-{env}-{entity_type}"
    if workspace:
        table_name = f"{table_name}-{workspace}"

    return table_name


class Constants:
    GP_PRACTICE_EXTRACT = "dos-gp-practice-extract"
    GP_PRACTICE_TRANSFORM = "dos-gp-practice-transform"

    GP_PRACTICE_EXTRACT_FILE = f"{GP_PRACTICE_EXTRACT}.parquet"
    GP_PRACTICE_TRANSFORM_FILE = f"{GP_PRACTICE_TRANSFORM}.parquet"


class TargetEnvironment(StrEnum):
    local = "local"
    dev = "dev"
