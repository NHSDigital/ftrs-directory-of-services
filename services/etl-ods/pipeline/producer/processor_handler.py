import json
from datetime import datetime, timedelta, timezone

from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    current_correlation_id,
    fetch_or_set_correlation_id,
)
from ftrs_common.utils.request_id import fetch_or_set_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.producer.processor import processor

ods_processor_logger = Logger.get(service="ods_processor")

MAX_DAYS_PAST = 185


def processor_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for triggering the processor with a date parameter.
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
        ods_processor_logger.append_keys(
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
            return {"statusCode": 200, "body": "Processing complete"}

    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_023,
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
        return False, f"Date must not be more than {MAX_DAYS_PAST} days in the past"
    return True, None


def _error_response(status_code: int, message: str) -> dict:
    ods_processor_logger.log(
        OdsETLPipelineLogBase.ETL_PROCESSOR_029,
        status_code=status_code,
        error_message=str(message),
    )
    return {"statusCode": status_code, "body": json.dumps({"error": message})}
