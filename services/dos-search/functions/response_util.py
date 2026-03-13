from collections.abc import Callable
from dataclasses import dataclass

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.logger import LogBase, Logger

from functions.request_context_middleware import request_context_middleware


@dataclass(frozen=True)
class DosSearchLambdaRuntime:
    logger: Logger
    tracer: Tracer
    app: APIGatewayRestResolver
    default_response_headers: dict[str, str]
    create_response: Callable[[int, FHIRResourceModel], Response]


DEFAULT_FHIR_RESPONSE_HEADERS: dict[str, str] = {
    "Content-Type": "application/fhir+json",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": (
        "Authorization, Content-Type, NHSD-Correlation-ID, NHSD-Request-ID"
    ),
}


def build_dos_search_lambda_runtime(
    *,
    log_reference: LogBase,
    service_name: str = "dos-search",
) -> DosSearchLambdaRuntime:
    logger = Logger.get(service=service_name)
    tracer = Tracer()
    app = APIGatewayRestResolver()
    app.use([request_context_middleware])

    default_response_headers = dict(DEFAULT_FHIR_RESPONSE_HEADERS)
    create_response = build_create_fhir_response(
        logger=logger,
        log_reference=log_reference,
        headers=default_response_headers,
    )

    return DosSearchLambdaRuntime(
        logger=logger,
        tracer=tracer,
        app=app,
        default_response_headers=default_response_headers,
        create_response=create_response,
    )


def build_create_fhir_response(
    *,
    logger: Logger,
    log_reference: LogBase,
    headers: dict[str, str] | None = None,
) -> Callable[[int, FHIRResourceModel], Response]:
    resolved_headers = dict(headers or DEFAULT_FHIR_RESPONSE_HEADERS)

    def _create_response(
        status_code: int, fhir_resource: FHIRResourceModel
    ) -> Response:
        return create_fhir_response(
            logger=logger,
            log_reference=log_reference,
            status_code=status_code,
            fhir_resource=fhir_resource,
            headers=resolved_headers,
        )

    return _create_response


def create_fhir_response(
    *,
    logger: Logger,
    log_reference: LogBase,
    status_code: int,
    fhir_resource: FHIRResourceModel,
    headers: dict[str, str] | None = None,
) -> Response:
    body = fhir_resource.model_dump_json()
    logger.log(
        log_reference,
        status_code=status_code,
        dos_message_category="RESPONSE",
    )
    return Response(
        status_code=status_code,
        headers=dict(headers or DEFAULT_FHIR_RESPONSE_HEADERS),
        body=body,
    )
