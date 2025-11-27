import os
from typing import Any, Dict, Literal

import pytest
from pytest_bdd import given, parsers, then, when
from sqlalchemy import text
from sqlmodel import Session

from utilities.common.data_migration.migration_context_helper import (
    build_supported_records_context,
    get_expected_dynamodb_table_names,
    get_migration_type_description,
    store_migration_result,
    store_sqs_result,
)
from utilities.common.data_migration.migration_helper import (
    MigrationHelper,
)
from utilities.common.data_migration.migration_metrics_helper import (
    ExpectedMetrics,
    verify_all_metrics,
)
from utilities.common.data_migration.migration_service_helper import (
    parse_and_create_service,
)
from utilities.common.data_migration.sqs_helper import (
    build_sqs_event,
)
from utilities.common.constants import (
    DYNAMODB_CLIENT,
    ENV_ENVIRONMENT,
    ENV_PROJECT_NAME,
    ENV_WORKSPACE,
    SERVICES_TABLE,
)
from utilities.common.log_helper import (
    get_mock_logger_from_context,
    verify_migration_completed_log,
    verify_service_not_migrated_log,
    verify_service_skipped_log,
    verify_transformation_log,
    verify_transformer_selected_log,
)


# ============================================================
# Setup Steps (Background)
# ============================================================


@given("the test environment is configured")
def environment_configured(
    migration_helper: MigrationHelper, dynamodb: Dict[str, Any]
) -> None:
    """Verify test environment is properly configured."""
    try:
        response = dynamodb[DYNAMODB_CLIENT].list_tables()
        table_names = response.get("TableNames", [])
        assert "TableNames" in response, "DynamoDB should be accessible"
    except Exception as e:
        pytest.fail(f"Failed to access DynamoDB: {e}")

    assert migration_helper is not None, "Migration helper should be configured"
    assert migration_helper.db_uri is not None, "Database URI should be set"
    assert (
        migration_helper.dynamodb_endpoint is not None
    ), "DynamoDB endpoint should be set"


@given("the DoS database has test data")
def dos_database_has_test_data(dos_db_with_migration: Session) -> None:
    """Verify DoS database is accessible and has tables."""
    result = dos_db_with_migration.exec(text(f"SELECT COUNT(*) FROM {SERVICES_TABLE}"))
    count = result.fetchone()[0]
    assert count >= 0, "Should be able to query services table"


@given("DynamoDB tables are ready")
def dynamodb_tables_ready(dynamodb: Dict[str, Any]) -> None:
    """Verify DynamoDB tables exist and are accessible."""
    client = dynamodb[DYNAMODB_CLIENT]
    response = client.list_tables()
    table_names = response.get("TableNames", [])

    expected_tables = get_expected_dynamodb_table_names()
    missing_tables = [table for table in expected_tables if table not in table_names]

    if missing_tables:
        project_name = os.getenv(ENV_PROJECT_NAME)
        environment = os.getenv(ENV_ENVIRONMENT)
        workspace = os.getenv(ENV_WORKSPACE)

        pytest.fail(
            f"Missing required DynamoDB tables: {', '.join(missing_tables)}\n"
            f"Found tables: {', '.join(table_names)}\n"
            f"Expected pattern: {project_name}-{environment}-database-{{resource}}-{workspace}"
        )


# ============================================================
# Service Creation Steps (Given)
# ============================================================


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
    return parse_and_create_service(
        dos_db_with_migration,
        migration_context,
        entity_type,
        entity_name,
        datatable,
    )


# ============================================================
# Migration Execution Steps (When)
# ============================================================


@when("the data migration process is run")
def full_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
) -> None:
    """Execute full service migration."""
    result = migration_helper.run_full_service_migration()
    store_migration_result(migration_context, result)


@when(
    parsers.parse("a single service migration is run for ID '{service_id:d}'"),
    target_fixture="migration_executed",
)
def single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: Dict[str, Any],
    service_id: int,
) -> None:
    """Execute migration for a single service."""
    result = migration_helper.run_single_service_migration(service_id)
    store_migration_result(migration_context, result, service_id)


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
    """Execute migration with SQS event built from minimal parameters."""
    event = build_sqs_event(
        table_name=table_name,
        record_id=record_id,
        service_id=record_id,
        method=method,
    )

    result = migration_helper.run_sqs_event_migration(event)
    store_sqs_result(migration_context, result, event, record_id)

    return {"event": event, "result": result}


# ============================================================
# Verification Steps (Then)
# ============================================================


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
def verify_migration_metrics(
    migration_context: Dict[str, Any],
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    migrated: int,
    skipped: int,
    errors: int,
) -> None:
    """Verify migration metrics match expected values."""
    result = migration_context["result"]

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    migration_type = get_migration_type_description(migration_context)
    additional_context = build_supported_records_context(migration_context)

    expected = ExpectedMetrics(
        total=total,
        supported=supported,
        unsupported=unsupported,
        transformed=transformed,
        migrated=migrated,
        skipped=skipped,
        errors=errors,
    )

    verify_all_metrics(
        actual_metrics=result.metrics,
        expected=expected,
        migration_type=migration_type,
        additional_context=additional_context,
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
    """Verify SQS event migration metrics match expected values."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    migration_type = get_migration_type_description(migration_context)

    expected = ExpectedMetrics(
        total=total,
        supported=supported,
        unsupported=unsupported,
        transformed=transformed,
        migrated=migrated,
        skipped=skipped,
        errors=errors,
    )

    verify_all_metrics(
        actual_metrics=result.metrics,
        expected=expected,
        migration_type=migration_type,
    )

    mock_logger = get_mock_logger_from_context(migration_context)
    verify_migration_completed_log(mock_logger)


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
    """Verify the correct transformer was selected for the service."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformer_selected_log(
        mock_logger=mock_logger,
        transformer_name=transformer_name,
        service_id=service_id,
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
    """Verify transformation output counts."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformation_log(
        mock_logger=mock_logger,
        service_id=service_id,
        organisation_count=org_count,
        location_count=location_count,
        healthcare_service_count=service_count,
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
    """Verify that a service was not migrated with the expected reason."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_service_not_migrated_log(
        mock_logger=mock_logger,
        service_id=service_id,
        expected_reason=expected_reason,
    )


@then(
    parsers.parse(
        "service ID '{service_id:d}' was skipped due to reason '{expected_reason}'"
    )
)
def verify_service_skipped(
    migration_context: Dict[str, Any],
    service_id: int,
    expected_reason: str,
) -> None:
    """Verify that a service was skipped with the expected reason."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_service_skipped_log(
        mock_logger=mock_logger,
        service_id=service_id,
        expected_reason=expected_reason,
    )
