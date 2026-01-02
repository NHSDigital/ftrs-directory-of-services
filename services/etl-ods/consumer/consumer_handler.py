from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import fetch_or_set_correlation_id
from ftrs_common.utils.request_id import fetch_or_set_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from consumer.consumer import process_message_and_send_request

ods_consumer_logger = Logger.get(service="ods_consumer")


def consumer_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for consuming messages from SQS queue.
    """
    if event:
        correlation_id = fetch_or_set_correlation_id(
            event.get("headers", {}).get("X-Correlation-ID")
        )
        request_id = fetch_or_set_request_id(
            context_id=getattr(context, "aws_request_id", None) if context else None,
            header_id=event.get("headers", {}).get("X-Request-ID"),
        )
        ods_consumer_logger.append_keys(
            correlation_id=correlation_id, request_id=request_id
        )
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_001,
        )
        batch_item_failures = []
        sqs_batch_response = {}

        records = event.get("Records")
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_002,
            total_records=len(records) if records else 0,
        )
        for record in records:
            ods_consumer_logger.log(
                OdsETLPipelineLogBase.ETL_CONSUMER_003,
                message_id=record["messageId"],
                total_records=len(records),
            )
            try:
                process_message_and_send_request(record)
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_004,
                    message_id=record["messageId"],
                )
            except Exception:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_005,
                    message_id=record["messageId"],
                )
                batch_item_failures.append({"itemIdentifier": record["messageId"]})

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response
