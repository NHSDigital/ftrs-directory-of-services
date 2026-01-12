from __future__ import annotations

import os

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from pydantic import ValidationError

from functions import error_util
from functions.ftrs_service.ftrs_service import FtrsService
from functions.lambda_invoker import (
    get_orchestrator_mode,
    get_worker_lambda_names,
    invoke_lambda_pipeline_json,
)
from functions.organization_query_params import OrganizationQueryParams


class InvalidRequestHeadersError(ValueError):
    """Raised when disallowed HTTP headers are supplied in the request."""


class MissingEnvironmentVariableError(RuntimeError):
    """Raised when a required environment variable is missing."""

    def __init__(self, variable_name: str) -> None:
        super().__init__(variable_name)
        self.variable_name = variable_name


logger = Logger()
tracer = Tracer()

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


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name, "").strip()
    if not value:
        raise MissingEnvironmentVariableError(var_name)
    return value


def _require_worker_lambda_names() -> list[str]:
    worker_names = get_worker_lambda_names()
    if not worker_names:
        raise MissingEnvironmentVariableError("DOS_SEARCH_ORG_WORKER_LAMBDA_NAMES")
    return worker_names


def create_response(status_code: int, fhir_resource: FHIRResourceModel) -> Response:
    logger.info("Creating response", extra={"status_code": status_code})
    return Response(
        status_code=status_code,
        headers=DEFAULT_RESPONSE_HEADERS,
        body=fhir_resource.model_dump_json(),
    )


@tracer.capture_method
def handle_get_organization(router: APIGatewayRestResolver) -> Response:
    """Handle GET /Organization.

    This is extracted to support two deployment shapes:
    - inline: execute business logic in the API-facing lambda
    - lambda: delegate to a worker lambda as part of a "set of lambdas" pattern
    """

    try:
        _validate_headers(router.current_event.headers)

        query_params = router.current_event.query_string_parameters or {}
        validated_params = OrganizationQueryParams.model_validate(query_params)

        ods_code = validated_params.ods_code
        logger.append_keys(ods_code=ods_code)

        mode = get_orchestrator_mode()
        if mode == "lambda":
            worker_names = _require_worker_lambda_names()

            lambda_proxy_response = invoke_lambda_pipeline_json(
                function_names=worker_names,
                initial_payload={
                    "path": router.current_event.path,
                    "httpMethod": router.current_event.http_method,
                    "headers": router.current_event.headers,
                    "queryStringParameters": router.current_event.query_string_parameters,
                    "requestContext": router.current_event.request_context,
                    "body": router.current_event.body,
                },
            )

            return Response(
                status_code=int(lambda_proxy_response.get("statusCode", 502)),
                headers=(
                    lambda_proxy_response.get("headers") or DEFAULT_RESPONSE_HEADERS
                ),
                body=str(lambda_proxy_response.get("body", "")),
            )

        # inline mode (default)
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
