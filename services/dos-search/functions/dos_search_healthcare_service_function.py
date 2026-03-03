from http import HTTPStatus
import time

from ftrs_common.feature_flags import FeatureFlag, FeatureFlagsClient
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_service.healthcare_services_by_ods import (
    HealthcareServicesByOdsService,
)
from functions.healthcare_service_query_params import HealthcareServiceQueryParams
from functions.logger.dos_logger import DosLogger

service = "dos-search"
dos_logger = DosLogger.get(service=service)
logger = dos_logger.logger
tracer = Tracer()
app = APIGatewayRestResolver()
FEATURE_FLAGS_CLIENT: FeatureFlagsClient = FeatureFlagsClient()

DEFAULT_RESPONSE_HEADERS: dict[str, str] = {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": (
        "Authorization, Content-Type, NHSD-Correlation-ID, NHSD-Request-ID"
    ),
}


@app.get("/HealthcareService")
@tracer.capture_method
def get_healthcare_service() -> Response:
    if FEATURE_FLAGS_CLIENT.is_enabled(
        FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED
    ):
        dos_logger.info(
            "Healthcare Service search endpoint is enabled via feature flag",
            feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
            feature_flag_status="enabled",
            dos_message_category="FEATURE_FLAG",
        )
    else:
        dos_logger.warning(
            "Healthcare Service search endpoint is disabled via feature flag",
            feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
            feature_flag_status="disabled",
            dos_message_category="FEATURE_FLAG",
        )
        return {
            "statusCode": HTTPStatus.SERVICE_UNAVAILABLE,
            "body": "Service Unavailable: Healthcare Service search endpoint is currently disabled",
        }
    start = time.time()
    dos_logger.init(app.current_event)

    try:
        query_params = app.current_event.query_string_parameters or {}
        validated_params = HealthcareServiceQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        dos_logger.info(
            "Received request for healthcare service",
            ods_code=ods_code,
            dos_message_category="REQUEST",
        )

        ftrs_service = HealthcareServicesByOdsService()
        fhir_resource = ftrs_service.healthcare_services_by_ods(ods_code)

    except ValidationError as exception:
        fhir_resource = error_util.create_validation_error_operation_outcome(exception)
        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            fhir_resource, start
        )
        dos_logger.warning(
            "Validation error occurred",
            validation_errors=exception.errors(),
            dos_response_time=f"{duration_ms}ms",
            dos_response_size=response_size,
        )
        return create_response(400, fhir_resource)

    except Exception:
        fhir_resource = error_util.create_resource_internal_server_error()
        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            fhir_resource, start
        )
        dos_logger.exception(
            "Internal server error occurred",
            dos_response_time=f"{duration_ms}ms",
            dos_response_size=response_size,
        )
        return create_response(500, fhir_resource)

    else:
        response_size, duration_ms = dos_logger.get_response_size_and_duration(
            fhir_resource, start
        )
        dos_logger.info(
            "Successfully processed healthcare service request",
            dos_response_time=f"{duration_ms}ms",
            dos_response_size=response_size,
            dos_message_category="METRICS",
        )
        return create_response(200, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    body = fhir_resource.model_dump_json()
    dos_logger.info(
        "Creating response",
        status_code=status_code,
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
