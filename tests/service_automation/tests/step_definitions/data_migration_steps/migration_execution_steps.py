"""BDD steps for executing data migrations."""

from typing import Any, Dict, Literal

from pytest_bdd import given, parsers, when

from utilities.common.data_migration.migration_context_helper import (
    store_sqs_result,
)
from utilities.common.data_migration.migration_helper import MigrationHelper
from utilities.common.data_migration.migration_service_helper import (
    parse_and_create_service,
)
from utilities.common.data_migration.sqs_helper import build_sqs_event
from sqlalchemy.orm import Session


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
    dos_db: Session,
    migration_context: Dict[str, Any],
    entity_type: str,
    entity_name: str,
    datatable: list[list[str]],
) -> Dict[str, Any]:
    """Create a service in DoS database with attributes from Gherkin table."""
    return parse_and_create_service(
        dos_db,
        migration_context,
        entity_type,
        entity_name,
        datatable,
    )


# ============================================================
# Migration Execution Steps (When)
# ============================================================


@when("triage code full migration is executed")
def triage_code_full_migration(
    migration_context: Dict[str, Any],
    migration_helper: MigrationHelper,
    dynamodb: Dict[str, Any],
) -> None:
    """Execute triage code migration."""
    result = migration_helper.run_triage_code_migration_only()
    migration_context["result"] = result
    migration_context["mock_logger"] = result.mock_logger


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
    event = build_sqs_event(
        table_name="services",
        record_id=service_id,
        service_id=service_id,
        method="insert",
    )

    result = migration_helper.run_sqs_event_migration(event)
    store_sqs_result(migration_context, result, event, service_id)
    return {"event": event, "result": result}


@when(
    parsers.parse(
        "the service migration process is run for table '{table_name}', "
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
