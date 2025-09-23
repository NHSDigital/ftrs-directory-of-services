import json
from datetime import datetime, timezone

import requests
from aws_lambda_powertools.tracing import Tracer
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import set_correlation_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.load_data import load_data
from pipeline.utilities import generate_correlation_id, get_correlation_id

from .extract import (
    extract_ods_code,
    fetch_ods_organisation_data,
    fetch_organisation_uuid,
    fetch_sync_data,
)
from .transform import transform_to_payload

MAX_DAYS_PAST = 185
BATCH_SIZE = 10
ods_processor_logger = Logger.get(service="ods_processor")
tracer = Tracer()


def processor(date: str) -> None:
    """
    Extract GP practice data from the source, transform to payload, and load in batches.
    """
    try:
        organisations = fetch_sync_data(date)
        if not organisations:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_020,
                date=date,
            )
            return
        transformed_batch = []
        for organisation in organisations:
            org_link = organisation.get("OrgLink")
            if not org_link:
                ods_processor_logger.log(
                    OdsETLPipelineLogBase.ETL_PROCESSOR_021,
                )
                continue
            organisation_ods_code = extract_ods_code(org_link)
            transformed_request = process_organisation(organisation_ods_code)
            if transformed_request is not None:
                transformed_batch.append(transformed_request)

            if len(transformed_batch) == BATCH_SIZE:
                load_data(transformed_batch)
                transformed_batch.clear()

        if transformed_batch:
            load_data(transformed_batch)

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


def process_organisation(ods_code: str) -> str | None:
    """
    Process a single organisation by extracting data, transforming it, and returning the payload.
    """
    try:
        correlation_id = get_correlation_id()
        organisation_data = fetch_ods_organisation_data(ods_code)
        fhir_organisation = transform_to_payload(organisation_data, ods_code)
        org_uuid = fetch_organisation_uuid(ods_code)
        fhir_organisation.id = org_uuid
        if org_uuid is None:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_027,
                ods_code=ods_code,
                error_message="Organisation UUID not found.",
            )
            return None
        return json.dumps(
            {
                "path": org_uuid,
                "body": fhir_organisation.model_dump(),
                "correlation_id": correlation_id,
            }
        )

    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_027,
            ods_code=ods_code,
            error_message=str(e),
        )
        return None


def processor_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for triggering the processor with a date parameter.
    """
    try:
        correlation_id = generate_correlation_id()
        set_correlation_id(correlation_id)
        ods_processor_logger.append_keys(correlation_id=correlation_id)

        date = event.get("date")
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
