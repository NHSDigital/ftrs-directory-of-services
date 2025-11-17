from typing import Any, Dict, Literal

from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from utilities.common.migration_helper import MigrationHelper
from utilities.common.data_migration_shared_steps import (
    run_dos_database_has_test_data,
    run_dynamodb_tables_ready,
    run_test_environment_configured,
    run_sqs_event_migration_with_params,
    run_verify_sqs_event_metrics,
)

scenarios(
    "../../tests/features/data_migration_features/sqs_event_migration_success.feature"
)


@given("the test environment is configured")
def test_environment_configured(
    migration_helper: MigrationHelper, dynamodb: Dict[str, Any]
) -> None:
    """Verify test environment is properly configured."""
    run_test_environment_configured(migration_helper, dynamodb)


@given("the DoS database has test data")
def dos_database_has_test_data(dos_db_with_migration: Session) -> None:
    """Verify DoS database is accessible and has tables."""
    run_dos_database_has_test_data(dos_db_with_migration)


@given("DynamoDB tables are ready")
def dynamodb_tables_ready(dynamodb: Dict[str, Any]) -> None:
    """Verify DynamoDB tables exist and are accessible."""
    run_dynamodb_tables_ready(dynamodb)


@when(
    parsers.parse(
        "the data migration process is run for table '{table_name}', "
        "ID '{record_id:d}' and method '{method}'"
    ),
    target_fixture="sqs_event_processed",
)
def sqs_event_migration_with_params(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    table_name: str,
    record_id: int,
    method: Literal["insert", "update", "delete"],
) -> Dict[str, Any]:
    """
    Execute migration with SQS event built from minimal parameters.

    This step constructs an SQS event internally using the provided parameters,
    eliminating the need for verbose JSON payloads in feature files.

    Args:
        migration_helper: Helper for running migrations
        migration_context: Test context dictionary
        table_name: Name of the database table (e.g., 'services')
        record_id: Database record ID to process
        method: DMS operation type ('insert', 'update', or 'delete')

    Returns:
        Dictionary containing event and result
    """
    return run_sqs_event_migration_with_params(
        migration_helper,
        migration_context,
        table_name,
        record_id,
        method,
    )


@then(
    parsers.parse(
        "the SQS event metrics should be "
        "{total:d} total, "
        "{supported:d} supported, "
        "{unsupported:d} unsupported, "
        "{transformed:d} transformed, "
        "{migrated:d} migrated, "
        "{skipped:d} skipped and "
        "{errors:d} errors"
    )
)
def verify_sqs_event_metrics(
    migration_context: Dict[str, Any],
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    migrated: int,
    skipped: int,
    errors: int,
) -> None:
    """
    Verify SQS event migration metrics match expected values.

    Also verifies DM_ETL_999 completion log is present.

    Args:
        migration_context: Test context dictionary
        total: Expected total_records count
        supported: Expected supported_records count
        unsupported: Expected unsupported_records count
        transformed: Expected transformed_records count
        migrated: Expected migrated_records count
        skipped: Expected skipped_records count
        errors: Expected errors count

    Raises:
        AssertionError: If any metric doesn't match or completion log missing
    """
    run_verify_sqs_event_metrics(
        migration_context,
        total,
        supported,
        unsupported,
        transformed,
        migrated,
        skipped,
        errors,
    )
