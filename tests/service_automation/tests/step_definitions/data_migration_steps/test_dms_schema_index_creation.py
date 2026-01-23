"""BDD step definitions for DMS schema index creation tests."""
from typing import Dict, List

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

import sys
from pathlib import Path

data_migration_src = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "services"
    / "data-migration"
    / "src"
)
sys.path.insert(0, str(data_migration_src))

from dms_provisioner.dms_service import create_indexes_from_sql_file

# Load all scenarios from the feature file
scenarios("./data_migration_features/dms_schema_index_creation.feature")


@pytest.fixture
def dms_context(dos_db: Session) -> Dict:
    """Context for storing DMS test state."""
    return {
        "db_session": dos_db,
        "engine": dos_db.get_bind(),
    }


@given("the database has schema and data from source")
def given_database_with_migration(dos_db: Session) -> None:
    """Verify database is loaded with migrated schema and data."""
    # Verify pathwaysdos schema exists
    result = dos_db.execute(
        text(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pathwaysdos'"
        )
    )
    assert result.fetchone() is not None, "pathwaysdos schema should exist"


@given(parsers.parse('the index "{index_name}" already exists on "{table_name}" table'))
def given_index_already_exists(
    dos_db: Session, index_name: str, table_name: str
) -> None:
    """Verify specific index already exists on table (for idempotency test)."""
    result = dos_db.execute(
        text(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'pathwaysdos'
            AND tablename = :table_name
            AND indexname = :index_name
            """
        ),
        {"table_name": table_name, "index_name": index_name}
    )
    existing_index = result.fetchone()
    assert existing_index is not None, f"Index {index_name} should already exist on {table_name}"


@when("the DMS provisioner creates indexes from schema file")
def when_dms_provisioner_creates_indexes(dms_context: Dict) -> None:
    """Execute the DMS provisioner function to create indexes."""
    engine: Engine = dms_context["engine"]
    create_indexes_from_sql_file(engine=engine)


@then(parsers.parse('the index "{index_name}" should exist on "{table_name}" table'))
def then_index_exists_on_table(
    dos_db: Session, index_name: str, table_name: str
) -> None:
    """Verify specific index exists on specified table."""
    result = dos_db.execute(
        text(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'pathwaysdos'
            AND tablename = :table_name
            AND indexname = :index_name
            """
        ),
        {"table_name": table_name, "index_name": index_name}
    )

    existing_index = result.fetchone()
    assert existing_index is not None, f"Index {index_name} should exist on {table_name}"
