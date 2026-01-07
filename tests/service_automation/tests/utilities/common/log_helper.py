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
        reference: Log reference code (e.g., "SM_PROC_003")
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
    organisation_count: int,
    location_count: int,
    healthcare_service_count: int,
) -> None:
    """
    Verify SM_PROC_007a transformation log with expected counts.

    Args:
        mock_logger: MockLogger instance
        service_id: Service ID that was transformed
        organisation_count: Expected number of organisations
        location_count: Expected number of locations
        healthcare_service_count: Expected number of healthcare services

    Raises:
        AssertionError: If log not found or counts don't match
    """
    assert_log_exists(mock_logger, "SM_PROC_007a", level="DEBUG")

    log_detail = get_log_detail(
        mock_logger,
        "SM_PROC_007a",
        level="DEBUG",
    )

    assert organisation_count in [0, 1], "Organisation count should be 0 or 1"
    assert location_count in [0, 1], "Location count should be 0 or 1"
    assert healthcare_service_count in [0, 1], (
        "Healthcare service count should be 0 or 1"
    )

    organisation = log_detail["transformed_record"].get("organisation")
    location = log_detail["transformed_record"].get("location")
    healthcare_service = log_detail["transformed_record"].get("healthcare_service")

    if organisation_count == 0:
        assert organisation is None, "Expected no organisation in transformed record"
    else:
        assert organisation is not None, "Expected organisation in transformed record"

    if location_count == 0:
        assert location is None, "Expected no location in transformed record"
    else:
        assert location is not None, "Expected location in transformed record"

    if healthcare_service_count == 0:
        assert healthcare_service is None, (
            "Expected no healthcare service in transformed record"
        )
    else:
        assert healthcare_service is not None, (
            "Expected healthcare service in transformed record"
        )


def verify_service_not_migrated_log(
    mock_logger: MockLogger,
    service_id: int,
    expected_reason: str,
) -> None:
    """
    Verify SM_PROC_006 not migrated log with expected reason.

    Args:
        mock_logger: MockLogger instance
        service_id: Service ID that was not migrated
        expected_reason: Expected reason for not migrating

    Raises:
        AssertionError: If log not found or reason doesn't match
    """
    assert_log_exists(mock_logger, "SM_PROC_006", level="INFO", service_id=service_id)

    assert_log_detail_matches(
        mock_logger,
        "SM_PROC_006",
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
    Verify SM_PROC_006 skipped log with expected reason.

    Args:
        mock_logger: MockLogger instance
        service_id: Service ID that was skipped
        expected_reason: Expected reason for skipping

    Raises:
        AssertionError: If log not found or reason doesn't match
    """
    assert_log_exists(mock_logger, "SM_PROC_006", level="INFO", service_id=service_id)

    assert_log_detail_matches(
        mock_logger,
        "SM_PROC_006",
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
    Verify SM_PROC_003 transformer selection log with expected transformer name.

    Args:
        mock_logger: MockLogger instance
        transformer_name: Expected transformer name (e.g., 'GPPracticeTransformer')
        service_id: Service ID that was migrated

    Raises:
        AssertionError: If log not found or wrong transformer name
    """
    assert_log_exists(mock_logger, "SM_PROC_003", level="INFO", service_id=service_id)

    # Get all SM_PROC_003 logs
    logs = mock_logger.get_log("SM_PROC_003", level="INFO")

    # Find the log entry for this specific transformer
    matching_logs = [
        log
        for log in logs
        if log.get("detail", {}).get("transformer_name") == transformer_name
    ]

    assert len(matching_logs) > 0, (
        f"SM_PROC_003 log not found for transformer '{transformer_name}'\n"
        f"Expected: Transformer {transformer_name} selected for service\n"
        f"Found {len(logs)} SM_PROC_003 logs\n"
        f"Found transformer names: {[log.get('detail', {}).get('transformer_name') for log in logs]}"
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
    Verify SM_APP_004 migration completion log exists.

    This log is emitted at the end of the data migration pipeline,
    indicating successful completion of the migration process.

    Args:
        mock_logger: MockLogger instance

    Raises:
        AssertionError: If completion log not found
    """
    assert_log_exists(mock_logger, "SM_APP_004", level="INFO")

    # Get the completion log
    completion_logs = mock_logger.get_log("SM_APP_004", level="INFO")

    assert len(completion_logs) == 1, (
        "SM_APP_004 completion log not found\n"
        f"Expected: Completed handling of SQS event\n"
        f"Log output: {mock_logger.format_logs_for_print()}"
    )

    # Verify the log message
    log_entry = completion_logs[0]
    assert "msg" in log_entry, f"Log entry missing 'msg' field: {log_entry}"

    expected_message = "Completed handling of SQS event"
    assert expected_message in log_entry["msg"], (
        f"Unexpected completion message:\n"
        f"  Expected: '{expected_message}'\n"
        f"  Actual: '{log_entry['msg']}'"
    )


def verify_error_log_present(
    mock_logger: MockLogger,
    error_fragment: str,
) -> None:
    """
    Verify SM_APP_009 error log with error details is present.

    SM_APP_009 is the general error log for unexpected exceptions during processing.

    Args:
        mock_logger: MockLogger instance
        error_fragment: Fragment of the error message expected

    Raises:
        AssertionError: If log not found or error fragment not matched
    """
    assert_log_exists(mock_logger, "SM_APP_009", level="ERROR")
    logs = mock_logger.get_log("SM_APP_009", level="ERROR")

    matched = [
        log_line
        for log_line in logs
        if error_fragment in log_line["detail"].get("error", "")
    ]
    assert matched, (
        f"Error level log (SM_APP_009) with error containing fragment '{error_fragment}' not found\n"
        f"Available ERROR logs: {mock_logger.get_logs('ERROR')}"
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
