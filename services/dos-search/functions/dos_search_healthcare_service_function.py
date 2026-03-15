import time
from collections.abc import Callable

from aws_lambda_powertools.event_handler import Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.feature_flags import (
    FeatureFlag,
    FeatureFlagGuardConfig,
    FeatureFlagGuardDependencies,
    build_feature_flag_guard_chain,
)
from pydantic import ValidationError

from functions import error_util
from functions.constants import FEATURE_FLAG_LOG_CONTEXT
from functions.event_context import DosSearchLogBase, get_response_size_and_duration
from functions.ftrs_service.healthcare_services_by_ods import (
    HealthcareServicesByOdsService,
)
from functions.healthcare_service_query_params import HealthcareServiceQueryParams
from functions.response_util import build_dos_search_lambda_runtime

runtime = build_dos_search_lambda_runtime(log_reference=DosSearchLogBase.DOS_SEARCH_004)
logger = runtime.logger
tracer = runtime.tracer
app = runtime.app
DEFAULT_RESPONSE_HEADERS = runtime.default_response_headers
create_response = runtime.create_response

type HealthcareServiceRequestGuard = Callable[[float], Response]

_HEALTHCARE_SERVICE_FEATURE_FLAG_CONFIG = FeatureFlagGuardConfig(
    flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
    enabled_log_reference=DosSearchLogBase.DOS_SEARCH_014,
    disabled_log_reference=DosSearchLogBase.DOS_SEARCH_013,
    log_context=FEATURE_FLAG_LOG_CONTEXT,
)

_HEALTHCARE_SERVICE_FEATURE_FLAG_DEPENDENCIES = FeatureFlagGuardDependencies(
    logger_getter=lambda: logger,
    create_error_resource_getter=(
        lambda: lambda: error_util.create_resource_service_unavailable_error(
            service_name="Healthcare Service search endpoint",
            availability_status="currently disabled",
        )
    ),
    get_response_size_and_duration_getter=lambda: get_response_size_and_duration,
    create_response_getter=lambda: create_response,
)


@app.get("/HealthcareService")
@tracer.capture_method
def get_healthcare_service() -> Response:
    start = time.time()

    return _guard_healthcare_service_request(start)


def _handle_healthcare_service_request(start: float) -> Response:
    try:
        query_params = app.current_event.query_string_parameters or {}
        validated_params = HealthcareServiceQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        logger.log(
            DosSearchLogBase.DOS_SEARCH_012,
            ods_code=ods_code,
            dos_message_category="REQUEST",
        )

        ftrs_service = HealthcareServicesByOdsService()
        fhir_resource = ftrs_service.healthcare_services_by_ods(ods_code)

    except ValidationError as exception:
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

    except Exception:
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

    else:
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


_guard_healthcare_service_request: HealthcareServiceRequestGuard = (
    build_feature_flag_guard_chain(
        config=_HEALTHCARE_SERVICE_FEATURE_FLAG_CONFIG,
        dependencies=_HEALTHCARE_SERVICE_FEATURE_FLAG_DEPENDENCIES,
        handler=_handle_healthcare_service_request,
    ).handle
)


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
