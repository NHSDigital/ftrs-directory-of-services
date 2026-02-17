import asyncio
from http import HTTPStatus

from dos_ingest.app import app, operation_outcome_exception_handler
from fastapi import Request
from ftrs_common.api_middleware.fhir_type_middleware import (
    FHIRAcceptHeaderMiddleware,
    FHIRContentTypeMiddleware,
)
from ftrs_common.api_middleware.response_logging_middleware import (
    ResponseLoggingMiddleware,
)
from ftrs_common.fhir.operation_outcome import OperationOutcomeException


def test_operation_outcome_exception_handler_maps_status_code() -> None:
    exc = OperationOutcomeException(
        {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "not-found",
                    "diagnostics": "missing",
                }
            ],
        }
    )

    response = asyncio.run(
        operation_outcome_exception_handler(Request({"type": "http"}), exc)
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_app_registers_expected_middleware() -> None:
    middleware_classes = [middleware.cls for middleware in app.user_middleware]

    assert FHIRContentTypeMiddleware in middleware_classes
    assert FHIRAcceptHeaderMiddleware in middleware_classes
    assert ResponseLoggingMiddleware in middleware_classes
