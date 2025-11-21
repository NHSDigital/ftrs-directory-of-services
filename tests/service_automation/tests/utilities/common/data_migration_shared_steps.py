"""Shared step definitions for data migration BDD tests."""
import os
from typing import Any, Dict, List, Literal

import pytest
from loguru import logger
from sqlalchemy import text
from sqlmodel import Session

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
from tests.service_automation.tests.utilities.common.data_migration.migration_context_helper import (
    build_supported_records_context,
    get_expected_dynamodb_table_names,
    get_migration_type_description,
    store_migration_result,
    store_sqs_result,
)
from utilities.common.data_migration.migration_helper import MigrationHelper
from utilities.common.data_migration.migration_metrics_helper import ExpectedMetrics, verify_all_metrics
from utilities.common.data_migration.migration_service_helper import parse_and_create_service
from utilities.common.data_migration.sqs_helper import build_sqs_event

ServiceAttributes = Dict[str, Any]
MigrationContext = Dict[str, Any]
DynamoDBFixture = Dict[str, Any]
GherkinTable = List[List[str]]
SQSEvent = Dict[str, Any]


def run_test_environment_configured(
    migration_helper: MigrationHelper, dynamodb: DynamoDBFixture
) -> None:
    """Verify test environment is properly configured."""
    try:
        response = dynamodb[DYNAMODB_CLIENT].list_tables()
        table_names = response.get("TableNames", [])
        logger.info(f"Found {len(table_names)} DynamoDB tables")
        assert "TableNames" in response, "DynamoDB should be accessible"
    except Exception as e:
        pytest.fail(f"Failed to access DynamoDB: {e}")

    assert migration_helper is not None, "Migration helper should be configured"
    assert migration_helper.db_uri is not None, "Database URI should be set"
    assert (
        migration_helper.dynamodb_endpoint is not None
    ), "DynamoDB endpoint should be set"

    logger.info("Environment configuration verified")


def run_dos_database_has_test_data(dos_db_with_migration: Session) -> None:
    """Verify DoS database is accessible and has tables."""
    result = dos_db_with_migration.exec(text(f"SELECT COUNT(*) FROM {SERVICES_TABLE}"))
    count = result.fetchone()[0]
    assert count >= 0, "Should be able to query services table"
    logger.info(f"DoS database ready with {count} services")


def run_dynamodb_tables_ready(dynamodb: DynamoDBFixture) -> None:
    """Verify DynamoDB tables exist and are accessible."""
    client = dynamodb[DYNAMODB_CLIENT]
    response = client.list_tables()
    table_names = response.get("TableNames", [])

    logger.debug(f"Found {len(table_names)} tables in DynamoDB")

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

    logger.info("All required DynamoDB tables are ready")


def run_create_service_with_attributes(
    dos_db_with_migration: Session,
    migration_context: MigrationContext,
    entity_type: str,
    entity_name: str,
    datatable: GherkinTable,
) -> ServiceAttributes:
    """Create a service in DoS database with attributes from Gherkin table."""
    return parse_and_create_service(
        dos_db_with_migration,
        migration_context,
        entity_type,
        entity_name,
        datatable,
    )


def run_full_service_migration(
    migration_helper: MigrationHelper,
    migration_context: MigrationContext,
) -> None:
    """Execute full service migration and capture output."""
    result = migration_helper.run_full_service_migration()
    store_migration_result(migration_context, result)

    logger.info(
        "Full service migration completed",
        extra={
            "success": result.success,
            "total_records": result.metrics.total_records if result.metrics else 0,
        },
    )


def run_single_service_migration(
    migration_helper: MigrationHelper,
    migration_context: MigrationContext,
    service_id: int,
) -> None:
    """Execute migration for a single service and capture output."""
    result = migration_helper.run_single_service_migration(service_id)
    store_migration_result(migration_context, result, service_id)

    logger.info(
        "Single service migration completed",
        extra={"service_id": service_id, "success": result.success},
    )


def run_sqs_event_migration_with_params(
    migration_helper: MigrationHelper,
    migration_context: MigrationContext,
    table_name: str,
    record_id: int,
    method: Literal["insert", "update", "delete"],
) -> Dict[str, Any]:
    """Execute migration with SQS event built from minimal parameters."""
    event = build_sqs_event(
        table_name=table_name,
        record_id=record_id,
        method=method,
    )

    logger.debug(
        "Processing SQS event with parameters",
        extra={"table_name": table_name, "record_id": record_id, "method": method},
    )

    result = migration_helper.run_sqs_event_migration(event)
    store_sqs_result(migration_context, result, event, record_id)

    logger.info(
        "SQS event migration completed",
        extra={
            "success": result.success,
            "migrated_records": (
                result.metrics.migrated_records if result.metrics else 0
            ),
            "table_name": table_name,
            "record_id": record_id,
            "method": method,
        },
    )

    return {"event": event, "result": result}


def run_verify_migration_metrics_inline(
    migration_context: MigrationContext,
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

    logger.info(
        f"Verified metrics for {migration_type}",
        extra={
            "total": total,
            "supported": supported,
            "is_full_sync": migration_context.get("service_id") is None,
        },
    )


def run_verify_sqs_event_metrics(
    migration_context: MigrationContext,
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

    logger.info(
        f"Verified SQS event metrics for {migration_type}",
        extra={"total": total, "migrated": migrated},
    )


def run_verify_service_not_migrated(
    migration_context: MigrationContext,
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

    logger.info(
        f"Verified service {service_id} was not migrated",
        extra={"reason": expected_reason},
    )


def run_verify_service_skipped(
    migration_context: MigrationContext,
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

    logger.info(
        f"Verified service {service_id} was skipped",
        extra={"reason": expected_reason},
    )


def run_verify_transformer_selected(
    migration_context: MigrationContext,
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

    logger.info(
        f"Verified transformer selection for service {service_id}",
        extra={"transformer_name": transformer_name},
    )


def run_verify_transformation_output(
    migration_context: MigrationContext,
    service_id: int,
    org_count: int,
    location_count: int,
    service_count: int,
) -> None:
    """Verify that a service was transformed into the expected number of resources."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformation_log(
        mock_logger=mock_logger,
        service_id=service_id,
        organisation_count=org_count,
        location_count=location_count,
        healthcare_service_count=service_count,
    )

    logger.info(
        f"Verified transformation output for service {service_id}",
        extra={
            "organisation_count": org_count,
            "location_count": location_count,
            "healthcare_service_count": service_count,
        },
    )
