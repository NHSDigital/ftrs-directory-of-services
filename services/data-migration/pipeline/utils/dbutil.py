from typing import Iterable

from ftrs_common.logger import Logger
from ftrs_data_layer.domain import legacy
from ftrs_data_layer.domain.legacy import SymptomGroupSymptomDiscriminator
from ftrs_data_layer.repository.base import ModelType
from ftrs_data_layer.repository.dynamodb import AttributeLevelRepository
from sqlalchemy import Engine, create_engine, distinct
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from pipeline.utils.config import DatabaseConfig, DataMigrationConfig

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


def get_all_symptom_groups(engine: Engine) -> list[int]:
    """
    Fetch all unique symptom group IDs from the SymptomGroupSymptomDiscriminator table.

    Args:
        engine: Database engine

    Returns:
        List of unique symptom group IDs
    """
    stmt = select(distinct(SymptomGroupSymptomDiscriminator.symptomgroupid))
    with Session(engine) as session:
        result = session.scalars(stmt)
    return list(result.all())


def get_symptom_discriminators_for_symptom_group(
    engine: Engine, symptom_group_id: int
) -> list[SymptomGroupSymptomDiscriminator]:
    """
    Fetch all symptom discriminator mappings for a specific symptom group.

    Args:
        engine: Database engine
        symptom_group_id: ID of the symptom group to fetch discriminators for

    Returns:
        List of SymptomGroupSymptomDiscriminator records
    """
    query = (
        select(SymptomGroupSymptomDiscriminator)
        .where(SymptomGroupSymptomDiscriminator.symptomgroupid == symptom_group_id)
        .options(
            joinedload(SymptomGroupSymptomDiscriminator.symptomgroup),
            joinedload(SymptomGroupSymptomDiscriminator.symptomdiscriminator),
        )
    )
    with Session(engine) as session:
        result = session.scalars(query)
        return list(result.all())


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


def get_sqlalchemy_engine_from_config(db_config: DatabaseConfig) -> Engine:
    """Create and configure an SQLAlchemy engine from DatabaseConfig with optimized settings."""
    return create_engine(
        db_config.connection_string,
        # Connection pool settings for better performance
        pool_size=10,  # Number of connections to maintain in a pool
        max_overflow=20,  # Additional connections beyond pool_size
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=3600,  # Recycle connections after 1 hour
        # Connection timeout settings
        connect_args={
            "connect_timeout": 30,  # Connection timeout in seconds
            "application_name": "dms_pipeline",  # Identify your application in pg_stat_activity
        },
        # Enable connection pooling optimizations
        pool_reset_on_return="commit",  # Reset connections on return to pool
    )
