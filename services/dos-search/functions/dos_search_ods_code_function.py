import os
import time
from typing import Any, Dict, Optional

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_logger import FtrsLogger
from functions.ftrs_service.ftrs_service import FtrsService
from functions.organization_query_params import OrganizationQueryParams

service = "dos-search"

logger = Logger()
ftrs_logger = FtrsLogger(service=service)
tracer = Tracer()
app = APIGatewayRestResolver()


def extract(event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract APIM headers and common event fields into the structured 'extra' dict.

    All mandatory fields are present; missing values use the configured placeholder.
    Optional one-time fields are prefixed with 'Opt_'.
    """
    placeholder = "FTRS_LOG_PLACEHOLDER"

    headers = (
        {} if not event or not isinstance(event, dict) else (event.get("headers") or {})
    )
    hdr_lower = headers
    # ftrs_logger._normalize_headers(headers)

    def h(*names: str) -> Optional[str]:
        # try original casing keys first, then lowercased mapping
        for n in names:
            if n in headers and headers.get(n) not in (None, ""):
                return headers.get(n)
        # fallback to lowercased lookup of provided names
        for n in names:
            val = hdr_lower.get(n.lower())
            if val not in (None, ""):
                return val
        return None

    out: Dict[str, Any] = {}

    # NHSD correlation id
    corr = h("NHSD-Correlation-ID", "X-Request-Id") or placeholder
    out["ftrs_nhsd_correlation_id"] = corr
    out["nhsd_correlation_id"] = corr

    # NHSD request id
    reqid = h("NHSD-Request-ID") or placeholder
    out["ftrs_nhsd_request_id"] = reqid
    out["nhsd_request_id"] = reqid

    # APIM message id
    msgid = (
        h("x-apim-msg-id", "X-Message-Id", "apim-message-id", "ftrs-message-id")
        or placeholder
    )
    out["ftrs_message_id"] = msgid
    out["nhsd_message_id"] = msgid

    # Mandatory/default ftrs fields
    out["ftrs_message_category"] = "LOGGING"
    out["ftrs_environment"] = (
        os.environ.get("ENVIRONMENT") or os.environ.get("WORKSPACE") or service
        if not None
        else placeholder
    )
    out["ftrs_api_version"] = h("x-api-version", "api-version") or placeholder
    out["ftrs_lambda_version"] = (
        os.environ.get("AWS_LAMBDA_FUNCTION_VERSION") or placeholder
    )
    out["ftrs_response_time"] = placeholder
    out["ftrs_response_size"] = placeholder

    # Optional one-time fields prefixed with 'Opt_'
    end_user_role = (
        h("x-end-user-role")
        or (event.get("end_user_role") if isinstance(event, dict) else None)
        or (
            event.get("requestContext", {}).get("authorizer", {}).get("end_user_role")
            if isinstance(event, dict)
            else None
        )
        or placeholder
    )
    out["Opt_ftrs_end_user_role"] = end_user_role

    client_id = (
        h("x-client-id")
        or (event.get("client_id") if isinstance(event, dict) else None)
        or placeholder
    )
    out["Opt_ftrs_client_id"] = client_id

    app_name = (
        h("x-application-name")
        or (event.get("application_name") if isinstance(event, dict) else None)
        or placeholder
    )
    out["Opt_ftrs_application_name"] = app_name

    # Request params (queryStringParameters + pathParameters)
    req_params: Dict[str, Any] = {}
    if isinstance(event, dict):
        qs = event.get("queryStringParameters") or {}
        path_params = event.get("pathParameters") or {}
        if isinstance(qs, dict):
            req_params.update(qs)
        if isinstance(path_params, dict):
            req_params.update(path_params)
    out["Opt_ftrs_request_parms"] = req_params or {}

    return out


@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    start = time.time()
    log_data = extract(app.current_event)
    try:
        query_params = app.current_event.query_string_parameters or {}
        print(
            "easily searchable: ",
            "current event: ",
            app.current_event,
            "log data: ",
            log_data,
        )
        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        # Structured request log
        ftrs_logger.info(
            "Received request for odsCode", log_data=log_data, ods_code=ods_code
        )

        ftrs_service = FtrsService()
        fhir_resource = ftrs_service.endpoints_by_ods(ods_code)

    except ValidationError as exception:
        # Log warning with structured fields
        ftrs_logger.warning(
            "Validation error occurred",
            log_data=log_data,
            validation_errors=exception.errors(),
        )
        fhir_resource = error_util.create_validation_error_operation_outcome(exception)
        return create_response(400, fhir_resource)
    except Exception:
        # Log exception with structured fields
        ftrs_logger.exception("Internal server error occurred", log_data=log_data)
        fhir_resource = error_util.create_resource_internal_server_error()
        return create_response(500, fhir_resource)
    else:
        # success path: measure and log response metrics
        duration_ms = int((time.time() - start) * 1000)
        # attempt to approximate response size (bytes)
        try:
            body = fhir_resource.model_dump_json()
            response_size = len(body.encode("utf-8"))
        except Exception:
            response_size = None

        ftrs_logger.info(
            "Successfully processed",
            log_data=log_data,
            ftrs_response_time=f"{duration_ms}ms",
            ftrs_response_size=response_size,
        )
        return create_response(200, fhir_resource)


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    # Log response creation with structured fields (we don't have event in this scope)
    # response details have been logged in the handler; this is an additional log point
    ftrs_logger.info("Creating response", log_data=None, status_code=status_code)
    return Response(
        status_code=status_code,
        content_type="application/fhir+json",
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
