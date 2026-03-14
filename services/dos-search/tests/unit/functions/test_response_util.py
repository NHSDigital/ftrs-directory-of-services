from unittest.mock import MagicMock, patch

from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.logbase import DosSearchLogBase
from functions.response_util import (
    DEFAULT_CORS_ALLOW_HEADERS,
    DEFAULT_FHIR_RESPONSE_HEADERS,
    DosSearchLambdaRuntime,
    build_create_fhir_response,
    build_dos_search_lambda_runtime,
    build_fhir_response_headers,
    create_fhir_response,
)

type ResponseHeaders = dict[str, str]
type RuntimeBuildResult = tuple[
    DosSearchLambdaRuntime,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
]


def _build_runtime_with_mocks() -> RuntimeBuildResult:
    logger = MagicMock()
    tracer = MagicMock()
    app = MagicMock()
    create_response = MagicMock()

    with (
        patch("functions.response_util.Logger.get", return_value=logger),
        patch("functions.response_util.Tracer", return_value=tracer),
        patch("functions.response_util.APIGatewayRestResolver", return_value=app),
        patch(
            "functions.response_util.build_create_fhir_response",
            return_value=create_response,
        ),
    ):
        runtime = build_dos_search_lambda_runtime(
            log_reference=DosSearchLogBase.DOS_SEARCH_004
        )

    return runtime, logger, tracer, app, create_response


def test_build_fhir_response_headers_includes_default_cors_and_security_headers() -> (
    None
):
    assert build_fhir_response_headers() == {
        "Content-Type": "application/fhir+json",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": ", ".join(DEFAULT_CORS_ALLOW_HEADERS),
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Cache-Control": "no-store",
    }


def test_build_fhir_response_headers_supports_custom_methods_and_headers() -> None:
    assert build_fhir_response_headers(
        allowed_methods=("POST", "GET", "POST"),
        allowed_headers=("x-request-id", "authorization", "x-request-id"),
    ) == {
        "Content-Type": "application/fhir+json",
        "Access-Control-Allow-Methods": "GET, POST",
        "Access-Control-Allow-Headers": "authorization, x-request-id",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Cache-Control": "no-store",
    }


def test_build_create_fhir_response_builds_reusable_response_callable() -> None:
    logger = MagicMock()
    fhir_resource = OperationOutcome.model_construct(id="response-id")
    create_response = build_create_fhir_response(
        logger=logger,
        log_reference=DosSearchLogBase.DOS_SEARCH_004,
    )

    response = create_response(201, fhir_resource)

    logger.log.assert_called_once_with(
        DosSearchLogBase.DOS_SEARCH_004,
        status_code=201,
        dos_message_category="RESPONSE",
    )
    assert response.status_code == 201
    assert response.headers == DEFAULT_FHIR_RESPONSE_HEADERS
    assert response.body == fhir_resource.model_dump_json()


def test_create_fhir_response_builds_fhir_response_and_logs() -> None:
    logger = MagicMock()
    fhir_resource = OperationOutcome.model_construct(id="response-id")

    response = create_fhir_response(
        logger=logger,
        log_reference=DosSearchLogBase.DOS_SEARCH_004,
        status_code=202,
        fhir_resource=fhir_resource,
    )

    logger.log.assert_called_once_with(
        DosSearchLogBase.DOS_SEARCH_004,
        status_code=202,
        dos_message_category="RESPONSE",
    )
    assert response.status_code == 202
    assert response.headers == DEFAULT_FHIR_RESPONSE_HEADERS
    assert response.body == fhir_resource.model_dump_json()


def test_create_fhir_response_uses_custom_headers_when_provided() -> None:
    logger = MagicMock()
    fhir_resource = OperationOutcome.model_construct(id="response-id")
    headers: ResponseHeaders = {
        "Content-Type": "application/fhir+json",
        "X-Test": "1",
    }

    response = create_fhir_response(
        logger=logger,
        log_reference=DosSearchLogBase.DOS_SEARCH_004,
        status_code=200,
        fhir_resource=fhir_resource,
        headers=headers,
    )

    assert response.headers == headers


def test_build_create_fhir_response_copies_custom_headers() -> None:
    logger = MagicMock()
    fhir_resource = OperationOutcome.model_construct(id="response-id")
    headers: ResponseHeaders = {
        "Content-Type": "application/fhir+json",
        "X-Test": "1",
    }
    create_response = build_create_fhir_response(
        logger=logger,
        log_reference=DosSearchLogBase.DOS_SEARCH_004,
        headers=headers,
    )
    headers["X-Test"] = "2"

    response = create_response(200, fhir_resource)

    assert response.headers == {
        "Content-Type": "application/fhir+json",
        "X-Test": "1",
    }


def test_build_dos_search_lambda_runtime_builds_common_runtime() -> None:
    runtime, logger, tracer, app, create_response = _build_runtime_with_mocks()

    assert runtime.logger is logger
    assert runtime.tracer is tracer
    assert runtime.app is app
    assert runtime.default_response_headers == DEFAULT_FHIR_RESPONSE_HEADERS
    assert runtime.default_response_headers is not DEFAULT_FHIR_RESPONSE_HEADERS
    assert runtime.create_response is create_response
    app.use.assert_called_once()
    middleware = app.use.call_args.args[0]
    assert len(middleware) == 1
    assert middleware[0].__name__ == "request_context_middleware"


def test_build_dos_search_lambda_runtime_returns_runtime_dataclass() -> None:
    runtime, logger, tracer, app, create_response = _build_runtime_with_mocks()

    assert runtime == DosSearchLambdaRuntime(
        logger=logger,
        tracer=tracer,
        app=app,
        default_response_headers=DEFAULT_FHIR_RESPONSE_HEADERS,
        create_response=create_response,
    )


def test_build_dos_search_lambda_runtime_supports_custom_cors_headers() -> None:
    runtime = build_dos_search_lambda_runtime(
        log_reference=DosSearchLogBase.DOS_SEARCH_004,
        allowed_methods=("POST",),
        allowed_headers=("x-request-id", "authorization"),
    )

    assert runtime.default_response_headers["Access-Control-Allow-Methods"] == "POST"
    assert (
        runtime.default_response_headers["Access-Control-Allow-Headers"]
        == "authorization, x-request-id"
    )
