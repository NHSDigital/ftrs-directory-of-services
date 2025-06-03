import json
import logging
import os
from pipeline.utilities import get_base_crud_api_url, make_request
import requests
from http import HTTPStatus


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def consumer_lambda_handler(event: dict, context: any) -> None:
    if event:
        logger.info("Received event for ODS ETL consumer lambda.")
        batch_item_failures = []
        sqs_batch_response = {}

        records = event.get("Records")
        logger.info(f"Records received: {records}")
        for record in records:
            logger.info(
                f"Processing message id: {record['messageId']} of {len(records)} from ODS ETL queue."
            )
            try:
                process_message_and_send_request(record)
                logger.info(
                    f"Message id: {record['messageId']} processed successfully."
                )
            except Exception:
                logger.exception(
                    f"Failed to process message id: {record['messageId']}."
                )
                batch_item_failures.append({"itemIdentifier": record["messageId"]})

        sqs_batch_response["batchItemFailures"] = batch_item_failures
        return sqs_batch_response


def process_message_and_send_request(record: dict) -> None:
    if isinstance(record.get("body"), str):
        body_content = json.loads(json.loads(record.get("body")))
        path = body_content.get("path")
        body = body_content.get("body")

    else:
        path = record.get("path")
        body = record.get("body")

    if not path or not body:
        err_msg = (
            f"Message id: {record['messageId']} is missing 'path' or 'body' fields."
        )
        logger.warning(err_msg)
        raise ValueError(err_msg)

    api_url = get_base_crud_api_url() + "/organisation" + path

    try:
        response = make_request(api_url, method="PUT", sign=True, json=body)
        logger.info(
            f"Successfully sent request. Response status code: {response.status_code}"
        )

    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            logger.warning(
                f"Bad request returned for message id: {record['messageId']}. Not re-processing."
            )
            return

        logger.exception(f"Request failed for message id: {record['messageId']}.")
        raise RequestProcessingError(
            message_id=record["messageId"],
            status_code=(http_error.response.status_code),
            response_text=str(http_error),
        )


class RequestProcessingError(Exception):
    def __init__(self, message_id: str, status_code: int, response_text: str) -> None:
        self.message_id = message_id
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"Message id: {message_id}, Status Code: {status_code}, Response: {response_text}"
        )
