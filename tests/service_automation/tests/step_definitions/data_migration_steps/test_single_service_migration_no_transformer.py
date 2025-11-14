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
    run_verify_service_not_migrated,
)

scenarios("../../tests/features/data_migration_features/single_service_migration_no_transformer.feature")


@given("the test environment is configured")
def test_environment_configured(
    migration_helper: MigrationHelper, dynamodb: Dict[str, Any]
) -> None:
    run_test_environment_configured(migration_helper, dynamodb)


@given("the DoS database has test data")
def dos_database_has_test_data(dos_db_with_migration: Session) -> None:
    run_dos_database_has_test_data(dos_db_with_migration)


@given("DynamoDB tables are ready")
def dynamodb_tables_ready(dynamodb: Dict[str, Any]) -> None:
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
        "service ID '{service_id:d}' was not migrated due to reason '{expected_reason}'"
    )
)
def verify_service_not_migrated(
    migration_context: Dict[str, Any],
    service_id: int,
    expected_reason: str,
) -> None:
    run_verify_service_not_migrated(
        migration_context,
        service_id,
        expected_reason,
    )


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
    run_verify_transformation_output(
        migration_context,
        service_id,
        org_count,
        location_count,
        service_count,
    )
