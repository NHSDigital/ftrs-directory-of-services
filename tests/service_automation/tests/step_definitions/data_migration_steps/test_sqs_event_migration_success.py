"""BDD step definitions for running single service migration."""
from typing import Any, Dict

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from sqlmodel import Session

from utilities.common.migration_helper import MigrationHelper
from utilities.common.data_migration_shared_steps import (
    run_create_service_with_attributes,
    run_dos_database_has_test_data,
    run_dynamodb_tables_ready,
    run_test_environment_configured,
    run_sqs_event_migration,
    run_verify_sqs_event_metrics,
)

scenarios("../../tests/features/data_migration_features/sqs_event_migration_success.feature")


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

@when(
    "the data migration process is run with the event:",
    target_fixture="sqs_event_processed",
)
def sqs_event_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    docstring: str,
    capfd: pytest.CaptureFixture[str],
) -> Dict[str, Any]:
    run_sqs_event_migration(
        migration_helper,
        migration_context,
        docstring,
        capfd,
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
