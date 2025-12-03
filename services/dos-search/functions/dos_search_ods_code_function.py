import time

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_service.ftrs_service import FtrsService
from functions.logger.dos_logger import DosLogger
from functions.organization_query_params import OrganizationQueryParams

service = "dos-search"
dos_logger = DosLogger.get(service=service)
logger = dos_logger.logger
tracer = Tracer()
app = APIGatewayRestResolver()


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    start = time.time()
    dos_logger.init(app.current_event)
    try:
        query_params = app.current_event.query_string_parameters or {}
        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        # Structured request log
        dos_logger.info(
            "Received request for odsCode",
            ods_code=ods_code,
            dos_message_category="REQUEST",
        )

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
        try:
            # attempt to approximate response size (bytes)
            body = fhir_resource.model_dump_json()
            response_size = len(body.encode("utf-8"))
        except Exception:
            response_size = None
            dos_logger.exception("Failed to calculate response size")

        dos_logger.info(
            "Successfully processed: Logging response time & size",
            opt_ftrs_response_time=f"{duration_ms}ms",
            opt_ftrs_response_size=response_size,
            dos_message_category="METRICS",
        )
        return create_response(200, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    # Log response creation with structured fields (we don't have event in this scope)
    # response details have been logged in the handler; this is an additional log point
    body = fhir_resource.model_dump_json()
    dos_logger.info(
        "Creating response",
        status_code=status_code,
        body=body,
        dos_message_category="RESPONSE",
    )
    return Response(
        status_code=status_code,
        content_type="application/fhir+json",
        body=body,
    )


@logger.inject_lambda_context(
    correlation_id_path=correlation_paths.API_GATEWAY_REST,
    log_event=True,
    clear_state=True,  # This should be sufficient to handle the clearing of any keys appended during execution
)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
