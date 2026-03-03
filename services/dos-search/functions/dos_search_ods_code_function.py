import time

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.event_handler.middlewares import NextMiddleware
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.logger import Logger
from pydantic import ValidationError

from functions import error_util
from functions.event_context import (
    MANDATORY_LOG_KEYS,
    get_response_size_and_duration,
    setup_request,
)
from functions.ftrs_service.ftrs_service import FtrsService
from functions.logbase import DosSearchLogBase
from functions.organization_headers import OrganizationHeaders
from functions.organization_query_params import OrganizationQueryParams

service = "dos-search"
logger = Logger.get(service=service)
tracer = Tracer()


def request_context_middleware(
    app: APIGatewayRestResolver, next_middleware: NextMiddleware
) -> Response:
    setup_request(app.current_event, logger)
    try:
        return next_middleware(app)
    finally:
        logger.remove_keys(*MANDATORY_LOG_KEYS)


app = APIGatewayRestResolver()
app.use([request_context_middleware])


DEFAULT_RESPONSE_HEADERS: dict[str, str] = {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": ", ".join(
        sorted(OrganizationHeaders.get_allowed_headers())
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Cache-Control": "no-store",
}


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    start = time.time()
    try:
        try:
            OrganizationHeaders.model_validate(app.current_event.headers)
        except ValidationError as exception:
            return handle_event_validation_error(exception, start)

        try:
            validated_params = OrganizationQueryParams.model_validate(
                app.current_event.query_string_parameters
            )
        except ValidationError as exception:
            return handle_event_validation_error(exception, start)

        ods_code = validated_params.ods_code
        # Structured request log
        logger.log(
            DosSearchLogBase.DOS_SEARCH_002,
            ods_code=ods_code,
            dos_message_category="REQUEST",
        )

        ftrs_service = FtrsService()
        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except Exception as exc:
        logger.exception("Unhandled exception")
        return handle_general_exception(exc, start)
    else:
        # success path: measure and log response metrics
        response_size, duration_ms = get_response_size_and_duration(
            fhir_resource, start, logger
        )

        logger.log(
            DosSearchLogBase.DOS_SEARCH_003,
            dos_response_time=f"{duration_ms}ms",
            dos_response_size=response_size,
            dos_message_category="METRICS",
        )
        return create_response(200, fhir_resource)


def handle_event_validation_error(exception: ValidationError, start: float) -> Response:
    fhir_resource = error_util.create_validation_error_operation_outcome(exception)

    response_size, duration_ms = get_response_size_and_duration(
        fhir_resource, start, logger
    )
    logger.log(
        DosSearchLogBase.DOS_SEARCH_005,
        validation_errors=exception.errors(),
        dos_response_time=f"{duration_ms}ms",
        dos_response_size=response_size,
    )
    return create_response(400, fhir_resource)


def handle_general_exception(exc: Exception, start: float) -> Response:
    fhir_resource = error_util.create_resource_internal_server_error()

    response_size, duration_ms = get_response_size_and_duration(
        fhir_resource, start, logger
    )
    logger.log(
        DosSearchLogBase.DOS_SEARCH_006,
        dos_response_time=f"{duration_ms}ms",
        dos_response_size=response_size,
        exception_type=type(exc).__name__,
        exception_message=str(exc),
    )

    return create_response(500, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    # Log response creation with structured fields (we don't have event in this scope)
    # response details have been logged in the handler; this is an additional log point
    body = fhir_resource.model_dump_json()
    logger.log(
        DosSearchLogBase.DOS_SEARCH_004,
        status_code=status_code,
        body=body,
        dos_message_category="RESPONSE",
    )
    return Response(
        status_code=status_code,
        headers=DEFAULT_RESPONSE_HEADERS,
        body=body,
    )


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
