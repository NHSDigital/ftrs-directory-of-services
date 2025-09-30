import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from sqlalchemy import text


# Load scenarios from feature files
scenarios('./data_migration_features/load_dos_schema_data_to_testcontainer.feature')


@given('I have a database with migrated data')
def database_with_migrated_data(migration_context):
    """Set up context with migrated database."""
    # Verify we have migrated data
    result = migration_context["db_session"].exec(
        text("SELECT COUNT(*) FROM pathwaysdos.servicetypes")
    )
    count = result.fetchone()[0]
    assert count > 0, "Database should have migrated data"
    return migration_context


@when(parsers.parse('I query the "{table_name}" table'))
def query_table(migration_context, table_name):
    """Query a specific table."""
    result = migration_context["db_session"].exec(
        text(f"SELECT COUNT(*) FROM pathwaysdos.{table_name}")
    )
    count = result.fetchone()[0]
    migration_context["results"][f"{table_name}_count"] = count


@then(parsers.parse('the "{table_name}" table should have data'))
def table_should_have_data(migration_context, table_name):
    """Verify table has data."""
    count = migration_context["results"].get(f"{table_name}_count", 0)
    assert count > 0, f"Table {table_name} should contain data"
