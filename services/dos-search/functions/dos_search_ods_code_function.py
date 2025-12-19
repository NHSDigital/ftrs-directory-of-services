from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_service.ftrs_service import FtrsService
from functions.organization_query_params import OrganizationQueryParams


class InvalidRequestHeadersError(ValueError):
    """Raised when disallowed HTTP headers are supplied in the request."""


logger = Logger()
tracer = Tracer()
app = APIGatewayRestResolver()

DEFAULT_RESPONSE_HEADERS: dict[str, str] = {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": (
        "Authorization, Content-Type, NHSD-Correlation-ID, NHSD-Request-ID, "
        "NHSD-Message-Id, NHSD-Api-Version, NHSD-End-User-Role, NHSD-Client-Id, "
        "NHSD-Connecting-Party-App-Name, Accept, Accept-Encoding, Accept-Language, "
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
    try:
        _validate_headers(app.current_event.headers)

        query_params = app.current_event.query_string_parameters or {}
        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        logger.append_keys(ods_code=ods_code)

        ftrs_service = FtrsService()
        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except ValidationError as exception:
        logger.warning(
            "Validation error occurred", extra={"validation_errors": exception.errors()}
        )
        fhir_resource = error_util.create_validation_error_operation_outcome(exception)
        return create_response(400, fhir_resource)
    except InvalidRequestHeadersError as exception:
        invalid_headers: list[str] = exception.args[0] if exception.args else []
        logger.warning(
            "Invalid request headers supplied",
            extra={"invalid_headers": invalid_headers},
        )
        fhir_resource = error_util.create_invalid_header_operation_outcome(
            invalid_headers
        )
        return create_response(400, fhir_resource)
    except Exception:
        logger.exception("Internal server error occurred")
        fhir_resource = error_util.create_resource_internal_server_error()
        return create_response(500, fhir_resource)
    else:
        logger.info("Successfully processed")
        return create_response(200, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    logger.info("Creating response", extra={"status_code": status_code})
    return Response(
        status_code=status_code,
        headers=DEFAULT_RESPONSE_HEADERS,
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
