from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from starlette.testclient import TestClient

from organisations.app.handler_organisation import (
    STATUS_CODE_MAP,
    app,
    handler,
    operation_outcome_exception_handler,
)


def test_lambda_handler_execution() -> None:
    mock_event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": "GET",
            "requestId": "test-request-id",
            "apiId": "test-api-id",
        },
        "resource": "/",
    }
    mock_context = MagicMock()
    response = handler(mock_event, mock_context)

    assert "statusCode" in response
    assert "headers" in response
    assert "body" in response


@pytest.fixture
def test_app() -> FastAPI:
    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


@pytest.mark.parametrize(
    "error_code,expected_status_code",
    [
        ("not-found", HTTPStatus.NOT_FOUND),
        ("invalid", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("exception", HTTPStatus.INTERNAL_SERVER_ERROR),
        ("forbidden", HTTPStatus.FORBIDDEN),
        ("processing", HTTPStatus.ACCEPTED),
        ("duplicate", HTTPStatus.CONFLICT),
        ("structure", HTTPStatus.BAD_REQUEST),
        ("security", HTTPStatus.UNAUTHORIZED),
        ("not-supported", HTTPStatus.METHOD_NOT_ALLOWED),
        ("business-rule", HTTPStatus.UNPROCESSABLE_ENTITY),
        ("informational", HTTPStatus.OK),
        ("unknown-code", HTTPStatus.INTERNAL_SERVER_ERROR),  # Default status code
    ],
)
async def test_operation_outcome_exception_handler_status_codes(
    error_code: str, expected_status_code: int
) -> None:
    """Test that each error code maps to the correct HTTP status code."""
    exc = OperationOutcomeException(
        {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": error_code,
                    "diagnostics": f"Test error with code {error_code}",
                }
            ],
        }
    )
    request = Request({"type": "http"})
    response = await operation_outcome_exception_handler(request, exc)
    assert response.status_code == expected_status_code


async def test_operation_outcome_exception_handler_response_content() -> None:
    """Test that the response contains the correct OperationOutcome content."""
    test_outcome = {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "not-found",
                "diagnostics": "Test error message",
            }
        ],
    }
    exc = OperationOutcomeException(test_outcome)
    request = Request({"type": "http"})
    response = await operation_outcome_exception_handler(request, exc)
    assert (
        response.body.decode()
        == '{"resourceType":"OperationOutcome","issue":[{"severity":"error","code":"not-found","diagnostics":"Test error message"}]}'
    )


def test_status_code_map_values() -> None:
    """Test that STATUS_CODE_MAP values are valid HTTP status codes."""
    valid_status_codes = set(HTTPStatus)
    for status_code in STATUS_CODE_MAP.values():
        assert status_code in {s.value for s in valid_status_codes}
