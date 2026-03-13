import time

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.operationoutcome import OperationOutcome
from ftrs_common.feature_flags import FeatureFlag
from ftrs_common.logger import Logger

from functions.dos_search_feature_flag_factory import build_dos_search_feature_flag_chain
from functions.event_context import DosSearchLogBase, get_response_size_and_duration
from functions.request_context_middleware import request_context_middleware
from functions.response_util import (
    DEFAULT_FHIR_RESPONSE_HEADERS,
    build_create_fhir_response,
)

service = "dos-search"
logger = Logger.get(service=service)
tracer = Tracer()
app = APIGatewayRestResolver()
app.use([request_context_middleware])

DEFAULT_RESPONSE_HEADERS: dict[str, str] = DEFAULT_FHIR_RESPONSE_HEADERS
create_response = build_create_fhir_response(
    logger=logger,
    log_reference=DosSearchLogBase.DOS_SEARCH_004,
    headers=DEFAULT_RESPONSE_HEADERS,
)


@app.post("/triage_code")
@tracer.capture_method
def post_triage_code() -> Response:
    start = time.time()

    return _REQUEST_GUARD_CHAIN.handle(start)


def _handle_triage_code_request(start: float) -> Response:
    logger.log(
        DosSearchLogBase.DOS_SEARCH_015,
        dos_message_category="REQUEST",
    )
    fhir_resource = _create_not_implemented_resource()
    response_size, duration_ms = get_response_size_and_duration(
        fhir_resource, start, logger
    )
    logger.log(
        DosSearchLogBase.DOS_SEARCH_018,
        dos_response_time=f"{duration_ms}ms",
        dos_response_size=response_size,
        dos_message_category="METRICS",
    )
    return create_response(501, fhir_resource)


def _create_not_implemented_resource() -> OperationOutcome:
    return OperationOutcome.model_validate(
        {
            "issue": [
                {
                    "severity": "warning",
                    "code": "not-supported",
                    "diagnostics": (
                        "Triage code search endpoint is not yet implemented"
                    ),
                }
            ]
        }
    )


def _create_service_unavailable_resource() -> OperationOutcome:
    return OperationOutcome.model_validate(
        {
            "issue": [
                {
                    "severity": "fatal",
                    "code": "exception",
                    "diagnostics": (
                        "Service Unavailable: Triage code search endpoint is currently disabled"
                    ),
                }
            ]
        }
    )


_REQUEST_GUARD_CHAIN = build_dos_search_feature_flag_chain(
    flag_name=FeatureFlag.DOS_SEARCH_TRIAGE_CODE_ENABLED,
    logger_getter=lambda: logger,
    enabled_log_reference=DosSearchLogBase.DOS_SEARCH_017,
    disabled_log_reference=DosSearchLogBase.DOS_SEARCH_016,
    create_error_resource_getter=lambda: _create_service_unavailable_resource,
    create_response_getter=lambda: create_response,
    handler=_handle_triage_code_request,
)


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
