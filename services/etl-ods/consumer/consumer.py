import json
import os
import time
from http import HTTPStatus

import requests
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    correlation_id_context,
    fetch_or_set_correlation_id,
)
from ftrs_common.utils.request_id import fetch_or_set_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from common.utils import get_base_apim_api_url, make_request

ods_consumer_logger = Logger.get(service="ods_consumer")


class RateLimitExceededException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class RequestProcessingError(Exception):
    def __init__(self, message_id: str, status_code: int, response_text: str) -> None:
        self.message_id = message_id
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )


def _handle_records(records: dict) -> tuple[list[dict], int, int]:
    batch_item_failures = []
    successful_count = 0
    failed_count = 0

    for record in records:
        message_id = record["messageId"]
        receive_count = int(record["attributes"]["ApproximateReceiveCount"])

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
            successful_count += 1
        except RateLimitExceededException as rate_limit_error:
            max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT"))
            if receive_count >= max_receive_count:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_010,
                    message_id=message_id,
                    receive_count=receive_count,
                    error_message=f"Rate limit exceeded - final attempt, message will be sent to DLQ (attempt {receive_count}/{max_receive_count})",
                    exception=rate_limit_error,
                )
            else:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_010,
                    message_id=message_id,
                    receive_count=receive_count,
                    error_message=f"Rate limit exceeded - message will be retried (attempt {receive_count}/{max_receive_count})",
                )
            batch_item_failures.append({"itemIdentifier": record["messageId"]})
        except Exception:
            max_receive_count = int(os.environ.get("MAX_RECEIVE_COUNT"))
            if receive_count >= max_receive_count:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_005,
                    message_id=record["messageId"],
                    error_message=f"Processing failed - final attempt, message will be sent to DLQ (attempt {receive_count}/{max_receive_count})",
                )
            else:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_005,
                    message_id=record["messageId"],
                    error_message=f"Processing failed - message will be retried (attempt {receive_count}/{max_receive_count})",
                )
            batch_item_failures.append({"itemIdentifier": record["messageId"]})
            failed_count += 1

    return batch_item_failures, successful_count, failed_count


def consumer_lambda_handler(event: dict, context: any) -> dict:
    start_time = time.time()

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

        # Log Consumer start
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_001,
            lambda_name="etl-ods-consumer",
            etl_stage="consumer_start",
        )

        sqs_batch_response = {}

        records = event.get("Records")
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_002,
            total_records=len(records) if records else 0,
        )

        batch_item_failures, successful_count, failed_count = _handle_records(
            records or []
        )

        if batch_item_failures:
            ods_consumer_logger.log(
                OdsETLPipelineLogBase.ETL_CONSUMER_010,
                retry_count=len(batch_item_failures),
                total_records=len(records),
            )

        sqs_batch_response["batchItemFailures"] = batch_item_failures

        # Log batch processing completion
        duration_ms = round((time.time() - start_time) * 1000, 2)
        ods_consumer_logger.log(
            OdsETLPipelineLogBase.ETL_CONSUMER_BATCH_COMPLETE,
            lambda_name="etl-ods-consumer",
            etl_stage="consumer_batch_complete",
            duration_ms=duration_ms,
            total_records=len(records) if records else 0,
            successful_count=successful_count,
            failed_count=failed_count,
            batch_status="completed"
            if failed_count == 0
            else "completed_with_failures",
        )

        return sqs_batch_response


def process_message_and_send_request(record: dict) -> None:
    if isinstance(record.get("body"), str):
        body_content = json.loads(record.get("body"))
        path = body_content.get("path")
        body = body_content.get("body")
        correlation_id = body_content.get("correlation_id")

    else:
        path = record.get("path")
        body = record.get("body")
        correlation_id = record.get("correlation_id")

    message_id = record["messageId"]

    correlation_id = fetch_or_set_correlation_id(correlation_id)

    with correlation_id_context(correlation_id):
        ods_consumer_logger.append_keys(correlation_id=correlation_id)

        if not path or not body:
            err_msg = ods_consumer_logger.log(
                OdsETLPipelineLogBase.ETL_CONSUMER_006,
                message_id=message_id,
            )
            raise ValueError(err_msg)

        api_url = get_base_apim_api_url()
        api_url = api_url + "/Organization/" + path

        try:
            response_data = make_request(
                api_url, method="PUT", json=body, jwt_required=True
            )
            ods_consumer_logger.log(
                OdsETLPipelineLogBase.ETL_CONSUMER_007,
                status_code=response_data.get("status_code", "unknown"),
            )
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_008, message_id=message_id
                )
                return
            elif http_error.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_009,
                    message_id=message_id,
                    status_code=HTTPStatus.TOO_MANY_REQUESTS,
                    error_message=f"Rate limit exceeded: {str(http_error)}",
                )
                raise RateLimitExceededException()
            else:
                ods_consumer_logger.log(
                    OdsETLPipelineLogBase.ETL_CONSUMER_009,
                    message_id=record["messageId"],
                )
                raise RequestProcessingError(
                    message_id=message_id,
                    status_code=(http_error.response.status_code),
                    response_text=str(http_error),
                )
