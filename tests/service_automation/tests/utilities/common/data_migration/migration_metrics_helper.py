"""Helper utilities for verifying migration metrics."""
from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class ExpectedMetrics:
    """Expected values for migration metrics."""

    total: int
    supported: int
    unsupported: int
    transformed: int
    migrated: int
    skipped: int
    errors: int


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
    actual_metrics: Any,
    expected: ExpectedMetrics,
    migration_type: str,
    additional_context: str = "",
) -> None:
    """Verify all migration metrics match expected values."""
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
        actual_metrics.migrated_records,
        expected.migrated,
        "migrated records",
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
    )

    logger.debug(
        f"All metrics verified for {migration_type}",
        extra={
            "total": expected.total,
            "supported": expected.supported,
            "unsupported": expected.unsupported,
            "transformed": expected.transformed,
            "migrated": expected.migrated,
            "skipped": expected.skipped,
            "errors": expected.errors,
        },
    )
