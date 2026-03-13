import time

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from ftrs_common.feature_flags import FeatureFlag
from ftrs_common.logger import Logger
from pydantic import ValidationError

from functions import error_util
from functions.dos_search_feature_flag_factory import build_dos_search_feature_flag_chain
from functions.event_context import DosSearchLogBase, get_response_size_and_duration
from functions.ftrs_service.healthcare_services_by_ods import (
    HealthcareServicesByOdsService,
)
from functions.healthcare_service_query_params import HealthcareServiceQueryParams
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


@app.get("/HealthcareService")
@tracer.capture_method
def get_healthcare_service() -> Response:
    start = time.time()

    return _REQUEST_GUARD_CHAIN.handle(start)


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


_REQUEST_GUARD_CHAIN = build_dos_search_feature_flag_chain(
    flag_name=FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED,
    logger_getter=lambda: logger,
    enabled_log_reference=DosSearchLogBase.DOS_SEARCH_014,
    disabled_log_reference=DosSearchLogBase.DOS_SEARCH_013,
    create_error_resource_getter=(
        lambda: error_util.create_resource_service_unavailable_error
    ),
    create_response_getter=lambda: create_response,
    handler=_handle_healthcare_service_request,
)


@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
