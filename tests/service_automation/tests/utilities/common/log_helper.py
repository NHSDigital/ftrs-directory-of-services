"""Helper utilities for verifying log output in tests."""
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

import pytest


@dataclass
class LogVerificationConfig:
    """Configuration for verifying a specific log reference."""

    log_reference: str
    message_template: str
    additional_patterns: Optional[list[str]] = None
    validation_fn: Optional[Callable[[str], None]] = None


def verify_log_reference(
    migration_context: Dict[str, Any],
    service_id: int,
    config: LogVerificationConfig,
) -> str:
    """
    Verify that a specific log reference exists for a service.

    Args:
        migration_context: Test context dictionary with captured output
        service_id: Service ID that was processed
        config: Log verification configuration

    Returns:
        Matching log line

    Raises:
        pytest.fail: If log not found or validation fails
    """
    captured_output = migration_context.get("captured_output", {})
    stdout = captured_output.get("stdout", "")
    stderr = captured_output.get("stderr", "")

    combined_output = stdout + stderr
    output_lines = combined_output.split("\n")

    actual_service_id = migration_context.get("service_id", service_id)

    reference_pattern = f'"reference":"{config.log_reference}"'
    message_pattern = config.message_template
    record_id_pattern = f'"record_id":{actual_service_id}'

    required_patterns = [reference_pattern, message_pattern, record_id_pattern]
    if config.additional_patterns:
        required_patterns.extend(config.additional_patterns)

    matching_lines = [
        line
        for line in output_lines
        if all(pattern in line for pattern in required_patterns)
    ]

    if not matching_lines:
        build_and_fail_with_error_message(
            output_lines=output_lines,
            config=config,
            service_id=service_id,
            actual_service_id=actual_service_id,
            required_patterns=required_patterns,
        )

    matching_log = matching_lines[0].strip()

    if config.validation_fn:
        config.validation_fn(matching_log)

    return matching_log


def build_and_fail_with_error_message(
    output_lines: list[str],
    config: LogVerificationConfig,
    service_id: int,
    actual_service_id: int,
    required_patterns: list[str],
) -> None:
    """
    Build comprehensive error message and fail the test.

    Args:
        output_lines: All captured output lines
        config: Log verification configuration
        service_id: Service ID from step parameter
        actual_service_id: Actual service ID from context
        required_patterns: List of required patterns that should match

    Raises:
        pytest.fail: Always fails with detailed error message
    """
    all_reference_logs = [
        line for line in output_lines if f'"{config.log_reference}"' in line
    ]

    error_parts = [
        f"{config.log_reference} log not found for:",
        f"  - Service ID: {service_id}",
        f"  - Actual Service ID from context: {actual_service_id}",
        "",
        "Expected JSON log patterns:",
    ]

    error_parts.extend(f"  - {pattern}" for pattern in required_patterns)
    error_parts.extend(["", f"Total output lines captured: {len(output_lines)}"])

    if all_reference_logs:
        error_parts.extend(
            [
                "",
                f"Found {len(all_reference_logs)} {config.log_reference} log(s):",
            ]
        )
        error_parts.extend(f"  - {log.strip()}" for log in all_reference_logs)
    else:
        error_parts.extend(
            [
                "",
                f"No {config.log_reference} logs found in captured output.",
            ]
        )

    pytest.fail("\n".join(error_parts))
