import json
import os
import time
from http import HTTPStatus

import requests
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    correlation_id_context,
    current_correlation_id,
)
from ftrs_common.utils.request_id import (
    current_request_id,
    fetch_or_set_request_id,
)
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.extract import (
    fetch_organisation_uuid,
)
from common.sqs_sender import send_messages_to_queue

from .transform import transform_to_payload


class RateLimitExceededException(Exception):
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        self.message = message
        super().__init__(self.message)


BATCH_SIZE = 10
ods_transformer_logger = Logger.get(service="ods_transformer")


def _process_organisation(organisation: dict) -> str | None:
    ods_code = None
    try:
        correlation_id = current_correlation_id.get()
        request_id = current_request_id.get()

        fhir_organisation = transform_to_payload(organisation)
        ods_code = fhir_organisation.identifier[0].value

        org_uuid = fetch_organisation_uuid(ods_code)
        if org_uuid is None:
            ods_transformer_logger.log(
                OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
                ods_code=ods_code,
                error_message="Organisation UUID not found in internal system.",
            )
            return None

        fhir_organisation.id = org_uuid

        return json.dumps(
            {
                "path": org_uuid,
                "body": fhir_organisation.model_dump(mode="json"),
                "correlation_id": correlation_id,
                "request_id": request_id,
            }
        )
    except requests.exceptions.HTTPError as http_err:
        if (
            http_err.response is not None
            and http_err.response.status_code == HTTPStatus.TOO_MANY_REQUESTS
        ):
            ods_transformer_logger.log(
                OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
                ods_code=ods_code if ods_code else "unknown",
                error_message=f"Rate limit exceeded: {str(http_err)}",
            )
            raise RateLimitExceededException()
        else:
            ods_transformer_logger.log(
                OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
                ods_code=ods_code if ods_code else "unknown",
                error_message=str(http_err),
            )
            return None
    except Exception as e:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_TRANSFORMER_027,
            ods_code=ods_code if ods_code else "unknown",
            error_message=str(e),
        )
        return None


def _handle_rate_limit_error(
    message_id: str, receive_count: int, error: RateLimitExceededException
) -> None:
    """Handle rate limit exceeded errors with appropriate logging."""
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT"))
    if receive_count >= max_receive_count:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_009,
            message_id=message_id,
            receive_count=receive_count,
            error_message=f"Rate limit exceeded - final attempt, message will be sent to DLQ (attempt {receive_count}/{max_receive_count})",
            exception=error,
        )
    else:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_009,
            message_id=message_id,
            receive_count=receive_count,
            error_message=f"Rate limit exceeded - message will be retried (attempt {receive_count}/{max_receive_count})",
        )


def _handle_general_error(message_id: str, receive_count: int) -> None:
    """Handle general processing errors with appropriate logging."""
    max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT"))
    if receive_count >= max_receive_count:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_005,
            message_id=message_id,
            error_message=f"Processing failed - final attempt, message will be sent to DLQ (attempt {receive_count}/{max_receive_count})",
        )
    else:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_005,
            message_id=message_id,
            error_message=f"Processing failed - message will be retried (attempt {receive_count}/{max_receive_count})",
        )


def _process_single_record(
    record: dict, transformed_batch: list, batch_item_failures: list
) -> None:
    """Process a single SQS record."""
    message_id = record["messageId"]
    receive_count = int(record["attributes"]["ApproximateReceiveCount"])

    try:
        # Parse the message body
        body = json.loads(record["body"])
        organisation = body.get("organisation")
        correlation_id = body.get("correlation_id")
        request_id = body.get("request_id")

        if not organisation or not correlation_id or not request_id:
            ods_transformer_logger.log(
                OdsETLPipelineLogBase.ETL_CONSUMER_006,
                message_id=message_id,
            )
            batch_item_failures.append({"itemIdentifier": message_id})
            return

        # Set context for logging
        with correlation_id_context(correlation_id):
            current_request_id.set(request_id)
            ods_transformer_logger.append_keys(
                correlation_id=correlation_id, request_id=request_id
            )

            ods_transformer_logger.log(
                OdsETLPipelineLogBase.ETL_EXTRACTOR_003,
                message_id=message_id,
                receive_count=receive_count,
            )

            # Process the organization using the exact same function
            transformed_request = _process_organisation(organisation)
            if transformed_request is not None:
                transformed_batch.append(transformed_request)

                # Send data in batches of BATCH_SIZE to final queue
                if len(transformed_batch) == BATCH_SIZE:
                    send_messages_to_queue(transformed_batch, queue_suffix="load-queue")
                    transformed_batch.clear()

                ods_transformer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_004,
                    message_id=message_id,
                )

    except RateLimitExceededException as rate_limit_error:
        _handle_rate_limit_error(message_id, receive_count, rate_limit_error)
        batch_item_failures.append({"itemIdentifier": message_id})
    except Exception:
        _handle_general_error(message_id, receive_count)
        batch_item_failures.append({"itemIdentifier": message_id})


def transformer_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for processing individual organizations from SQS queue.
    """
    start_time = time.time()

    if not event:
        return {"batchItemFailures": []}

    correlation_id = event.get("headers", {}).get("X-Correlation-ID")
    request_id = fetch_or_set_request_id(
        context_id=getattr(context, "aws_request_id", None) if context else None,
        header_id=event.get("headers", {}).get("X-Request-ID"),
    )

    ods_transformer_logger.append_keys(
        correlation_id=correlation_id, request_id=request_id
    )

    # Log Transformer start
    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_TRANSFORMER_START,
        lambda_name="etl-ods-transformer",
    )

    batch_item_failures = []
    records = event.get("Records", [])
    transformed_batch = []
    successful_count = 0
    failed_count = 0

    ods_transformer_logger.log(
        OdsETLPipelineLogBase.ETL_CONSUMER_002,
        total_records=len(records),
    )

    for record in records:
        initial_failures = len(batch_item_failures)
        _process_single_record(record, transformed_batch, batch_item_failures)

        if len(batch_item_failures) > initial_failures:
            failed_count += 1
        else:
            successful_count += 1

    # Send any remaining transformed data to final queue
    if transformed_batch:
        send_messages_to_queue(transformed_batch, queue_suffix="load-queue")

    # Log the number of messages being sent for retry
    if batch_item_failures:
        ods_transformer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_010,
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
