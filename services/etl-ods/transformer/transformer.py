from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import current_correlation_id
from ftrs_common.utils.request_id import current_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.exceptions import UnrecoverableError
from common.message_utils import create_message_payload
from common.sqs_processor import (
    extract_record_metadata,
    process_sqs_records,
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


def _raise_transformation_error(
    message_id: str, transform_error: Exception, ods_code: str = "<unknown>"
) -> None:
    """Raise UnrecoverableError for transformation failures."""
    error_message = f"Transformation failed: {type(transform_error).__name__}: {str(transform_error)}"
    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
        ods_code=ods_code,
        error_message=error_message,
    )
    raise UnrecoverableError(
        message_id=message_id,
        error_type="TRANSFORMATION_FAILURE",
        details=error_message,
    )


def _raise_no_identifier_error(message_id: str) -> None:
    """Raise UnrecoverableError when organisation has no identifier."""
    error_message = "Organisation has no identifier after transformation"
    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
        ods_code="<no identifier>",
        error_message=error_message,
    )
    raise UnrecoverableError(
        message_id=message_id,
        error_type="INVALID_FHIR_NO_IDENTIFIER",
        details=error_message,
    )


def _transform_organisation(organisation: dict, message_id: str) -> str:
    """
    Transform organisation data to FHIR payload.

    Returns:
        str: JSON payload if successful

    Raises:
        PermanentProcessingError: For permanent failures (404) - consumed by sqs_processor
        UnrecoverableError: For transformation/validation failures - goes to DLQ
        RateLimitError: For rate limits - retries then DLQ
        Exception: For other errors - retries then DLQ
    """
    ods_code = "<unknown>"

    # Transform to FHIR - if this fails, it's a bug in our transformation logic
    try:
        fhir_organisation = transform_to_payload(organisation)
    except Exception as transform_error:
        _raise_transformation_error(message_id, transform_error, ods_code)

    # Validate identifier exists - invalid FHIR = code bug, treat like 400
    if not fhir_organisation.identifier:
        _raise_no_identifier_error(message_id)

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
        PermanentProcessingError: Permanent failure - consumed by sqs_processor
        UnrecoverableError: Unrecoverable failure - goes to DLQ
        RateLimitError: Rate limited - retries then DLQ
        Exception: Processing error - retries then DLQ
    """
    metadata = extract_record_metadata(record)
    message_id = metadata["message_id"]
    body = metadata["body"]

    # Validate required fields - raises UnrecoverableError if missing
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

    # Transform organisation - raises PermanentProcessingError for permanent failures
    return _transform_organisation(body["organisation"], message_id)


def _send_batch_safely(batch: list[str], queue_suffix: str) -> None:
    """
    Send batch to queue without crashing the lambda.

    If sending fails, logs error but doesn't raise to prevent
    retrying already-processed source messages.
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


def transformer_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for transforming organisations from SQS.

    Error handling strategy:
    - Permanent failures (404, 422): Consumed immediately, never go to DLQ
    - Message integrity errors: Go directly to DLQ
    - Rate limits: Retry, then DLQ after max attempts
    - Other errors: Retry, then DLQ after max attempts
    """
    start_time = time.time()

    if not event:
        return {"batchItemFailures": []}

    records = event.get("Records", [])
    correlation_id = extract_correlation_id_from_sqs_records(records)
    setup_request_context(correlation_id, context, ods_transformer_logger)

    ods_transformer_logger.log(OdsETLPipelineLogBase.ETL_TRANSFORMER_028)
    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_029,
        total_records=len(records),
    )

    transformed_batch = []

    def process_and_batch(record: dict) -> None:
        """Process record and batch successful transformations."""
        payload = _process_record(record)

        # Add to batch and send when full
        transformed_batch.append(payload)
        if len(transformed_batch) >= BATCH_SIZE:
            _send_batch_safely(transformed_batch, "load-queue")
            transformed_batch.clear()

    # Process all records with standardized error handling
    batch_item_failures = process_sqs_records(
        records,
        process_and_batch,
        ods_transformer_logger,
    )

    # Send any remaining messages
    _send_batch_safely(transformed_batch, "load-queue")

    if batch_item_failures:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_TRANSFORMER_030,
            retry_count=len(batch_item_failures),
            total_records=len(records),
        )

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
