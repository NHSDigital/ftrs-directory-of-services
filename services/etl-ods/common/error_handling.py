import os
import re
from http import HTTPStatus

import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.exceptions import (
    PermanentProcessingError,
    RateLimitError,
    RetryableProcessingError,
    UnrecoverableError,
)


def handle_rate_limit_error(
    message_id: str,
    receive_count: int,
    error: RateLimitError,
    logger: Logger,
) -> None:
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT", "3"))
    if receive_count >= max_receive_count:
        error_message = (
            "Rate limit exceeded - final attempt, message will be sent to DLQ"
        )
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_001,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=max_receive_count,
            error_message=error_message,
            exception=error,
        )
    else:
        error_message = f"Rate limit exceeded - message will be retried (attempt {receive_count}/{max_receive_count})"
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_001,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=max_receive_count,
            error_message=error_message,
        )


def handle_permanent_error(
    message_id: str, error: "PermanentProcessingError", logger: Logger
) -> None:
    """Handle permanent failures that should be consumed immediately (no retry, no DLQ).

    Typically for expected business scenarios like 404 Not Found.
    """
    error_message = f"Permanent failure (status {error.status_code}): {error.response_text}. Message will be consumed immediately."

    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_002,
        message_id=message_id,
        receive_count=1,
        max_receive_count=1,
        error_message=error_message,
    )


def handle_unrecoverable_error(
    message_id: str, error: "UnrecoverableError", logger: Logger
) -> None:
    """Handle unrecoverable failures that should go to DLQ immediately (no retry).

    Typically indicates bugs in our code or configuration issues that need investigation.
    """
    error_message = f"Unrecoverable failure ({error.error_type}): {error.details}. Sending to DLQ immediately."
    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_002,
        message_id=message_id,
        receive_count=1,
        max_receive_count=1,
        error_message=error_message,
    )


def handle_retryable_error(
    message_id: str,
    receive_count: int,
    error: RetryableProcessingError,
    logger: Logger,
) -> None:
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT", "3"))
    if receive_count >= max_receive_count:
        error_message = f"Retryable failure (status {error.status_code}): {error.response_text}. Final attempt, message will be sent to DLQ"
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=max_receive_count,
            error_message=error_message,
        )
    else:
        error_message = f"Retryable failure (status {error.status_code}): {error.response_text}. Message will be retried (attempt {receive_count}/{max_receive_count})"
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=max_receive_count,
            error_message=error_message,
        )


def handle_general_error(
    message_id: str, receive_count: int, error: Exception, logger: Logger
) -> None:
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT", "3"))
    error_details = f"{type(error).__name__}: {str(error)}"

    if receive_count >= max_receive_count:
        error_message = f"Processing failed - final attempt, message will be sent to DLQ. Error: {error_details}"
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=max_receive_count,
            error_message=error_message,
        )
    else:
        error_message = f"Processing failed - message will be retried (attempt {receive_count}/{max_receive_count}). Error: {error_details}"
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_002,
            message_id=message_id,
            receive_count=receive_count,
            max_receive_count=max_receive_count,
            error_message=error_message,
        )


def _build_error_message(
    error_type: str, status_code: int, error: Exception, context: str = None
) -> str:
    """Build error message with optional context."""
    if status_code:
        base_message = f"{error_type} (status {status_code}): {str(error)}"
        context_message = (
            f"{error_type} for {context} (status {status_code}): {str(error)}"
        )
    else:
        base_message = f"{error_type}: {str(error)}"
        context_message = f"{error_type} for {context}: {str(error)}"

    return context_message if context else base_message


def _log_and_raise_permanent(
    message_id: str,
    status_code: int,
    http_error: Exception,
    logger: Logger,
    context: str = None,
) -> None:
    """Log and raise permanent processing error."""
    error_message = _build_error_message(
        "Permanent HTTP error", status_code, http_error, context
    )
    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_009,
        message_id=message_id,
        status_code=status_code,
        error_message=error_message,
    )
    raise PermanentProcessingError(
        message_id=message_id,
        status_code=status_code or 0,
        response_text=str(http_error),
    )


def handle_http_error(
    http_error: requests.exceptions.HTTPError,
    message_id: str,
    logger: Logger,
    error_context: str = None,
) -> None:
    """
    Handle HTTP errors with standard logging and exception raising patterns.

    Classification:
    - Unrecoverable (DLQ immediately, no retry): 400, 401, 403, 405, 406, 422
    - Retryable (retry with backoff, DLQ after max): 408, 409, 410, 412, 429, 500, 502, 503, 504
    - Permanent (consume immediately, no retry, no DLQ): 404

    Args:
        http_error: The HTTP error that occurred
        message_id: Message ID for logging context
        logger: Logger instance
        error_context: Context information (like ODS code) for logging

    Raises:
        UnrecoverableError: For bugs/config issues that need immediate investigation
        PermanentProcessingError: For expected permanent failures (404)
        RateLimitError: For rate limit errors (429) - retryable
        RetryableProcessingError: For transient errors that should be retried
    """
    # Try to get status code from response, fallback to parsing from error message
    status_code = None
    if http_error.response is not None:
        status_code = http_error.response.status_code

    # If status_code is still None, try parsing from error message
    if status_code is None:
        error_str = str(http_error)
        match = re.search(r"(\d{3})\s+(?:Client|Server)\s+Error", error_str)
        if match:
            status_code = int(match.group(1))

    RETRYABLE_STATUS_CODES = {408, 409, 410, 412, 429, 500, 502, 503, 504}
    PERMANENT_STATUS_CODES = {404}
    UNRECOVERABLE_STATUS_CODES = {400, 401, 403, 405, 406, 422}

    if status_code == HTTPStatus.BAD_REQUEST:
        error_message = _build_error_message(
            "Bad Request - invalid payload", 400, http_error, error_context
        )
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=status_code,
            error_message=error_message,
        )
        raise UnrecoverableError(
            message_id=message_id,
            error_type="HTTP_400_BAD_REQUEST",
            details=str(http_error),
        )

    if status_code == HTTPStatus.TOO_MANY_REQUESTS:
        error_message = _build_error_message(
            "Rate limit exceeded", 429, http_error, error_context
        )
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=status_code,
            error_message=error_message,
        )
        err_msg = "Rate limit exceeded"
        raise RateLimitError(err_msg)

    if status_code in RETRYABLE_STATUS_CODES:
        error_message = _build_error_message(
            "Retryable HTTP error", status_code, http_error, error_context
        )
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=status_code,
            error_message=error_message,
        )
        raise RetryableProcessingError(
            message_id=message_id,
            status_code=status_code,
            response_text=str(http_error),
        )

    if status_code in PERMANENT_STATUS_CODES:
        _log_and_raise_permanent(
            message_id, status_code, http_error, logger, error_context
        )

    if status_code in UNRECOVERABLE_STATUS_CODES:
        error_message = _build_error_message(
            "Unrecoverable HTTP error", status_code, http_error, error_context
        )
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=status_code,
            error_message=error_message,
        )
        raise UnrecoverableError(
            message_id=message_id,
            error_type=f"HTTP_{status_code}",
            details=str(http_error),
        )

    error_message = _build_error_message(
        "Unknown HTTP error", status_code or 0, http_error, error_context
    )

    if not status_code:
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_014,
            method="HTTP",
            url=error_context or "unknown",
            error_message=error_message,
        )
    else:
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_009,
            message_id=message_id,
            status_code=status_code,
            error_message=error_message,
        )

    raise UnrecoverableError(
        message_id=message_id,
        error_type=f"HTTP_{status_code or 0}_UNKNOWN",
        details=str(http_error),
    )


def handle_general_exception(
    exception: Exception,
    message_id: str,
    logger: Logger,
    error_context: str = "unknown",
) -> None:
    """
    Handle general exceptions with consistent logging.

    Args:
        exception: The exception that occurred
        message_id: Message ID for logging context
        logger: Logger instance
        error_context: Context information for logging
    """
    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_009,
        message_id=message_id,
        status_code=0,
        error_message=f"Error in {error_context}: {str(exception)}",
    )
