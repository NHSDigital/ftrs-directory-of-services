import json
import re

import requests
from ftrs_common.logger import Logger
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from pipeline.load_data import load_data
from .extract import (
    extract_ods_code,
    fetch_ods_organisation_data,
    fetch_organisation_uuid,
    fetch_sync_data,
)
from .transform import transform_to_payload

BATCH_SIZE = 10
ods_processor_logger = Logger.get(service="ods_processor")


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
        organisation_data = fetch_ods_organisation_data(ods_code)
        fhir_organisation = transform_to_payload(organisation_data, ods_code)
        org_uuid = fetch_organisation_uuid(ods_code)
        if org_uuid is None:
            ods_processor_logger.log(
                OdsETLPipelineLogBase.ETL_PROCESSOR_027,
                ods_code=ods_code,
                error_message="Organisation UUID not found.",
            )
            return None
        return json.dumps({"path": org_uuid, "body": fhir_organisation})

    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_027,
            ods_code=ods_code,
            error_message=str(e),
        )
        return None  # Explicitly return None on error


def processor_lambda_handler(event: dict, context: any) -> dict:
    """
    Lambda handler for triggering the processor with a date parameter.
    """
    try:
        date = event.get("date")
        if not date:
            return {"statusCode": 400, "body": "Date parameter is required"}
        date_pattern = r"^\d{4}-\d{2}-\d{2}$"
        if not re.match(date_pattern, date):
            return {"statusCode": 400, "body": "Date must be in YYYY-MM-DD format"}

        processor(date=date)
        return {"statusCode": 200, "body": "Processing complete"}

    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_023,
            error_message=str(e),
        )
        return {"statusCode": 500, "body": f"Unexpected error: {e}"}
