import pytest
from ftrs_common.api_middleware.response_logging_middleware import (
    ResponseLoggingMiddleware,
)
from ftrs_common.fhir.operation_outcome_status_mapper import STATUS_CODE_MAP
from starlette.requests import Request
from starlette.responses import StreamingResponse


@pytest.mark.asyncio
async def test_logs_error_response(caplog: pytest.LogCaptureFixture) -> None:
    middleware = ResponseLoggingMiddleware(None)
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    async def call_next(_: Request) -> StreamingResponse:
        return StreamingResponse(
            [b'{"error":"fail"}'], status_code=STATUS_CODE_MAP["invalid"]
        )

    with caplog.at_level("ERROR"):
        result: StreamingResponse = await middleware.dispatch(request, call_next)
        assert result.status_code == STATUS_CODE_MAP["invalid"]
        assert any(
            'Error response returned with status code: 422. Error message: {"error":"fail"}.'
            in r.getMessage()
            for r in caplog.records
        )
        assert any('{"error":"fail"}' in r.getMessage() for r in caplog.records)


@pytest.mark.asyncio
async def test_logs_success_response(caplog: pytest.LogCaptureFixture) -> None:
    middleware = ResponseLoggingMiddleware(None)
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    async def call_next(_: Request) -> StreamingResponse:
        return StreamingResponse([b"OK"], status_code=STATUS_CODE_MAP["informational"])

    with caplog.at_level("INFO"):
        result: StreamingResponse = await middleware.dispatch(request, call_next)
        assert result.status_code == STATUS_CODE_MAP["informational"]
        assert any(
            "Response returned with status code: 200." in r.getMessage()
            for r in caplog.records
        )
        assert any("200" in r.getMessage() for r in caplog.records)


@pytest.mark.asyncio
async def test_none_response(caplog: pytest.LogCaptureFixture) -> None:
    middleware = ResponseLoggingMiddleware(None)
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    async def call_next(_: Request) -> None:
        return None

    with caplog.at_level("INFO"):
        result = await middleware.dispatch(request, call_next)
        assert result is None
        # No logs should be emitted
        assert not caplog.records


@pytest.mark.asyncio
async def test_empty_body_iterator(caplog: pytest.LogCaptureFixture) -> None:
    middleware = ResponseLoggingMiddleware(None)
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    async def call_next(_: Request) -> StreamingResponse:
        return StreamingResponse([], status_code=STATUS_CODE_MAP["invalid"])

    with caplog.at_level("ERROR"):
        result = await middleware.dispatch(request, call_next)
        assert result.status_code == STATUS_CODE_MAP["invalid"]
        assert any(
            "Error response returned with status code: 422. Error message: ."
            in r.getMessage()
            for r in caplog.records
        )
        assert any(r.levelname == "ERROR" for r in caplog.records)
