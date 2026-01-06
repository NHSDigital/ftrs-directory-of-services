import json

import requests
from ftrs_common.logger import Logger
from ftrs_common.utils.correlation_id import (
    get_correlation_id,
)
from ftrs_common.utils.request_id import get_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase

from producer.extract import (
    fetch_organisation_uuid,
    fetch_outdated_organisations,
)
from producer.load_data import load_data
from producer.transform import transform_to_payload

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
        return _build_sqs_message(org_uuid, fhir_organisation)

    except Exception as e:
        ods_processor_logger.log(
            OdsETLPipelineLogBase.ETL_PROCESSOR_027,
            ods_code=ods_code if ods_code else "unknown",
            error_message=str(e),
        )
        return None


def _build_sqs_message(org_uuid: str, fhir_organisation: any) -> str:
    correlation_id = get_correlation_id()
    request_id = get_request_id()

    return json.dumps(
        {
            "path": org_uuid,
            "body": fhir_organisation.model_dump(),
            "correlation_id": correlation_id,
            "request_id": request_id,
        }
    )
