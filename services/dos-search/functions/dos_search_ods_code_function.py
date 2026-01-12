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


class InvalidRequestHeadersError(ValueError):
    """Raised when disallowed HTTP headers are supplied in the request."""


service = "dos-search"
dos_logger = DosLogger.get(service=service)
logger = dos_logger.logger
tracer = Tracer()
app = APIGatewayRestResolver()

DEFAULT_RESPONSE_HEADERS: dict[str, str] = {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": (
        "Authorization, Content-Type, NHSD-Correlation-ID, NHSD-Request-ID, X-Correlation-ID, X-Request-ID, "
        "NHSD-Message-Id, version, end-user-role, application-id, application-name"
        "connecting-party-app-name, Accept, Accept-Encoding, Accept-Language, "
        "User-Agent, Host, X-Amzn-Trace-Id, X-Forwarded-For, X-Forwarded-Port, "
        "X-Forwarded-Proto"
    ),
}

ALLOWED_REQUEST_HEADERS: frozenset[str] = frozenset(
    header.strip().lower()
    for header in DEFAULT_RESPONSE_HEADERS["Access-Control-Allow-Headers"].split(",")
    if header.strip()
)


def _validate_headers(headers: dict[str, str] | None) -> None:
    if not headers:
        return

    invalid_headers = [
        header_name
        for header_name in headers
        if header_name and header_name.lower() not in ALLOWED_REQUEST_HEADERS
    ]
    if invalid_headers:
        raise InvalidRequestHeadersError(invalid_headers)


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    start = time.time()
    dos_logger.init(app.current_event)
    try:
        _validate_headers(app.current_event.headers)
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
        fhir_resource = error_util.create_validation_error_operation_outcome(exception)

        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            fhir_resource, start
        )
        dos_logger.warning(
            "Validation error occurred: Logging response time & size",
            validation_errors=exception.errors(),
            opt_ftrs_response_time=f"{duration_ms}ms",
            opt_ftrs_response_size=response_size,
        )
        return create_response(400, fhir_resource)
    except InvalidRequestHeadersError as exception:
        invalid_headers: list[str] = exception.args[0] if exception.args else []
        dos_logger.warning(
            "Invalid request headers supplied",
            invalid_headers=invalid_headers,
        )
        fhir_resource = error_util.create_invalid_header_operation_outcome(
            invalid_headers
        )
        return create_response(400, fhir_resource)
    except Exception:
        # Log exception with structured fields
        fhir_resource = error_util.create_resource_internal_server_error()

        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            fhir_resource, start
        )
        dos_logger.exception(
            "Internal server error occurred: Logging response time & size",
            opt_ftrs_response_time=f"{duration_ms}ms",
            opt_ftrs_response_size=response_size,
        )

        return create_response(500, fhir_resource)
    else:
        # success path: measure and log response metrics
        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            fhir_resource, start
        )

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
        headers=DEFAULT_RESPONSE_HEADERS,
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
