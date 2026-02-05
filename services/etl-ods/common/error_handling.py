import json
import os
from typing import Any, Dict, Union

import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.exceptions import (
    PermanentProcessingError,
    RetryableProcessingError,
)


def extract_operation_outcome(response: requests.Response) -> Dict[str, Any]:
    """Extract FHIR OperationOutcome information from HTTP response.

    Args:
        response: HTTP response that may contain FHIR OperationOutcome

    Returns:
        Dictionary with operation outcome details for logging
    """
    outcome_info = {
        "resource_type": "Unknown",
        "issues_count": 0,
        "severity_levels": [],
        "issue_codes": [],
        "issue_details": [],
    }

    try:
        if response.headers.get("content-type", "").startswith("application/"):
            response_data = response.json()

            if (
                isinstance(response_data, dict)
                and response_data.get("resourceType") == "OperationOutcome"
            ):
                outcome_info["resource_type"] = "OperationOutcome"
                issues = response_data.get("issue", [])
                outcome_info["issues_count"] = len(issues)

                for issue in issues:
                    if isinstance(issue, dict):
                        severity = issue.get("severity", "unknown")
                        code = issue.get("code", "unknown")
                        details = issue.get("details", {}).get("text", "No details")

                        outcome_info["severity_levels"].append(severity)
                        outcome_info["issue_codes"].append(code)
                        outcome_info["issue_details"].append(
                            details[:100]
                        )  # Limit detail length
            else:
                outcome_info["resource_type"] = response_data.get(
                    "resourceType", "Non-FHIR"
                )

    except (json.JSONDecodeError, AttributeError, KeyError):
        outcome_info["resource_type"] = "Invalid JSON or Non-JSON response"

    return outcome_info


def _build_troubleshooting_info(
    error: Exception, receive_count: int = None, max_receive_count: int = None
) -> str:
    """Build standardized troubleshooting information for errors.

    Args:
        error: The exception to extract info from
        receive_count: Current retry attempt (for retryable errors)
        max_receive_count: Maximum retry attempts (for retryable errors)

    Returns:
        Formatted troubleshooting string
    """
    if hasattr(error, "status_code"):
        parts = _build_permanent_error_info(error)
    else:
        parts = _build_general_error_info(error, receive_count, max_receive_count)

    return " | ".join(parts)


def _build_permanent_error_info(error: "PermanentProcessingError") -> list:
    """Build troubleshooting info for permanent processing errors."""
    parts = [f"Status: {error.status_code}"]

    error_category = getattr(error, "error_category", None)
    if error_category:
        parts.append(f"Category: {error_category}")

    if hasattr(error, "response_text") and "OperationOutcome" in str(
        error.response_text
    ):
        parts.append(f"FHIR: {error.response_text}")

    custom_info = getattr(error, "troubleshooting_info", None)
    if custom_info and custom_info != "No additional troubleshooting info":
        parts.extend(_format_custom_info(custom_info))

    return parts


def _build_general_error_info(
    error: Exception, receive_count: int, max_receive_count: int
) -> list:
    """Build troubleshooting info for general exceptions."""
    parts = [
        f"Exception: {type(error).__name__}",
        f"Details: {str(error)[:200]}",
    ]

    if receive_count is not None and max_receive_count is not None:
        parts.append(f"Attempt: {receive_count}/{max_receive_count}")

    return parts


def _format_custom_info(custom_info: Union[Dict[str, Any], str]) -> list:
    """Format custom troubleshooting info into list of strings."""
    if isinstance(custom_info, dict):
        return [f"{key}: {value}" for key, value in custom_info.items()]
    else:
        return [str(custom_info)]


def handle_permanent_error(
    message_id: str, error: "PermanentProcessingError", logger: Logger
) -> None:
    """Handle permanent failures that should be consumed immediately (no retry, no DLQ).

    Typically for expected business scenarios like 404 Not Found.
    """
    error_category = getattr(error, "error_category", "UNKNOWN")
    troubleshooting_info = _build_troubleshooting_info(error)

    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_002,
        message_id=message_id,
        receive_count=1,
        max_receive_count=1,
        error_message=f"Permanent failure (status {error.status_code}) - consumed immediately",
        error_category=error_category,
        troubleshooting_info=troubleshooting_info,
    )


def handle_retryable_error(
    message_id: str,
    receive_count: int,
    error: RetryableProcessingError,
    logger: Logger,
) -> None:
    """Handle retryable failures that may be retried with backoff."""
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT", "3"))

    if receive_count >= max_receive_count:
        error_message = f"Retryable failure (status {error.status_code}) - final attempt, sending to DLQ"
    else:
        error_message = f"Retryable failure (status {error.status_code}) - retry {receive_count}/{max_receive_count}"

    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_002,
        message_id=message_id,
        receive_count=receive_count,
        max_receive_count=max_receive_count,
        error_message=error_message,
    )


def handle_general_error(
    message_id: str,
    receive_count: int,
    error: Exception,
    logger: Logger,
) -> None:
    """Handle general exceptions as retryable errors."""
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT", "3"))

    troubleshooting_info = _build_troubleshooting_info(
        error, receive_count, max_receive_count
    )

    if receive_count >= max_receive_count:
        error_message = (
            f"General failure ({type(error).__name__}) - final attempt, sending to DLQ"
        )
    else:
        error_message = f"General failure ({type(error).__name__}) - retry {receive_count}/{max_receive_count}"

    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_002,
        message_id=message_id,
        receive_count=receive_count,
        max_receive_count=max_receive_count,
        error_message=error_message,
        troubleshooting_info=troubleshooting_info,
    )


def handle_http_error(
    http_error: requests.exceptions.HTTPError,
    message_id: str,
    error_context: str = "unknown",
) -> None:
    """
    Handle HTTP errors by classifying them as permanent or retryable.

    Classification:
    - Permanent (consume immediately, no retry, no DLQ): 400, 401, 403, 404, 405, 406, 422
    - Retryable (retry with backoff, DLQ after max): 408, 409, 410, 412, 429, 500, 502, 503, 504
    """
    response = http_error.response

    # Ensure we always have a valid status code
    if response and hasattr(response, "status_code"):
        status_code = response.status_code
    else:
        # If we can't get the status code, treat as a general error (500)
        status_code = 500

    operation_outcome = extract_operation_outcome(http_error.response)
    outcome_summary = _get_operation_outcome_summary(operation_outcome)

    permanent_status_codes = {400, 401, 403, 404, 405, 406, 422}
    retryable_status_codes = {408, 409, 410, 412, 429, 500, 502, 503, 504}

    if status_code in permanent_status_codes:
        _raise_permanent_http_error(
            message_id, status_code, error_context, outcome_summary
        )
    elif status_code in retryable_status_codes:
        _raise_retryable_http_error(
            message_id, status_code, error_context, outcome_summary
        )
    else:
        _raise_unknown_http_error(
            message_id, status_code, error_context, outcome_summary
        )


def _get_operation_outcome_summary(operation_outcome: Dict[str, Any]) -> str:
    """Get formatted summary of operation outcome."""
    if operation_outcome["resource_type"] == "OperationOutcome":
        return f"OperationOutcome: {operation_outcome['issues_count']} issues"
    return "Non-FHIR response"


def _raise_permanent_http_error(
    message_id: str, status_code: int, error_context: str, outcome_summary: str
) -> None:
    """Raise permanent processing error for HTTP errors."""
    raise PermanentProcessingError(
        message_id=message_id,
        status_code=status_code,
        response_text=f"HTTP {status_code} in {error_context}: {outcome_summary}",
    )


def _raise_retryable_http_error(
    message_id: str, status_code: int, error_context: str, outcome_summary: str
) -> None:
    """Raise retryable processing error for HTTP errors."""
    raise RetryableProcessingError(
        message_id=message_id,
        status_code=status_code,
        response_text=f"HTTP {status_code} in {error_context}: {outcome_summary}",
    )


def _raise_unknown_http_error(
    message_id: str, status_code: int, error_context: str, outcome_summary: str
) -> None:
    """Raise permanent processing error for unknown HTTP status codes."""
    raise PermanentProcessingError(
        message_id=message_id,
        status_code=status_code,
        response_text=f"Unknown HTTP {status_code} in {error_context}: {outcome_summary}",
    )
