from http import HTTPStatus

import pytest
from ftrs_common.api_middleware.security_headers_middleware import (
    SECURITY_HEADERS,
    SecurityHeadersMiddleware,
)
from starlette.requests import Request
from starlette.responses import Response


class DummyCallNext:
    """Simple class to mock the call_next parameter in middleware."""

    async def __call__(self, request: Request) -> Response:
        return Response("OK", status_code=200)


@pytest.mark.asyncio
async def test_middleware_adds_strict_transport_security_header() -> None:
    """Test that middleware adds Strict-Transport-Security header."""
    middleware = SecurityHeadersMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert response.status_code == 200
    assert "strict-transport-security" in response.headers
    assert (
        response.headers["strict-transport-security"]
        == "max-age=31536000; includeSubDomains"
    )


@pytest.mark.asyncio
async def test_middleware_adds_x_content_type_options_header() -> None:
    """Test that middleware adds X-Content-Type-Options header."""
    middleware = SecurityHeadersMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert response.status_code == 200
    assert "x-content-type-options" in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"


@pytest.mark.asyncio
async def test_middleware_adds_x_frame_options_header() -> None:
    """Test that middleware adds X-Frame-Options header."""
    middleware = SecurityHeadersMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert response.status_code == 200
    assert "x-frame-options" in response.headers
    assert response.headers["x-frame-options"] == "DENY"


@pytest.mark.asyncio
async def test_middleware_adds_cache_control_header() -> None:
    """Test that middleware adds Cache-Control header."""
    middleware = SecurityHeadersMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert response.status_code == 200
    assert "cache-control" in response.headers
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.asyncio
async def test_middleware_adds_all_security_headers() -> None:
    """Test that middleware adds all expected security headers."""
    middleware = SecurityHeadersMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, DummyCallNext())

    assert response.status_code == 200
    for header_name, header_value in SECURITY_HEADERS.items():
        assert response.headers[header_name.lower()] == header_value


@pytest.mark.asyncio
async def test_middleware_with_error_response() -> None:
    """Test that middleware adds security headers even when the next middleware returns an error."""

    class ErrorCallNext:
        async def __call__(self, request: Request) -> Response:
            return Response("Error", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    middleware = SecurityHeadersMiddleware(ErrorCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, ErrorCallNext())

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    for header_name in SECURITY_HEADERS:
        assert header_name.lower() in response.headers


@pytest.mark.asyncio
async def test_middleware_with_custom_response_headers() -> None:
    """Test that middleware works with responses that already have custom headers."""

    class CustomHeaderCallNext:
        async def __call__(self, request: Request) -> Response:
            response = Response("OK", status_code=200)
            response.headers["Custom-Header"] = "custom-value"
            return response

    middleware = SecurityHeadersMiddleware(CustomHeaderCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)

    response = await middleware.dispatch(request, CustomHeaderCallNext())

    assert "custom-header" in response.headers
    assert response.headers["custom-header"] == "custom-value"
    assert "strict-transport-security" in response.headers
