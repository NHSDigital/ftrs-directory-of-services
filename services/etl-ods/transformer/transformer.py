from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import current_correlation_id
from ftrs_common.utils.request_id import current_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.error_handling import (
    handle_general_error,
    handle_permanent_error,
    handle_retryable_error,
)
from common.exceptions import PermanentProcessingError, RetryableProcessingError
from common.message_utils import create_message_payload
from common.sqs_processor import (
    extract_record_metadata,
    validate_required_fields,
)
from common.sqs_request_context import (
    extract_correlation_id_from_sqs_records,
    setup_request_context,
)
from common.sqs_sender import send_messages_to_queue
from transformer.transform import transform_to_payload
from transformer.uuid_fetcher import fetch_organisation_uuid

BATCH_SIZE = 10
ods_transformer_logger = Logger.get(service="ods_transformer")


def _send_batch_safely(batch: list[str], queue_suffix: str) -> None:
    """
    Send batch to queue with error handling to prevent loss of messages and ensure visibility of failures.
    """
    if not batch:
        return

    try:
        send_messages_to_queue(batch, queue_suffix=queue_suffix)
    except Exception as err:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_COMMON_020,
            error_message=f"Failed to send batch to {queue_suffix}: {str(err)}. Transformed messages lost.",
        )


def _transform_organisation(organisation: dict, message_id: str) -> str:
    """
    Transform organisation data to FHIR payload.

    Returns:
        str: JSON payload if successful

    Raises:
        Exception: For transformation or validation failures - handled by SQS handler
    """
    ods_code = "<unknown>"

    # Transform to FHIR - if this fails, it's a bug in our transformation logic
    try:
        fhir_organisation = transform_to_payload(organisation)
    except Exception as transform_error:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
            ods_code=ods_code,
            error_message=f"Transformation failed: {type(transform_error).__name__}: {str(transform_error)}",
            exception_type=type(transform_error).__name__,
            exception_details=str(transform_error)[:500],
            troubleshooting_info=f"Transformation failed for ODS {ods_code} in message {message_id}. Review data structure and transformation logic.",
        )
        raise PermanentProcessingError(
            message_id=message_id,
            status_code=400,
            response_text=f"Transformation failed: {str(transform_error)}",
        )

    # Validate identifier exists - invalid FHIR = code bug, treat like 400
    if not fhir_organisation.identifier:
        raise PermanentProcessingError(
            message_id=message_id,
            status_code=400,
            response_text="No ODS code identifier found in organization",
        )

    ods_code = fhir_organisation.identifier[0].value

    # Fetch UUID for organisation (raises PermanentProcessingError for 404)
    org_uuid = fetch_organisation_uuid(ods_code, message_id)

    # Build payload
    correlation_id = current_correlation_id.get()
    request_id = current_request_id.get()
    fhir_organisation.id = org_uuid
    payload = create_message_payload(
        path=org_uuid,
        body=fhir_organisation.model_dump(),
        correlation_id=correlation_id,
        request_id=request_id,
    )

    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_026,
        ods_code=ods_code,
    )
    return payload


def _process_record(record: dict) -> str:
    """
    Process a single SQS record.

    Returns:
        str: Transformed payload if successful

    Raises:
        PermanentProcessingError: Permanent failure - consumed immediately
        RetryableProcessingError: Retryable failure - retries then DLQ
        Exception: Processing error - retries then DLQ
    """
    metadata = extract_record_metadata(record)
    message_id = metadata["message_id"]
    body = metadata["body"]

    validate_required_fields(
        body,
        ["organisation"],
        message_id,
        ods_transformer_logger,
    )

    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_EXTRACTOR_003,
        message_id=message_id,
    )

    return _transform_organisation(body["organisation"], message_id)


def process_transformation_message_with_batching(
    event: dict, context: LambdaContext
) -> dict:
    """Process SQS event with request-scoped batching for safety and performance."""
    if not event:
        return {"batchItemFailures": []}

    records = event.get("Records", [])

    correlation_id = extract_correlation_id_from_sqs_records(records)
    setup_request_context(correlation_id, context, ods_transformer_logger)

    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_029,
        total_records=len(records),
    )

    message_batch = []
    batch_item_failures = []

    def send_batch_if_full() -> None:
        """Send batch when it reaches batch size."""
        if len(message_batch) >= BATCH_SIZE:
            _send_batch_safely(message_batch.copy(), "load-queue")
            message_batch.clear()

    for record in records:
        try:
            payload = _process_record(record)

            message_batch.append(payload)
            send_batch_if_full()

        except PermanentProcessingError as permanent_error:
            message_id = record.get("messageId", "unknown")
            handle_permanent_error(message_id, permanent_error, ods_transformer_logger)
            # Permanent errors are consumed immediately (no retry, no DLQ)

        except RetryableProcessingError as retryable_error:
            message_id = record.get("messageId", "unknown")
            receive_count = int(
                record.get("attributes", {}).get("ApproximateReceiveCount", "1")
            )
            handle_retryable_error(
                message_id, receive_count, retryable_error, ods_transformer_logger
            )
            batch_item_failures.append({"itemIdentifier": message_id})

        except Exception as e:
            message_id = record.get("messageId", "unknown")
            receive_count = int(
                record.get("attributes", {}).get("ApproximateReceiveCount", "1")
            )
            handle_general_error(message_id, receive_count, e, ods_transformer_logger)
            batch_item_failures.append({"itemIdentifier": message_id})

    if message_batch:
        _send_batch_safely(message_batch, "load-queue")

    # Log batch processing completion
    duration_ms = round((time.time() - start_time) * 1000, 2)
    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_BATCH_COMPLETE,
        lambda_name="etl-ods-transformer",
        duration_ms=duration_ms,
        total_records=len(records),
        successful_count=successful_count,
        failed_count=failed_count,
        batch_status="completed" if failed_count == 0 else "completed_with_failures",
    )

    return {"batchItemFailures": batch_item_failures}


transformer_lambda_handler = process_transformation_message_with_batching
