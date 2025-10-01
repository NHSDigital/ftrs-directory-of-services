from http import HTTPStatus

import pytest
from ftrs_common.api_middleware.correlation_id_middleware import CorrelationIdMiddleware
from ftrs_common.utils.correlation_id import CORRELATION_ID_HEADER, get_correlation_id
from starlette.requests import Request
from starlette.responses import Response


class DummyCallNext:
    """Simple class to mock the call_next parameter in middleware."""

    async def __call__(self, request: Request) -> Response:
        return Response("OK", status_code=200)


@pytest.mark.asyncio
async def test_middleware_extracts_correlation_id_from_headers() -> None:
    """Test that middleware extracts correlation ID from request headers."""
    middleware = CorrelationIdMiddleware(DummyCallNext())
    test_correlation_id = "test-correlation-id"
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [
            (CORRELATION_ID_HEADER.lower().encode(), test_correlation_id.encode())
        ],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert response.headers[CORRELATION_ID_HEADER] == test_correlation_id
    assert get_correlation_id() == test_correlation_id


@pytest.mark.asyncio
async def test_middleware_generates_correlation_id_when_missing() -> None:
    """Test that middleware generates a correlation ID when not present in headers."""
    middleware = CorrelationIdMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert CORRELATION_ID_HEADER in response.headers
    assert response.headers[CORRELATION_ID_HEADER] is not None


@pytest.mark.asyncio
async def test_middleware_uses_same_id_throughout_request() -> None:
    """Test that the same correlation ID is used throughout request processing."""
    generated_correlation_id = None

    class CustomCallNext:
        async def __call__(self, request: Request) -> Response:
            nonlocal generated_correlation_id
            generated_correlation_id = get_correlation_id()
            return Response("OK", status_code=200)

    middleware = CorrelationIdMiddleware(CustomCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, CustomCallNext())

    assert generated_correlation_id is not None
    assert response.headers[CORRELATION_ID_HEADER] == generated_correlation_id


@pytest.mark.asyncio
async def test_middleware_preserves_correlation_id_from_headers() -> None:
    """Test that middleware preserves and uses the correlation ID from headers."""
    received_correlation_id = None
    test_correlation_id = "test-correlation-id-from-header"

    class CustomCallNext:
        async def __call__(self, request: Request) -> Response:
            nonlocal received_correlation_id
            received_correlation_id = get_correlation_id()
            return Response("OK", status_code=200)

    middleware = CorrelationIdMiddleware(CustomCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [
            (CORRELATION_ID_HEADER.lower().encode(), test_correlation_id.encode())
        ],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, CustomCallNext())

    assert received_correlation_id == test_correlation_id
    assert response.headers[CORRELATION_ID_HEADER] == test_correlation_id


@pytest.mark.asyncio
async def test_middleware_adds_correlation_id_to_response_headers() -> None:
    """Test that middleware adds the correlation ID to response headers."""

    class CustomCallNext:
        async def __call__(self, request: Request) -> Response:
            return Response("OK", status_code=200)

    middleware = CorrelationIdMiddleware(CustomCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, CustomCallNext())

    assert CORRELATION_ID_HEADER in response.headers
    assert response.headers[CORRELATION_ID_HEADER] is not None


@pytest.mark.asyncio
async def test_middleware_with_error_response() -> None:
    """Test that middleware adds correlation ID even when the next middleware returns an error."""

    class ErrorCallNext:
        async def __call__(self, request: Request) -> Response:
            return Response("Error", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    middleware = CorrelationIdMiddleware(ErrorCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, ErrorCallNext())

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert CORRELATION_ID_HEADER in response.headers
    assert response.headers[CORRELATION_ID_HEADER] is not None


@pytest.mark.asyncio
async def test_middleware_with_custom_response_headers() -> None:
    """Test that middleware works with responses that already have custom headers."""

    class CustomHeaderCallNext:
        async def __call__(self, request: Request) -> Response:
            response = Response("OK", status_code=200)
            response.headers["Custom-Header"] = "custom-value"
            return response

    middleware = CorrelationIdMiddleware(CustomHeaderCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, CustomHeaderCallNext())

    assert "Custom-Header" in response.headers
    assert response.headers["Custom-Header"] == "custom-value"
    assert CORRELATION_ID_HEADER in response.headers


@pytest.mark.asyncio
async def test_middleware_chain_with_correlation_id() -> None:
    """Test that correlation ID is preserved through multiple middleware in a chain."""

    class FirstMiddleware:
        async def __call__(self, request: Request) -> Response:
            correlation_id = get_correlation_id()
            response = Response("OK", status_code=200)
            response.headers["Middleware-1-Correlation-ID"] = correlation_id or "none"
            return response

    middleware = CorrelationIdMiddleware(FirstMiddleware())
    test_correlation_id = "test-chain-correlation-id"
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [
            (CORRELATION_ID_HEADER.lower().encode(), test_correlation_id.encode())
        ],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, FirstMiddleware())

    assert response.headers["Middleware-1-Correlation-ID"] == test_correlation_id
    assert response.headers[CORRELATION_ID_HEADER] == test_correlation_id
