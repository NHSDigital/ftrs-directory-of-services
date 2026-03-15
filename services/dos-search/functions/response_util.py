from collections.abc import Callable, Iterable
from dataclasses import dataclass

from aws_lambda_powertools import Tracer
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, Response
from fhir.resources.R4B.fhirresourcemodel import FHIRResourceModel
from ftrs_common.api_middleware.fhir_type_middleware import MEDIA_TYPE
from ftrs_common.api_middleware.security_headers_middleware import SECURITY_HEADERS
from ftrs_common.logger import LogBase, Logger

from functions.request_context_middleware import request_context_middleware

type ResponseHeaders = dict[str, str]
type FhirResponseFactory = Callable[[int, FHIRResourceModel], Response]


@dataclass(frozen=True)
class DosSearchLambdaRuntime:
    logger: Logger
    tracer: Tracer
    app: APIGatewayRestResolver
    default_response_headers: ResponseHeaders
    create_response: FhirResponseFactory


DEFAULT_CORS_ALLOW_HEADERS: tuple[str, ...] = (
    "Authorization",
    "Content-Type",
    "NHSD-Correlation-ID",
    "NHSD-Request-ID",
)


def build_fhir_response_headers(
    *,
    allowed_methods: Iterable[str] = ("GET",),
    allowed_headers: Iterable[str] | None = None,
) -> ResponseHeaders:
    return {
        "Content-Type": MEDIA_TYPE,
        "Access-Control-Allow-Methods": ", ".join(sorted(set(allowed_methods))),
        "Access-Control-Allow-Headers": ", ".join(
            sorted(set(allowed_headers or DEFAULT_CORS_ALLOW_HEADERS))
        ),
        **SECURITY_HEADERS,
    }


DEFAULT_FHIR_RESPONSE_HEADERS: ResponseHeaders = build_fhir_response_headers()


def build_dos_search_lambda_runtime(
    *,
    log_reference: LogBase,
    service_name: str = "dos-search",
    allowed_methods: Iterable[str] = ("GET",),
    allowed_headers: Iterable[str] | None = None,
) -> DosSearchLambdaRuntime:
    logger = Logger.get(service=service_name)
    tracer = Tracer()
    app = APIGatewayRestResolver()
    app.use([request_context_middleware])

    default_response_headers = build_fhir_response_headers(
        allowed_methods=allowed_methods,
        allowed_headers=allowed_headers,
    )
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
    headers: ResponseHeaders | None = None,
) -> FhirResponseFactory:
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
    headers: ResponseHeaders | None = None,
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
