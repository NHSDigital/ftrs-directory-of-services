"""BDD step definitions for DMS schema index creation tests."""

from typing import Dict

import pytest
from dms_provisioner.dms_service import create_indexes_from_sql_file
from pytest_bdd import given, parsers, scenarios, then, when
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import Session

scenarios("./data_migration_features/dms_schema_index_creation.feature")


@pytest.fixture
def dms_context(dos_db: Session) -> Dict:
    """Context for storing DMS test state."""
    bind = dos_db.get_bind()
    # If get_bind() returns a Connection, get the engine from it
    engine = bind.engine if hasattr(bind, "engine") else bind
    return {
        "db_session": dos_db,
        "engine": engine,
    }


@given(parsers.parse('the index "{index_name}" already exists on "{table_name}" table'))
def given_index_already_exists(
    dms_context: Dict, index_name: str, table_name: str
) -> None:
    """Create index to verify idempotency (index already exists scenario)."""
    engine: Engine = dms_context["engine"]
    # First create all indexes using the DMS provisioner
    create_indexes_from_sql_file(engine=engine)

    # Verify the specific index now exists
    dos_db: Session = dms_context["db_session"]
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
        {"table_name": table_name, "index_name": index_name},
    )
    existing_index = result.fetchone()
    assert existing_index is not None, (
        f"Index {index_name} should have been created and exist on {table_name}"
    )


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
        {"table_name": table_name, "index_name": index_name},
    )

    existing_index = result.fetchone()
    assert existing_index is not None, (
        f"Index {index_name} should exist on {table_name}"
    )
