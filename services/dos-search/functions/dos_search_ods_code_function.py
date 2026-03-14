import time

from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError

from functions import error_util
from functions.event_context import get_response_size_and_duration
from functions.ftrs_service.ftrs_service import FtrsService
from functions.logbase import DosSearchLogBase
from functions.organization_headers import OrganizationHeaders
from functions.organization_query_params import OrganizationQueryParams
from functions.response_util import build_dos_search_lambda_runtime

runtime = build_dos_search_lambda_runtime(
    log_reference=DosSearchLogBase.DOS_SEARCH_004,
    allowed_headers=OrganizationHeaders.get_allowed_headers(),
)
logger = runtime.logger
tracer = runtime.tracer
app = runtime.app
DEFAULT_RESPONSE_HEADERS = runtime.default_response_headers
create_response = runtime.create_response


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

    except Exception:
        return handle_general_exception(start)
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


def handle_general_exception(start: float) -> Response:
    fhir_resource = error_util.create_resource_internal_server_error()

    response_size, duration_ms = get_response_size_and_duration(
        fhir_resource, start, logger
    )
    logger.log(
        DosSearchLogBase.DOS_SEARCH_006,
        dos_response_time=f"{duration_ms}ms",
        dos_response_size=response_size,
    )

    return create_response(500, fhir_resource)


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
