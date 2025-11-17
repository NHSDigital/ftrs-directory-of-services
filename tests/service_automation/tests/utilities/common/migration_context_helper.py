"""Helper utilities for working with migration test context."""
import os
from typing import Any, Dict, Optional, Tuple

from utilities.common.constants import (
    DEFAULT_ENVIRONMENT,
    DEFAULT_PROJECT_NAME,
    DEFAULT_WORKSPACE,
    ENV_ENVIRONMENT,
    ENV_PROJECT_NAME,
    ENV_WORKSPACE,
    EXPECTED_DYNAMODB_RESOURCES,
)


def get_service_context(
    migration_context: Dict[str, Any],
) -> Tuple[Optional[int], Dict[str, Any], str]:
    """Extract service-related context from migration context."""
    return (
        migration_context.get("service_id"),
        migration_context.get("service_data", {}),
        migration_context.get("service_name", ""),
    )


def get_sqs_context(
    migration_context: Dict[str, Any],
) -> Tuple[Dict[str, Any], Optional[int], list[int]]:
    """Extract SQS-related context from migration context."""
    return (
        migration_context.get("sqs_event", {}),
        migration_context.get("sqs_service_id"),
        migration_context.get("sqs_service_ids", []),
    )


def build_supported_records_context(migration_context: Dict[str, Any]) -> str:
    """Build additional context string for supported records assertion."""
    service_id = migration_context.get("service_id")
    service_data = migration_context.get("service_data", {})

    if service_id is None:
        return "(All existing services in database)"

    return (
        f"Type ID: {service_data.get('typeid')}, "
        f"ODS Code: {service_data.get('odscode')}, "
        f"Status: {service_data.get('statusid')}"
    )


def get_migration_type_description(migration_context: Dict[str, Any]) -> str:
    """Get human-readable description of migration type from context."""
    service_id = migration_context.get("service_id")
    sqs_service_id = migration_context.get("sqs_service_id")
    sqs_event = migration_context.get("sqs_event", {})

    if sqs_event:
        is_empty_event = len(sqs_event) == 0
        record_count = len(sqs_event.get("Records", []))

        if is_empty_event:
            return "empty event"
        elif sqs_service_id:
            return f"SQS event for service {sqs_service_id}"
        else:
            return f"SQS event with {record_count} record(s)"
    elif service_id is None:
        return "full sync"
    else:
        return f"service {service_id}"


def store_migration_result(
    migration_context: Dict[str, Any],
    result: Any,
    service_id: Optional[int] = None,
) -> None:
    """Store migration result in context."""
    migration_context["result"] = result
    migration_context["mock_logger"] = result.mock_logger
    if service_id is not None:
        migration_context["service_id"] = service_id


def store_sqs_result(
    migration_context: Dict[str, Any],
    result: Any,
    event: Dict[str, Any],
    record_id: int,
) -> None:
    """Store SQS migration result in context."""
    migration_context["result"] = result
    migration_context["mock_logger"] = result.mock_logger
    migration_context["sqs_event"] = event
    migration_context["sqs_service_ids"] = [record_id]
    migration_context["sqs_service_id"] = record_id


def get_expected_dynamodb_table_names() -> list[str]:
    """Get expected DynamoDB table names based on environment configuration."""
    project_name = os.getenv(ENV_PROJECT_NAME, DEFAULT_PROJECT_NAME)
    environment = os.getenv(ENV_ENVIRONMENT, DEFAULT_ENVIRONMENT)
    workspace = os.getenv(ENV_WORKSPACE, DEFAULT_WORKSPACE)

    return [
        f"{project_name}-{environment}-database-{resource}-{workspace}"
        for resource in EXPECTED_DYNAMODB_RESOURCES
    ]
