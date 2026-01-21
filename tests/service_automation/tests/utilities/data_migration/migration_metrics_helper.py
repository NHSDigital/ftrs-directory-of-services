"""Helper utilities for verifying migration metrics."""

from dataclasses import dataclass
from typing import Any
from service_migration.models import ServiceMigrationMetrics

from loguru import logger


<<<<<<< HEAD:tests/service_automation/tests/utilities/common/data_migration/migration_metrics_helper.py
=======
@dataclass
class ExpectedMetrics:
    """Expected values for migration metrics."""

    total: int
    supported: int
    unsupported: int
    transformed: int
    inserted: int
    updated: int
    skipped: int
    errors: int


>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682)):tests/service_automation/tests/utilities/data_migration/migration_metrics_helper.py
def assert_metric_matches(
    actual: int,
    expected: int,
    metric_name: str,
    migration_type: str,
    additional_context: str = "",
) -> None:
    """Assert that a metric value matches expected value."""
    error_parts = [
        f"{metric_name.capitalize()} mismatch for {migration_type}:",
        f"  Expected: {expected}",
        f"  Got: {actual}",
    ]

    if additional_context:
        error_parts.append(f"  {additional_context}")

    assert actual == expected, "\n".join(error_parts)


def verify_all_metrics(
    actual_metrics: ServiceMigrationMetrics,
    expected: ServiceMigrationMetrics,
    migration_type: str,
    additional_context: str = "",
) -> None:
    """Verify all migration metrics match expected values."""
<<<<<<< HEAD:tests/service_automation/tests/utilities/common/data_migration/migration_metrics_helper.py
    assert actual_metrics == expected, (
        f"Metrics do not match for {migration_type}.\n"
        f"Expected: {expected.model_dump()}\n"
        f"Got: {actual_metrics.model_dump()}\n"
        f"{additional_context}"
=======
    assert_metric_matches(
        actual_metrics.total_records,
        expected.total,
        "total records",
        migration_type,
    )
    assert_metric_matches(
        actual_metrics.supported_records,
        expected.supported,
        "supported records",
        migration_type,
        additional_context,
    )
    assert_metric_matches(
        actual_metrics.unsupported_records,
        expected.unsupported,
        "unsupported records",
        migration_type,
    )
    assert_metric_matches(
        actual_metrics.transformed_records,
        expected.transformed,
        "transformed records",
        migration_type,
    )
    assert_metric_matches(
        actual_metrics.inserted_records,
        expected.inserted,
        "inserted records",
        migration_type,
    )
    assert_metric_matches(
        actual_metrics.updated_records,
        expected.updated,
        "updated records",
        migration_type,
    )
    assert_metric_matches(
        actual_metrics.skipped_records,
        expected.skipped,
        "skipped records",
        migration_type,
    )
    assert_metric_matches(
        actual_metrics.errors,
        expected.errors,
        "errors",
        migration_type,
>>>>>>> 1e2fc0a7 (feat(data-migration): FTRS-1597 Detect changes from last known to current state (#682)):tests/service_automation/tests/utilities/data_migration/migration_metrics_helper.py
    )

    logger.debug(
        f"All metrics verified for {migration_type}",
        extra={
            "total": expected.total,
            "supported": expected.supported,
            "unsupported": expected.unsupported,
            "transformed": expected.transformed,
            "inserted": expected.inserted,
            "updated": expected.updated,
            "skipped": expected.skipped,
            "errored": expected.errored,
        },
    )
