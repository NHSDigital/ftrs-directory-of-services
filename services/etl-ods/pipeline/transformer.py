import json

from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    correlation_id_context,
    current_correlation_id,
)
from ftrs_common.utils.request_id import current_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.sqs_sender import send_messages_to_queue

from .extract import (
    fetch_organisation_uuid,
)
from .transform import transform_to_payload

BATCH_SIZE = 10
ods_processor_logger = Logger.get(service="ods_processor")


def _process_organisation(organisation: dict) -> str | None:
    """Process a single organisation - exact same function from processor.py"""
    ods_code = None
    try:
        correlation_id = current_correlation_id.get()
        request_id = current_request_id.get()

        fhir_organisation = transform_to_payload(organisation)
        ods_code = fhir_organisation.identifier[0].value

        org_uuid = fetch_organisation_uuid(ods_code)
        if org_uuid is None:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_027,
                ods_code=ods_code,
                error_message="Organisation UUID not found in internal system.",
            )
            return None

        fhir_organisation.id = org_uuid

        return json.dumps(
            {
                "path": org_uuid,
                "body": fhir_organisation.model_dump(),
                "correlation_id": correlation_id,
                "request_id": request_id,
            }
        )
    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_027,
            ods_code=ods_code if ods_code else "unknown",
            error_message=str(e),
        )
        return None


def transformer_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for processing individual organizations from SQS queue.
    """
    if not event:
        return {"batchItemFailures": []}

    batch_item_failures = []
    records = event.get("Records", [])
    transformed_batch = []

    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_CONSUMER_002,
        total_records=len(records),
    )

    for record in records:
        message_id = record["messageId"]

        try:
            # Parse the message body
            body = json.loads(record["body"])
            organisation = body.get("organisation")
            correlation_id = body.get("correlation_id")
            request_id = body.get("request_id")

            if not organisation or not correlation_id or not request_id:
                ods_processor_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_006,
                    message_id=message_id,
                )
                batch_item_failures.append({"itemIdentifier": message_id})
                continue

            # Set context for logging
            with correlation_id_context(correlation_id):
                current_request_id.set(request_id)
                ods_processor_logger.append_keys(
                    correlation_id=correlation_id, request_id=request_id
                )

                ods_processor_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_003,
                    message_id=message_id,
                    total_records=len(records),
                )

                # Process the organization using the exact same function
                transformed_request = _process_organisation(organisation)
                if transformed_request is not None:
                    transformed_batch.append(transformed_request)

                    # Send data in batches of BATCH_SIZE to final queue
                    if len(transformed_batch) == BATCH_SIZE:
                        send_messages_to_queue(transformed_batch, queue_suffix="queue")
                        transformed_batch.clear()

                ods_processor_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_004,
                    message_id=message_id,
                )

        except Exception:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_CONSUMER_005,
                message_id=message_id,
            )
            batch_item_failures.append({"itemIdentifier": message_id})

    # Send any remaining transformed data to final queue
    if transformed_batch:
        send_messages_to_queue(transformed_batch, queue_suffix="queue")

    return {"batchItemFailures": batch_item_failures}
