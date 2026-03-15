import time
from collections.abc import Callable
from functools import partial

from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.feature_flags import (
    FeatureFlag,
    FeatureFlagGuardConfig,
    FeatureFlagGuardDependencies,
    build_feature_flag_guard_chain,
)

from functions import error_util
from functions.constants import FEATURE_FLAG_LOG_CONTEXT
from functions.event_context import DosSearchLogBase, get_response_size_and_duration
from functions.response_util import build_dos_search_lambda_runtime

runtime = build_dos_search_lambda_runtime(
    log_reference=DosSearchLogBase.DOS_SEARCH_004,
    allowed_methods=("POST",),
)
logger = runtime.logger
tracer = runtime.tracer
app = runtime.app
DEFAULT_RESPONSE_HEADERS = runtime.default_response_headers
create_response = runtime.create_response

type TriageCodeRequestGuard = Callable[[float], Response]

_create_triage_service_unavailable_resource = partial(
    error_util.create_resource_service_unavailable_error,
    service_name="Triage code search endpoint",
    availability_status="currently unavailable",
)

_TRIAGE_CODE_FEATURE_FLAG_CONFIG = FeatureFlagGuardConfig(
    flag_name=FeatureFlag.DOS_SEARCH_TRIAGE_CODE_ENABLED,
    enabled_log_reference=DosSearchLogBase.DOS_SEARCH_017,
    disabled_log_reference=DosSearchLogBase.DOS_SEARCH_016,
    log_context=FEATURE_FLAG_LOG_CONTEXT,
)

_TRIAGE_CODE_FEATURE_FLAG_DEPENDENCIES = FeatureFlagGuardDependencies(
    logger_getter=lambda: logger,
    create_error_resource_getter=lambda: _create_triage_service_unavailable_resource,
    get_response_size_and_duration_getter=lambda: get_response_size_and_duration,
    create_response_getter=lambda: create_response,
)


@app.post("/triage_code")
@tracer.capture_method
def post_triage_code() -> Response:
    start = time.time()

    return _guard_triage_code_request(start)


def _handle_triage_code_request(start: float) -> Response:
    logger.log(
        DosSearchLogBase.DOS_SEARCH_015,
        dos_message_category="REQUEST",
    )
    fhir_resource = _create_triage_service_unavailable_resource()
    response_size, duration_ms = get_response_size_and_duration(
        fhir_resource, start, logger
    )
    logger.log(
        DosSearchLogBase.DOS_SEARCH_018,
        dos_response_time=f"{duration_ms}ms",
        dos_response_size=response_size,
        dos_message_category="METRICS",
    )
    return create_response(503, fhir_resource)


_guard_triage_code_request: TriageCodeRequestGuard = build_feature_flag_guard_chain(
    config=_TRIAGE_CODE_FEATURE_FLAG_CONFIG,
    dependencies=_TRIAGE_CODE_FEATURE_FLAG_DEPENDENCIES,
    handler=_handle_triage_code_request,
).handle


@tracer.capture_lambda_handler
def lambda_handler(
    event: dict[str, object], context: LambdaContext
) -> dict[str, object]:
    return app.resolve(event, context)
