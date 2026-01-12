import json
from datetime import datetime, timedelta, timezone

import requests
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    current_correlation_id,
    fetch_or_set_correlation_id,
    get_correlation_id,
)
from ftrs_common.utils.request_id import fetch_or_set_request_id, get_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.sqs_sender import send_messages_to_queue

from .extract import (
    fetch_outdated_organisations,
)

MAX_DAYS_PAST = 185
ods_extractor_logger = Logger.get(service="ods_extractor")


def processor(date: str) -> None:
    """
    Extract ODS data and send each organization to queue.
    """
    try:
        organisations = fetch_outdated_organisations(date)
        if not organisations:
            return
        _send_organisations_to_queue(organisations)

    except requests.exceptions.RequestException as e:
        ods_extractor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_022,
            error_message=str(e),
        )
        raise
    except Exception as e:
        ods_extractor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_023,
            error_message=str(e),
        )
        raise


def _send_organisations_to_queue(organisations: list[dict]) -> None:
    """Send each organization to the transform queue."""
    correlation_id = get_correlation_id()
    request_id = get_request_id()

    messages = []
    for organisation in organisations:
        message_body = {
            "organisation": organisation,
            "correlation_id": correlation_id,
            "request_id": request_id,
        }
        messages.append(message_body)

    # Send all messages using the centralized SQS sender
    send_messages_to_queue(messages, queue_suffix="transform-queue")


def extractor_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for triggering the extractor with a date parameter.
    """
    try:
        current_correlation_id.set(None)
        correlation_id = fetch_or_set_correlation_id(
            event.get("headers", {}).get("X-Correlation-ID")
        )

        request_id = fetch_or_set_request_id(
            context_id=getattr(context, "aws_request_id", None) if context else None,
            header_id=event.get("headers", {}).get("X-Request-ID"),
        )
        ods_extractor_logger.append_keys(
            correlation_id=correlation_id, request_id=request_id
        )

        is_scheduled = event.get("is_scheduled", False)
        if not is_scheduled:
            date = event.get("date")
        else:
            # if triggered by EventBridge Scheduler, use the scheduled time minus one day
            date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        if not date:
            return _error_response(400, "Date parameter is required")

        valid, error_message = _validate_date(date)
        if not valid:
            return _error_response(400, error_message)
        else:
            processor(date=date)
            return {
                "statusCode": 200,
                "message": f"Successfully processed organizations for {date}",
            }

    except Exception as e:
        ods_extractor_logger.log(
            OdsETLPipelineLogBase.ETL_EXTRACTOR_023,
            error_message=str(e),
        )
        return _error_response(500, f"Unexpected error: {e}")


def _validate_date(date_str: str) -> tuple[bool, str | None]:
    """Validate the date string for format and 185-day rule."""
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format"
    today = datetime.now(timezone.utc)
    if (today - input_date).days > MAX_DAYS_PAST:
        return False, "Date must not be more than 185 days in the past"
    return True, None


def _error_response(status_code: int, message: str) -> dict:
    ods_extractor_logger.log(
        OdsETLPipelineLogBase.ETL_EXTRACTOR_029,
        status_code=status_code,
        error_message=str(message),
    )
    return {"statusCode": status_code, "body": json.dumps({"error": message})}
