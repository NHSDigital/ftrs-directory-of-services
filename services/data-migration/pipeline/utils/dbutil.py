from typing import Iterable

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.repository.base import ModelType
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from sqlalchemy import Engine
from sqlmodel import Session, select

from pipeline.utils.config import DataMigrationConfig

REPOSITORY_CACHE: dict[str, AttributeLevelRepository] = {}


def iter_records(
    engine: Engine, model_class: legacy, batch_size: int = 1000
) -> Iterable:
    """
    Iterate over records of a specific model class from the database.

    Args:
        model_class: The SQLModel class to query
        batch_size: Number of records to fetch at once

    Returns:
        Iterable of database records
    """
    stmt = select(model_class).execution_options(yield_per=batch_size)
    with Session(engine) as session:
        yield from session.scalars(stmt)

    # TODO: Remove this method and use the common function once merged by IS


def get_repository(
    config: DataMigrationConfig, entity_type: str, model_cls: ModelType, logger: Logger
) -> AttributeLevelRepository[ModelType]:
    """
    Get a DynamoDB repository for the specified table and model class.
    Caches the repository to avoid creating multiple instances for the same table.
    """
    table_name = f"ftrs-dos-{config.env}-database-{entity_type}"
    if config.workspace:
        table_name = f"{table_name}-{config.workspace}"

    if table_name not in REPOSITORY_CACHE:
        REPOSITORY_CACHE[table_name] = AttributeLevelRepository[ModelType](
            table_name=table_name,
            model_cls=model_cls,
            endpoint_url=config.dynamodb_endpoint,
            logger=logger,
        )
    return REPOSITORY_CACHE[table_name]
