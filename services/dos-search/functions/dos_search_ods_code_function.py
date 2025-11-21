import time
from copy import deepcopy

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_service.ftrs_service import FtrsService
from functions.logging.dos_logger import dos_logger
from functions.organization_query_params import OrganizationQueryParams

logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    start = time.time()
    log_data = dos_logger.extract(app.current_event)
    details = deepcopy(dos_logger.extract_one_time(app.current_event))
    dos_logger.info("Logging one-time fields", log_data=log_data, **details)
    try:
        query_params = app.current_event.query_string_parameters or {}
        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        # Structured request log
        dos_logger.info("Received request for odsCode", ods_code=ods_code)

        ftrs_service = FtrsService()
        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except ValidationError as exception:
        # Log warning with structured fields
        dos_logger.warning(
            "Validation error occurred",
            validation_errors=exception.errors(),
        )
        fhir_resource = error_util.create_validation_error_operation_outcome(exception)
        return create_response(400, fhir_resource)
    except Exception:
        # Log exception with structured fields
        dos_logger.exception("Internal server error occurred")
        fhir_resource = error_util.create_resource_internal_server_error()
        return create_response(500, fhir_resource)
    else:
        # success path: measure and log response metrics
        duration_ms = int((time.time() - start) * 1000)
        # attempt to approximate response size (bytes)
        try:
            body = fhir_resource.model_dump_json()
            response_size = len(body.encode("utf-8"))
        except Exception:
            response_size = None

        dos_logger.info(
            "Successfully processed",
            opt_ftrs_response_time=f"{duration_ms}ms",
            opt_ftrs_response_size=response_size,
        )
        return create_response(200, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    # Log response creation with structured fields (we don't have event in this scope)
    # response details have been logged in the handler; this is an additional log point
    dos_logger.info("Creating response", status_code=status_code)
    # Clears cached log data at final stage to prevent accidental persisting of ID values
    dos_logger.clear_log_data()
    return Response(
        status_code=status_code,
        content_type="application/fhir+json",
        body=fhir_resource.model_dump_json(),
    )


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,
)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
