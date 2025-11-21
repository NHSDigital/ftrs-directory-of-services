"""Helper utilities for verifying log output in tests."""
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ftrs_common.mocks.mock_logger import MockLogger


@dataclass
class LogAssertionConfig:
    """Configuration for log assertions."""

    reference: str
    level: str = "INFO"
    service_id: Optional[int] = None
    expected_detail: Optional[Dict[str, Any]] = None


def assert_log_exists(
    mock_logger: MockLogger,
    reference: str,
    level: str = "INFO",
    service_id: Optional[int] = None,
) -> None:
    """
    Assert that a log with given reference exists.

    Args:
        mock_logger: MockLogger instance to check
        reference: Log reference code (e.g., "DM_ETL_003")
        level: Log level to check (default: "INFO")
        service_id: Optional service ID for context in error messages

    Raises:
        AssertionError: If log reference not found
    """
    context = f" for service {service_id}" if service_id else ""

    assert mock_logger.was_logged(reference, level=level), (
        f"{reference} log not found{context}\n"
        f"Total logs: {mock_logger.get_log_count()}\n"
        f"{level} logs: {mock_logger.get_log_count(level)}\n"
        f"All {level} logs: {mock_logger.get_logs(level)}"
    )


def get_log_detail(
    mock_logger: MockLogger,
    reference: str,
    level: str = "INFO",
    index: int = 0,
) -> Dict[str, Any]:
    """
    Get detail field from a log entry.

    Args:
        mock_logger: MockLogger instance
        reference: Log reference code
        level: Log level (default: "INFO")
        index: Index of log entry if multiple exist (default: 0)

    Returns:
        Detail dictionary from log entry

    Raises:
        IndexError: If log entry at index doesn't exist
    """
    logs = mock_logger.get_log(reference, level=level)
    return logs[index].get("detail", {})


def assert_log_detail_matches(
    mock_logger: MockLogger,
    reference: str,
    expected_detail: Dict[str, Any],
    level: str = "INFO",
    service_id: Optional[int] = None,
) -> None:
    """
    Assert that log detail matches expected values.

    Args:
        mock_logger: MockLogger instance
        reference: Log reference code
        expected_detail: Dictionary of expected detail key-value pairs
        level: Log level (default: "INFO")
        service_id: Optional service ID for context

    Raises:
        AssertionError: If detail values don't match
    """
    logs = mock_logger.get_log(reference, level=level)
    log_entry = logs[0]
    detail = log_entry.get("detail", {})

    for key, expected_value in expected_detail.items():
        actual_value = detail.get(key)
        context = f" for service {service_id}" if service_id else ""

        assert actual_value == expected_value, (
            f"{key.capitalize()} mismatch{context}:\n"
            f"  Expected: {expected_value}\n"
            f"  Got: {actual_value}\n"
            f"  Log: {log_entry}"
        )


def verify_transformation_log(
    mock_logger: MockLogger,
    service_id: int,
    organisation_count: int,
    location_count: int,
    healthcare_service_count: int,
) -> None:
    """
    Verify DM_ETL_007 transformation log with expected counts.

    Args:
        mock_logger: MockLogger instance
        service_id: Service ID that was transformed
        organisation_count: Expected number of organisations
        location_count: Expected number of locations
        healthcare_service_count: Expected number of healthcare services

    Raises:
        AssertionError: If log not found or counts don't match
    """
    assert_log_exists(mock_logger, "DM_ETL_007", level="INFO", service_id=service_id)

    expected_detail = {
        "organisation_count": organisation_count,
        "location_count": location_count,
        "healthcare_service_count": healthcare_service_count,
    }

    assert_log_detail_matches(
        mock_logger, "DM_ETL_007", expected_detail, level="INFO", service_id=service_id
    )


def verify_service_not_migrated_log(
    mock_logger: MockLogger,
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify DM_ETL_004 not migrated log with expected reason.

    Args:
        mock_logger: MockLogger instance
        service_id: Service ID that was not migrated
        expected_reason: Expected reason for not migrating

    Raises:
        AssertionError: If log not found or reason doesn't match
    """
    assert_log_exists(mock_logger, "DM_ETL_004", level="INFO", service_id=service_id)

    assert_log_detail_matches(
        mock_logger,
        "DM_ETL_004",
        {"reason": expected_reason},
        level="INFO",
        service_id=service_id,
    )


def verify_service_skipped_log(
    mock_logger: MockLogger,
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify DM_ETL_005 skipped log with expected reason.

    Args:
        mock_logger: MockLogger instance
        service_id: Service ID that was skipped
        expected_reason: Expected reason for skipping

    Raises:
        AssertionError: If log not found or reason doesn't match
    """
    assert_log_exists(mock_logger, "DM_ETL_005", level="INFO", service_id=service_id)

    assert_log_detail_matches(
        mock_logger,
        "DM_ETL_005",
        {"reason": expected_reason},
        level="INFO",
        service_id=service_id,
    )


def verify_transformer_selected_log(
    mock_logger: MockLogger,
    transformer_name: str,
    service_id: int,
) -> None:
    """
    Verify DM_ETL_003 transformer selection log with expected transformer name.

    Args:
        mock_logger: MockLogger instance
        transformer_name: Expected transformer name (e.g., 'GPPracticeTransformer')
        service_id: Service ID that was migrated

    Raises:
        AssertionError: If log not found or wrong transformer name
    """
    assert_log_exists(mock_logger, "DM_ETL_003", level="INFO", service_id=service_id)

    # Get all DM_ETL_003 logs
    etl_003_logs = mock_logger.get_log("DM_ETL_003", level="INFO")

    # Find the log entry for this specific transformer
    matching_logs = [
        log
        for log in etl_003_logs
        if log.get("detail", {}).get("transformer_name") == transformer_name
    ]

    assert len(matching_logs) > 0, (
        f"DM_ETL_003 log not found for transformer '{transformer_name}'\n"
        f"Expected: Transformer {transformer_name} selected for record\n"
        f"Found {len(etl_003_logs)} DM_ETL_003 logs\n"
        f"Found transformer names: {[log.get('detail', {}).get('transformer_name') for log in etl_003_logs]}"
    )

    # Verify the log message format
    log_entry = matching_logs[0]
    assert "msg" in log_entry, f"Log entry missing 'msg' field: {log_entry}"
    assert transformer_name in log_entry["msg"], (
        f"Transformer name not in message:\n"
        f"  Expected substring: '{transformer_name}'\n"
        f"  Actual message: '{log_entry['msg']}'"
    )


def verify_migration_completed_log(
    mock_logger: MockLogger,
) -> None:
    """
    Verify DM_ETL_999 migration completion log exists.

    This log is emitted at the end of the data migration pipeline,
    indicating successful completion of the migration process.

    Args:
        mock_logger: MockLogger instance

    Raises:
        AssertionError: If completion log not found
    """
    assert_log_exists(mock_logger, "DM_ETL_999", level="INFO")

    # Get the completion log
    completion_logs = mock_logger.get_log("DM_ETL_999", level="INFO")

    assert len(completion_logs) > 0, (
        "DM_ETL_999 completion log not found\n"
        f"Expected: Data Migration ETL Pipeline completed successfully\n"
        f"Total INFO logs: {mock_logger.get_log_count('INFO')}"
    )

    # Verify the log message
    log_entry = completion_logs[0]
    assert "msg" in log_entry, f"Log entry missing 'msg' field: {log_entry}"

    expected_message = "Data Migration ETL Pipeline completed successfully"
    assert expected_message in log_entry["msg"], (
        f"Unexpected completion message:\n"
        f"  Expected: '{expected_message}'\n"
        f"  Actual: '{log_entry['msg']}'"
    )


def get_mock_logger_from_context(
    migration_context: Dict[str, Any],
) -> MockLogger:
    """
    Safely extract MockLogger from migration context.

    Args:
        migration_context: Test context dictionary

    Returns:
        MockLogger instance

    Raises:
        AssertionError: If MockLogger not found in context
    """
    mock_logger = migration_context.get("mock_logger")
    assert mock_logger is not None, (
        "MockLogger should be available in context.\n"
        f"Available context keys: {list(migration_context.keys())}"
    )
    return mock_logger
