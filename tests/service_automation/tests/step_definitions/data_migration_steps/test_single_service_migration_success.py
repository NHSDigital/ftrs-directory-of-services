"""BDD step definitions for running single service migration."""
from typing import Any, Dict

from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from utilities.common.migration_helper import MigrationHelper
from utilities.common.data_migration_shared_steps import (
    run_create_service_with_attributes,
    run_dos_database_has_test_data,
    run_dynamodb_tables_ready,
    run_test_environment_configured,
    run_single_service_migration,
    run_verify_migration_metrics_inline,
    run_verify_transformation_output,
    run_verify_transformer_selected,
)

scenarios("../../tests/features/data_migration_features/single_service_migration_success.feature")


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


@given(
    parsers.parse(
        "a '{entity_type}' exists called '{entity_name}' in DoS with attributes:"
    ),
    target_fixture="service_created",
)
def create_service_with_attributes(
    dos_db_with_migration: Session,
    migration_context: Dict[str, Any],
    entity_type: str,
    entity_name: str,
    datatable: list[list[str]],
) -> Dict[str, Any]:
    """Create a service in DoS database with attributes from Gherkin table."""
    run_create_service_with_attributes(
        dos_db_with_migration,
        migration_context,
        entity_type,
        entity_name,
        datatable,
    )


@when(parsers.parse("a single service migration is run for ID '{service_id:d}'"))
def single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Execute migration for a single service and capture output."""
    run_single_service_migration(
        migration_helper,
        migration_context,
        service_id,
    )


@then(
    parsers.parse(
        "the metrics should be "
        "{total:d} total, "
        "{supported:d} supported, "
        "{unsupported:d} unsupported, "
        "{transformed:d} transformed, "
        "{migrated:d} migrated, "
        "{skipped:d} skipped and "
        "{errors:d} errors"
    )
)
def verify_migration_metrics_inline(
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
    Verify migration metrics match expected values.

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
        AssertionError: If any metric doesn't match expected value
    """
    run_verify_migration_metrics_inline(
        migration_context,
        total,
        supported,
        unsupported,
        transformed,
        migrated,
        skipped,
        errors,
    )


@then(
    parsers.parse(
        "the '{transformer_name}' was selected for service ID '{service_id:d}'"
    )
)
def verify_transformer_selected(
    migration_context: Dict[str, Any],
    transformer_name: str,
    service_id: int,
) -> None:
    run_verify_transformer_selected(migration_context, transformer_name, service_id)


@then(
    parsers.parse(
        "service ID '{service_id:d}' was transformed into "
        "{org_count:d} organisation, "
        "{location_count:d} location and "
        "{service_count:d} healthcare service"
    )
)
def verify_transformation_output(
    migration_context: Dict[str, Any],
    service_id: int,
    org_count: int,
    location_count: int,
    service_count: int,
) -> None:
    """Verify that a service was transformed into the expected number of resources."""
    run_verify_transformation_output(
        migration_context,
        service_id,
        org_count,
        location_count,
        service_count,
    )
