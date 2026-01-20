from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from consumer.consumer import process_message_and_send_request
from consumer.request_context import (
    extract_correlation_id_from_sqs_records,
    setup_request_context,
)

ods_consumer_logger = Logger.get(service="ods_consumer")


def consumer_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for consuming messages from SQS queue.
    """
    if event:
        records = event.get("Records", [])
        correlation_id = extract_correlation_id_from_sqs_records(records)

        setup_request_context(correlation_id, context, ods_consumer_logger)
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_001,
        )
        batch_item_failures = []
        sqs_batch_response = {}

        records = event.get("Records", [])
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_002,
            total_records=len(records),
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
