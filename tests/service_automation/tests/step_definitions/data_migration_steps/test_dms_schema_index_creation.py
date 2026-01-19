"""BDD step definitions for DMS schema index creation tests (FTRS-1708)."""
from typing import Dict, List

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

# Import the DMS provisioner function we're testing
import sys
from pathlib import Path

# Add services/data-migration/src to path to import dms_provisioner
data_migration_src = (
    Path(__file__).parent.parent.parent.parent.parent.parent
    / "services"
    / "data-migration"
    / "src"
)
sys.path.insert(0, str(data_migration_src))

from dms_provisioner.dms_service import INDEXES_TABLES, create_indexes_from_sql_file

# Load all scenarios from the feature file
scenarios("./data_migration_features/dms_schema_index_creation.feature")


@pytest.fixture
def dms_context(dos_db_with_migration: Session) -> Dict:
    """Context for storing DMS test state."""
    return {
        "db_session": dos_db_with_migration,
        "engine": dos_db_with_migration.get_bind(),
        "tables_with_indexes": {},
        "error_occurred": False,
    }


@given("the database has schema and data from source")
def given_database_with_migration(dos_db_with_migration: Session, dms_context: Dict) -> None:
    """Verify database is loaded with migrated schema and data."""
    # Verify pathwaysdos schema exists
    result = dos_db_with_migration.execute(
        text(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pathwaysdos'"
        )
    )
    assert result.fetchone() is not None, "pathwaysdos schema should exist"


@given(parsers.parse('the "{table_name}" table exists with data'))
def given_table_exists_with_data(
    dos_db_with_migration: Session, dms_context: Dict, table_name: str
) -> None:
    """Verify specified table exists (data is optional - some tables may be empty)."""
    # Check table exists
    result = dos_db_with_migration.execute(
        text(
            f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'pathwaysdos'
            AND table_name = '{table_name}'
            """
        )
    )
    assert result.fetchone() is not None, f"Table {table_name} should exist"


@given(parsers.parse('all indexes are dropped from "{table_name}" table'))
def given_indexes_dropped_from_table(
    dos_db_with_migration: Session, dms_context: Dict, table_name: str
) -> None:
    """Drop all indexes from specified table except constraint-based indexes."""
    # Get all indexes for the table, excluding those created by constraints
    # (primary key, foreign key, unique constraints)
    result = dos_db_with_migration.execute(
        text(
            f"""
            SELECT i.indexname
            FROM pg_indexes i
            LEFT JOIN pg_constraint c ON i.indexname = c.conname
            WHERE i.schemaname = 'pathwaysdos'
            AND i.tablename = '{table_name}'
            AND c.conname IS NULL
            AND i.indexname NOT LIKE '%_pkey'
            AND i.indexname NOT LIKE '%_fkey'
            """
        )
    )

    indexes_before = [row[0] for row in result.fetchall()]
    dms_context["tables_with_indexes"][table_name] = {
        "indexes_before": indexes_before,
        "dropped_count": 0,
    }

    # Drop each index (safe to drop - not constraint-based)
    for index_name in indexes_before:
        dos_db_with_migration.execute(
            text(f"DROP INDEX IF EXISTS pathwaysdos.{index_name}")
        )
        dms_context["tables_with_indexes"][table_name]["dropped_count"] += 1

    dos_db_with_migration.commit()


@given(parsers.parse('all indexes are already created on "{table_name}" table'))
def given_indexes_already_created(
    dos_db_with_migration: Session, dms_context: Dict, table_name: str
) -> None:
    """Verify indexes already exist on table (for idempotency test)."""
    # Get current indexes (excluding constraint-based ones)
    result = dos_db_with_migration.execute(
        text(
            f"""
            SELECT COUNT(*)
            FROM pg_indexes i
            LEFT JOIN pg_constraint c ON i.indexname = c.conname
            WHERE i.schemaname = 'pathwaysdos'
            AND i.tablename = '{table_name}'
            AND c.conname IS NULL
            AND i.indexname NOT LIKE '%_pkey'
            AND i.indexname NOT LIKE '%_fkey'
            """
        )
    )
    count = result.fetchone()[0]
    dms_context["tables_with_indexes"][table_name] = {
        "indexes_before": count,
        "should_be_idempotent": True,
    }


@given("all INDEXES_TABLES exist with data")
def given_all_indexes_tables_exist(
    dos_db_with_migration: Session, dms_context: Dict
) -> None:
    """Verify all tables in INDEXES_TABLES list exist (data is optional)."""
    for table_name in INDEXES_TABLES:
        # Check table exists
        result = dos_db_with_migration.execute(
            text(
                f"""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'pathwaysdos'
                AND table_name = '{table_name}'
                """
            )
        )
        assert result.fetchone() is not None, f"Table {table_name} should exist"


@given("all indexes are dropped from all INDEXES_TABLES")
def given_indexes_dropped_from_all_tables(
    dos_db_with_migration: Session, dms_context: Dict
) -> None:
    """Drop all indexes from all tables in INDEXES_TABLES list (excluding constraint-based)."""
    total_dropped = 0

    for table_name in INDEXES_TABLES:
        # Get all indexes for the table, excluding constraint-based indexes
        result = dos_db_with_migration.execute(
            text(
                f"""
                SELECT i.indexname
                FROM pg_indexes i
                LEFT JOIN pg_constraint c ON i.indexname = c.conname
                WHERE i.schemaname = 'pathwaysdos'
                AND i.tablename = '{table_name}'
                AND c.conname IS NULL
                AND i.indexname NOT LIKE '%_pkey'
                AND i.indexname NOT LIKE '%_fkey'
                """
            )
        )

        indexes = [row[0] for row in result.fetchall()]

        # Drop each index
        for index_name in indexes:
            dos_db_with_migration.execute(
                text(f"DROP INDEX IF EXISTS pathwaysdos.{index_name}")
            )
            total_dropped += 1

    dos_db_with_migration.commit()
    dms_context["total_indexes_dropped"] = total_dropped


@when("the DMS provisioner creates indexes from schema file")
def when_dms_provisioner_creates_indexes(dms_context: Dict) -> None:
    """Execute the DMS provisioner function to create indexes."""
    engine: Engine = dms_context["engine"]

    try:
        # Call the actual function from dms_provisioner module
        # Uses INDEXES_TABLES and default SCHEMA_FILE path
        create_indexes_from_sql_file(engine=engine)
        dms_context["error_occurred"] = False
    except Exception as e:
        dms_context["error_occurred"] = True
        dms_context["error"] = str(e)


@then(parsers.parse('all indexes should exist on "{table_name}" table'))
def then_indexes_exist_on_table(
    dos_db_with_migration: Session, dms_context: Dict, table_name: str
) -> None:
    """Verify indexes were created on specified table."""
    # Get indexes after provisioning (excluding constraint-based indexes)
    result = dos_db_with_migration.execute(
        text(
            f"""
            SELECT i.indexname
            FROM pg_indexes i
            LEFT JOIN pg_constraint c ON i.indexname = c.conname
            WHERE i.schemaname = 'pathwaysdos'
            AND i.tablename = '{table_name}'
            AND c.conname IS NULL
            AND i.indexname NOT LIKE '%_pkey'
            AND i.indexname NOT LIKE '%_fkey'
            """
        )
    )

    indexes_after = [row[0] for row in result.fetchall()]

    # Verify at least some indexes were created
    assert (
        len(indexes_after) > 0
    ), f"Table {table_name} should have indexes after provisioning"

    # If we tracked indexes before dropping, verify they're restored
    if table_name in dms_context["tables_with_indexes"]:
        table_info = dms_context["tables_with_indexes"][table_name]
        if "indexes_before" in table_info and isinstance(
            table_info["indexes_before"], list
        ):
            indexes_before = table_info["indexes_before"]
            # Verify all original indexes are restored
            for original_index in indexes_before:
                assert (
                    original_index in indexes_after
                ), f"Index {original_index} should be restored on {table_name}"


@then("all INDEXES_TABLES should have their indexes created")
def then_all_tables_have_indexes(
    dos_db_with_migration: Session, dms_context: Dict
) -> None:
    """Verify all tables in INDEXES_TABLES have indexes."""
    tables_with_indexes = 0

    for table_name in INDEXES_TABLES:
        result = dos_db_with_migration.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM pg_indexes i
                LEFT JOIN pg_constraint c ON i.indexname = c.conname
                WHERE i.schemaname = 'pathwaysdos'
                AND i.tablename = '{table_name}'
                AND c.conname IS NULL
                AND i.indexname NOT LIKE '%_pkey'
                AND i.indexname NOT LIKE '%_fkey'
                """
            )
        )
        count = result.fetchone()[0]

        if count > 0:
            tables_with_indexes += 1

    # All 9 tables should have indexes
    assert (
        tables_with_indexes == len(INDEXES_TABLES)
    ), f"All {len(INDEXES_TABLES)} tables should have indexes (found {tables_with_indexes})"


@then("no errors should occur")
def then_no_errors_occur(dms_context: Dict) -> None:
    """Verify no errors occurred during index creation."""
    assert not dms_context[
        "error_occurred"
    ], f"No errors should occur: {dms_context.get('error', '')}"
