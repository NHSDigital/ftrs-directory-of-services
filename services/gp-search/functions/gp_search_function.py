from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import (
    SchemaValidationError,
    validate,
)
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel

from functions import error_util, json_schemas
from functions.ftrs_service.ftrs_service import FtrsService

logger = Logger()
tracer = Tracer()


# noinspection PyUnusedLocal
@logger.inject_lambda_context(log_event=True, clear_state=True)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    logger.debug(
        "Received event and context", extra={"event": event, "context": context}
    )
    try:
        event = normalize_event(event)
        validate(event, json_schemas.INPUT_EVENT)

        ods_code = event["odsCode"]
        logger.append_keys(ods_code=ods_code)

        ftrs_service = FtrsService()

        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except SchemaValidationError as exception:
        logger.warning("Schema validation error occurred", exc_info=exception)
        fhir_resource = error_util.create_resource_validation_error(exception)
        return create_response(422, fhir_resource)
    except Exception:
        logger.exception("Internal server error occurred")
        fhir_resource = error_util.create_resource_internal_server_error()
        return create_response(500, fhir_resource)
    else:
        logger.info("Successfully processed")
        return create_response(200, fhir_resource)


def normalize_event(event: dict) -> dict:
    if "odsCode" in event and isinstance(event["odsCode"], str):
        event["odsCode"] = event["odsCode"].upper()
    return event


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> dict:
    logger.info("Creating response", extra={"status_code": status_code})
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/fhir+json"},
        "body": fhir_resource.model_dump_json(),
    }
