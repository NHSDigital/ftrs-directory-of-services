"""Helper utilities for verifying migration metrics."""

from dataclasses import dataclass
from typing import Any
from service_migration.models import ServiceMigrationMetrics

from loguru import logger


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
    assert actual_metrics == expected, (
        f"Metrics do not match for {migration_type}.\n"
        f"Expected: {expected.model_dump()}\n"
        f"Got: {actual_metrics.model_dump()}\n"
        f"{additional_context}"
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
