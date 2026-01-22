"""BDD step definitions for DMS schema index creation tests."""
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
def dms_context(dos_db: Session) -> Dict:
    """Context for storing DMS test state."""
    return {
        "db_session": dos_db,
        "engine": dos_db.get_bind(),
        "tables_with_indexes": {},
        "error_occurred": False,
    }


@given("the database has schema and data from source")
def given_database_with_migration(dos_db: Session, dms_context: Dict) -> None:
    """Verify database is loaded with migrated schema and data."""
    # Verify pathwaysdos schema exists
    result = dos_db.execute(
        text(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'pathwaysdos'"
        )
    )
    assert result.fetchone() is not None, "pathwaysdos schema should exist"


@given(parsers.parse('the "{table_name}" table exists with data'))
def given_table_exists_with_data(
    dos_db: Session, dms_context: Dict, table_name: str
) -> None:
    """Verify specified table exists (data is optional - some tables may be empty)."""
    # Check table exists
    result = dos_db.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'pathwaysdos'
            AND table_name = :table_name
            """
        ),
        {"table_name": table_name}
    )
    assert result.fetchone() is not None, f"Table {table_name} should exist"


@given(parsers.parse('all indexes are dropped from "{table_name}" table'))
def given_indexes_dropped_from_table(
    dos_db: Session, dms_context: Dict, table_name: str
) -> None:
    """Drop all indexes from specified table except constraint-based indexes."""
    # Get all indexes for the table, excluding those created by constraints
    # (primary key, foreign key, unique constraints)
    result = dos_db.execute(
        text(
            """
            SELECT i.indexname
            FROM pg_indexes i
            LEFT JOIN pg_constraint c ON i.indexname = c.conname
            WHERE i.schemaname = 'pathwaysdos'
            AND i.tablename = :table_name
            AND c.conname IS NULL
            AND i.indexname NOT LIKE '%_pkey'
            AND i.indexname NOT LIKE '%_fkey'
            """
        ),
        {"table_name": table_name}
    )

    indexes_before = [row[0] for row in result.fetchall()]
    dms_context["tables_with_indexes"][table_name] = {
        "indexes_before": indexes_before,
        "dropped_count": 0,
    }

    # Drop each index (safe to drop - not constraint-based)
    for index_name in indexes_before:
        # SQL identifiers cannot be parameterized, but index_name comes from pg_indexes query
        # which ensures it's a valid identifier
        dos_db.execute(
            text(f"DROP INDEX IF EXISTS pathwaysdos.{index_name}")
        )
        dms_context["tables_with_indexes"][table_name]["dropped_count"] += 1

    dos_db.commit()


@given(parsers.parse('the index "{index_name}" already exists on "{table_name}" table'))
def given_index_already_exists(
    dos_db: Session, dms_context: Dict, index_name: str, table_name: str
) -> None:
    """Verify specific index already exists on table (for idempotency test)."""
    # Check if index exists
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

    # If it doesn't exist, create it by calling the provisioner
    if existing_index is None:
        engine: Engine = dms_context["engine"]
        create_indexes_from_sql_file(engine=engine)

        # Verify it was created
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
        assert existing_index is not None, f"Index {index_name} should exist on {table_name} after creation"

    dms_context.setdefault("indexes_before", {})[index_name] = True


@given(parsers.parse('all indexes are already created on "{table_name}" table'))
def given_indexes_already_created(
    dos_db: Session, dms_context: Dict, table_name: str
) -> None:
    """Verify indexes already exist on table (for idempotency test)."""
    # Get current indexes (excluding constraint-based ones)
    result = dos_db.execute(
        text(
            """
            SELECT COUNT(*)
            FROM pg_indexes i
            LEFT JOIN pg_constraint c ON i.indexname = c.conname
            WHERE i.schemaname = 'pathwaysdos'
            AND i.tablename = :table_name
            AND c.conname IS NULL
            AND i.indexname NOT LIKE '%_pkey'
            AND i.indexname NOT LIKE '%_fkey'
            """
        ),
        {"table_name": table_name}
    )
    count = result.fetchone()[0]
    dms_context["tables_with_indexes"][table_name] = {
        "indexes_before": count,
        "should_be_idempotent": True,
    }


@given("all INDEXES_TABLES exist with data")
def given_all_indexes_tables_exist(
    dos_db: Session, dms_context: Dict
) -> None:
    """Verify all tables in INDEXES_TABLES list exist (data is optional)."""
    for table_name in INDEXES_TABLES:
        # Check table exists
        result = dos_db.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'pathwaysdos'
                AND table_name = :table_name
                """
            ),
            {"table_name": table_name}
        )
        assert result.fetchone() is not None, f"Table {table_name} should exist"


@given("all indexes are dropped from all INDEXES_TABLES")
def given_indexes_dropped_from_all_tables(
    dos_db: Session, dms_context: Dict
) -> None:
    """Drop all indexes from all tables in INDEXES_TABLES list (excluding constraint-based)."""
    total_dropped = 0

    for table_name in INDEXES_TABLES:
        # Get all indexes for the table, excluding constraint-based indexes
        result = dos_db.execute(
            text(
                """
                SELECT i.indexname
                FROM pg_indexes i
                LEFT JOIN pg_constraint c ON i.indexname = c.conname
                WHERE i.schemaname = 'pathwaysdos'
                AND i.tablename = :table_name
                AND c.conname IS NULL
                AND i.indexname NOT LIKE '%_pkey'
                AND i.indexname NOT LIKE '%_fkey'
                """
            ),
            {"table_name": table_name}
        )

        indexes = [row[0] for row in result.fetchall()]

        # Drop each index
        for index_name in indexes:
            # SQL identifiers cannot be parameterized, but index_name comes from pg_indexes query
            # which ensures it's a valid identifier
            dos_db.execute(
                text(f"DROP INDEX IF EXISTS pathwaysdos.{index_name}")
            )
            total_dropped += 1

    dos_db.commit()
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


@then(parsers.parse('the index "{index_name}" should exist on "{table_name}" table'))
def then_index_exists_on_table(
    dos_db: Session, dms_context: Dict, index_name: str, table_name: str
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

    index_found = result.fetchone()
    assert index_found is not None, f"Index {index_name} should exist on table {table_name}"


@then(parsers.parse('all indexes should exist on "{table_name}" table'))
def then_indexes_exist_on_table(
    dos_db: Session, dms_context: Dict, table_name: str
) -> None:
    """Verify indexes were created on specified table."""
    # Get indexes after provisioning (excluding constraint-based indexes)
    result = dos_db.execute(
        text(
            """
            SELECT i.indexname
            FROM pg_indexes i
            LEFT JOIN pg_constraint c ON i.indexname = c.conname
            WHERE i.schemaname = 'pathwaysdos'
            AND i.tablename = :table_name
            AND c.conname IS NULL
            AND i.indexname NOT LIKE '%_pkey'
            AND i.indexname NOT LIKE '%_fkey'
            """
        ),
        {"table_name": table_name}
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
    dos_db: Session, dms_context: Dict
) -> None:
    """Verify all tables in INDEXES_TABLES have indexes."""
    tables_with_indexes = 0

    for table_name in INDEXES_TABLES:
        result = dos_db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM pg_indexes i
                LEFT JOIN pg_constraint c ON i.indexname = c.conname
                WHERE i.schemaname = 'pathwaysdos'
                AND i.tablename = :table_name
                AND c.conname IS NULL
                AND i.indexname NOT LIKE '%_pkey'
                AND i.indexname NOT LIKE '%_fkey'
                """
            ),
            {"table_name": table_name}
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
