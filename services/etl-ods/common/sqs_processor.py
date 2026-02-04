import json
from typing import Any, Callable, Dict, List, Union

import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.error_handling import (
    handle_general_error,
    handle_http_error,
    handle_permanent_error,
    handle_rate_limit_error,
    handle_retryable_error,
    handle_unrecoverable_error,
)
from common.exceptions import (
    PermanentProcessingError,
    RateLimitError,
    RetryableProcessingError,
    UnrecoverableError,
)
from common.sqs_request_context import (
    extract_correlation_id_from_sqs_records,
    setup_request_context,
)


def extract_record_metadata(record: Dict[str, Any]) -> Dict[str, Any]:
    body = record.get("body")
    message_id = record.get("messageId", "unknown")

    # Handle malformed JSON - this is unrecoverable
    if isinstance(body, str):
        try:
            parsed_body = json.loads(body)
        except json.JSONDecodeError as e:
            raise UnrecoverableError(
                message_id=message_id,
                error_type="MalformedJSON",
                details=f"Failed to parse JSON: {str(e)}",
            )
    elif body is None:
        parsed_body = {}
    else:
        parsed_body = body if body is not None else {}

    return {
        "message_id": message_id,
        "receive_count": int(record["attributes"]["ApproximateReceiveCount"]),
        "body": parsed_body,
    }


def _log_processing_start(logger: Logger, message_id: str, total_records: int) -> None:
    """Log the start of message processing."""
    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_003,
        message_id=message_id,
        total_records=total_records,
    )


def _log_processing_success(logger: Logger, message_id: str) -> None:
    """Log successful message processing."""
    logger.log(
        OdsETLPipelineLogBase.ETL_COMMON_004,
        message_id=message_id,
    )


def _add_to_batch_failures(
    message_id: str,
    batch_item_failures: List[Dict[str, str]],
) -> None:
    batch_item_failures.append({"itemIdentifier": message_id})


def _extract_message_metadata_for_error(record: Dict[str, Any]) -> tuple[str, int]:
    """Extract message_id and receive_count from record for error handling."""
    message_id = record.get("messageId", "unknown")
    receive_count = int(record.get("attributes", {}).get("ApproximateReceiveCount", 1))
    return message_id, receive_count


def _handle_http_error_with_context(
    http_error: requests.exceptions.HTTPError,
    record: Dict[str, Any],
    logger: Logger,
    batch_item_failures: List[Dict[str, str]],
) -> None:
    """Handle HTTP errors with context extraction and batch failure logic."""
    message_id, receive_count = _extract_message_metadata_for_error(record)

    # Extract context from record for logging
    try:
        body_content = json.loads(record.get("body", "{}"))
        error_context = body_content.get("path", "unknown")
    except (json.JSONDecodeError, AttributeError):
        error_context = "unknown"

    handle_http_error(
        http_error=http_error,
        message_id=message_id,
        logger=logger,
        error_context=error_context,
    )
    _add_to_batch_failures(message_id, batch_item_failures)


def process_sqs_records(
    records: List[Dict[str, Any]],
    process_function: Callable[[Dict[str, Any]], Any],
    logger: Logger,
) -> List[Dict[str, str]]:
    """Process a list of SQS records with common error handling."""
    batch_item_failures = []

    for record in records:
        try:
            metadata = extract_record_metadata(record)
            message_id = metadata["message_id"]
            receive_count = metadata["receive_count"]

            _log_processing_start(logger, message_id, len(records))

            process_function(record)
            _log_processing_success(logger, message_id)

        except requests.exceptions.HTTPError as http_error:
            _handle_http_error_with_context(
                http_error, record, logger, batch_item_failures
            )

        except UnrecoverableError as unrecoverable_error:
            message_id, receive_count = _extract_message_metadata_for_error(record)
            handle_unrecoverable_error(message_id, unrecoverable_error, logger)
            _add_to_batch_failures(message_id, batch_item_failures)

        except PermanentProcessingError as permanent_error:
            message_id = record.get("messageId", "unknown")
            handle_permanent_error(message_id, permanent_error, logger)
            # Permanent errors are consumed immediately (no DLQ)

        except RetryableProcessingError as retryable_error:
            message_id, receive_count = _extract_message_metadata_for_error(record)
            handle_retryable_error(message_id, receive_count, retryable_error, logger)
            _add_to_batch_failures(message_id, batch_item_failures)

        except RateLimitError as rate_limit_error:
            message_id, receive_count = _extract_message_metadata_for_error(record)
            handle_rate_limit_error(message_id, receive_count, rate_limit_error, logger)
            _add_to_batch_failures(message_id, batch_item_failures)

        except Exception as error:
            message_id, receive_count = _extract_message_metadata_for_error(record)
            handle_general_error(message_id, receive_count, error, logger)
            _add_to_batch_failures(message_id, batch_item_failures)

    return batch_item_failures


def create_sqs_lambda_handler(
    process_function: Callable[[Dict[str, Any]], Any],
    logger: Logger,
) -> Callable[[Dict[str, Any], Any], Dict[str, Any]]:
    """Create a standardized SQS lambda handler function.

    Args:
        process_function: Function to process each SQS record
        logger: Logger instance for the service
        dlq_queue_suffix: Queue suffix for DLQ (e.g., "transform", "load")

    Returns:
        Lambda handler function that processes SQS events
    """

    def lambda_handler(
        event: Dict[str, Any], context: Union[Dict[str, Any], object]
    ) -> Dict[str, Any]:
        if not event:
            return {"batchItemFailures": []}

        records = event.get("Records", [])
        correlation_id = extract_correlation_id_from_sqs_records(records)
        setup_request_context(correlation_id, context, logger)

        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_005,
        )

        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_006,
            total_records=len(records),
        )

        batch_item_failures = process_sqs_records(records, process_function, logger)

        if batch_item_failures:
            logger.log(
                OdsETLPipelineLogBase.ETL_COMMON_010,
                retry_count=len(batch_item_failures),
                total_records=len(records),
            )

        return {"batchItemFailures": batch_item_failures}

    return lambda_handler


def validate_required_fields(
    body: Dict[str, Any], required_fields: List[str], message_id: str, logger: Logger
) -> None:
    """Validate that required fields are present in the message body."""
    missing_fields = [
        field
        for field in required_fields
        if field not in body or body[field] is None or body[field] == ""
    ]

    if missing_fields:
        logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_007,
            message_id=message_id,
        )
        raise UnrecoverableError(
            message_id=message_id,
            error_type="MissingRequiredFields",
            details=f"Missing required field(s): {', '.join(missing_fields)}",
        )
