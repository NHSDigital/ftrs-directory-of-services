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

from pipeline.load_data import load_data
from pipeline.validation import get_permitted_org_type

from .extract import (
    fetch_organisation_uuid,
    fetch_outdated_organisations,
)
from .transform import transform_to_payload

MAX_DAYS_PAST = 185
BATCH_SIZE = 10
ods_processor_logger = Logger.get(service="ods_processor")


def processor(date: str) -> None:
    """
    Extract ODS data, transform to payload, and load in batches.
    """
    try:
        organisations = fetch_outdated_organisations(date)
        if not organisations:
            return
        _batch_and_load_organisations(organisations)

    except requests.exceptions.RequestException as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_022,
            error_message=str(e),
        )
        raise
    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_023,
            error_message=str(e),
        )
        raise


def _batch_and_load_organisations(organisations: list[dict]) -> None:
    transformed_batch = []

    for organisation in organisations:
        transformed_request = _process_organisation(organisation)
        if transformed_request is not None:
            transformed_batch.append(transformed_request)

            if len(transformed_batch) == BATCH_SIZE:
                load_data(transformed_batch)
                transformed_batch.clear()

    if transformed_batch:
        load_data(transformed_batch)


def _process_organisation(organisation: dict) -> str | None:
    ods_code = None
    try:
        correlation_id = get_correlation_id()
        request_id = get_request_id()

        permitted_org_type, non_primary_roles = get_permitted_org_type(organisation)
        if not permitted_org_type:
            return None

        fhir_organisation = transform_to_payload(
            organisation, permitted_org_type, non_primary_roles
        )
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
