"""Helper utilities for verifying migration metrics."""

from service_migration.models import ServiceMigrationMetrics


def verify_all_metrics(
    actual_metrics: ServiceMigrationMetrics,
    expected_metrics: ServiceMigrationMetrics,
    migration_type: str,
    additional_context: str = "",
) -> None:
    """Verify all migration metrics match expected values."""
    assert actual_metrics == expected_metrics, (
        f"Metrics do not match for {migration_type}. "
        f"Expected: {expected_metrics}, Actual: {actual_metrics}. "
        f"{additional_context}"
    )
