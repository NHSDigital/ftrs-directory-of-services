"""BDD steps for verifying migration execution results."""

from typing import Any, Dict

from pytest_bdd import given, parsers, then

from service_migration.models import ServiceMigrationMetrics
from utilities.common.data_migration.migration_context_helper import (
    get_migration_type_description,
)
from utilities.common.data_migration.migration_metrics_helper import (
    verify_all_metrics,
)
from utilities.common.log_helper import (
    get_mock_logger_from_context,
    verify_migration_completed_log,
    verify_error_log_present,
    verify_service_not_migrated_log,
    verify_service_skipped_log,
    verify_transformation_log,
    verify_transformer_selected_log,
)


# ============================================================
# Verification Steps (Then)
# ============================================================


@then("the service migration process completes successfully")
def verify_pipeline_completed_successfully(
    migration_context: Dict[str, Any],
) -> None:
    """Verify that the migration pipeline completed successfully."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.success is True, (
        "Migration process should complete successfully\nLog output:\n"
        + migration_context["mock_logger"].format_logs_for_print()
    )

    mock_logger = get_mock_logger_from_context(migration_context)
    verify_migration_completed_log(mock_logger)


@then("the service migration process results in a fatal error")
def verify_pipeline_completed_with_error(
    migration_context: Dict[str, Any],
) -> None:
    """Verify that the migration pipeline completed with a fatal error."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    # The migration process itself should succeed (no exceptions)
    # but the service should be marked as invalid
    assert result.success is True, (
        "Migration process should complete (even with invalid services)\nLog output:\n"
        + migration_context["mock_logger"].format_logs_for_print()
    )


@then("the triage code migration process completes successfully")
def verify_triage_code_completed_successfully(
    migration_context: Dict[str, Any],
) -> None:
    """Verify that the triage code migration pipeline completed successfully."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.success is True, (
        "Triage code migration process should complete successfully\nLog output:\n"
        + migration_context["mock_logger"].format_logs_for_print()
    )


@then(
    parsers.parse(
        "the metrics should be "
        "{total:d} total, "
        "{supported:d} supported, "
        "{unsupported:d} unsupported, "
        "{transformed:d} transformed, "
        "{inserted:d} inserted, "
        "{updated:d} updated, "
        "{skipped:d} skipped, "
        "{invalid:d} invalid and "
        "{errored:d} errored"
    )
)
def verify_sqs_event_metrics(
    migration_context: Dict[str, Any],
    total: int,
    supported: int,
    unsupported: int,
    transformed: int,
    inserted: int,
    updated: int,
    invalid: int,
    skipped: int,
    errored: int,
) -> None:
    """Verify SQS event migration metrics match expected values."""
    result = migration_context.get("result")

    assert result is not None, "Migration result should exist"
    assert result.metrics is not None, "Migration metrics should exist"

    migration_type = get_migration_type_description(migration_context)

    expected = ServiceMigrationMetrics(
        total=total,
        supported=supported,
        unsupported=unsupported,
        transformed=transformed,
        invalid=invalid,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
        errored=errored,
    )

    verify_all_metrics(
        actual_metrics=result.metrics,
        expected=expected,
        migration_type=migration_type,
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
    """Verify the correct transformer was selected for the service."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformer_selected_log(
        mock_logger=mock_logger,
        transformer_name=transformer_name,
        service_id=service_id,
    )


@then(
    parsers.parse(
        "the service was transformed into "
        "{org_count:d} organisation, "
        "{location_count:d} location and "
        "{service_count:d} healthcare service"
    )
)
def verify_transformation_output(
    migration_context: Dict[str, Any],
    org_count: int,
    location_count: int,
    service_count: int,
) -> None:
    """Verify transformation output counts."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_transformation_log(
        mock_logger=mock_logger,
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


@then(
    parsers.parse("error log containing message: '{error_message_fragment}' was found")
)
def verify_error_level_log(
    migration_context: Dict[str, Any],
    error_message_fragment: str,
) -> None:
    """Verify that error message with content was logged."""
    mock_logger = get_mock_logger_from_context(migration_context)

    verify_error_log_present(
        mock_logger=mock_logger,
        error_fragment=error_message_fragment,
    )


@given("the mock logger is reset")
def reset_mock_logger(migration_context: Dict[str, Any]) -> None:
    """Reset the mock logger in the migration context."""
    mock_logger = get_mock_logger_from_context(migration_context)
    mock_logger.clear_logs()
