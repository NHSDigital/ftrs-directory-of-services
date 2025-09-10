from http import HTTPStatus

import pytest
from ftrs_common.api_middleware.fhir_type_middleware import (
    FHIRAcceptHeaderMiddleware,
    FHIRContentTypeMiddleware,
)
from starlette.requests import Request
from starlette.responses import Response


class DummyCallNext:
    async def __call__(self, request: Request) -> Response:
        return Response("OK", status_code=HTTPStatus.OK)


# Content-Type middleware direct tests
@pytest.mark.asyncio
async def test_content_type_middleware_accepts_valid() -> None:
    middleware = FHIRContentTypeMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "PUT",
        "headers": [(b"content-type", b"application/fhir+json")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.OK
    assert response.body == b"OK"


@pytest.mark.asyncio
async def test_content_type_middleware_rejects_invalid() -> None:
    middleware = FHIRContentTypeMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "PUT",
        "headers": [(b"content-type", b"application/json")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert (
        b"PUT requests must have Content-Type 'application/fhir+json'" in response.body
    )


@pytest.mark.asyncio
async def test_content_type_middleware_rejects_suffix() -> None:
    middleware = FHIRContentTypeMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "PUT",
        "headers": [(b"content-type", b"application/fhir+json+abc")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


@pytest.mark.asyncio
async def test_content_type_middleware_allows_non_put() -> None:
    middleware = FHIRContentTypeMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [(b"content-type", b"application/json")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.OK
    assert response.body == b"OK"


# Accept header middleware direct tests
@pytest.mark.asyncio
async def test_accept_header_middleware_accepts_valid() -> None:
    middleware = FHIRAcceptHeaderMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [(b"accept", b"application/fhir+json")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.OK
    assert response.body == b"OK"


@pytest.mark.asyncio
async def test_accept_header_middleware_rejects_invalid() -> None:
    middleware = FHIRAcceptHeaderMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [(b"accept", b"application/json")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE
    assert b"GET requests must have Accept 'application/fhir+json'" in response.body


@pytest.mark.asyncio
async def test_accept_header_middleware_rejects_missing() -> None:
    middleware = FHIRAcceptHeaderMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "GET",
        "headers": [],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.NOT_ACCEPTABLE
    assert b"GET requests must have Accept 'application/fhir+json'" in response.body


@pytest.mark.asyncio
async def test_accept_header_middleware_allows_non_get() -> None:
    middleware = FHIRAcceptHeaderMiddleware(DummyCallNext())
    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"accept", b"application/json")],
        "path": "/",
    }
    request = Request(scope, receive=lambda: None)
    response = await middleware.dispatch(request, DummyCallNext())
    assert response.status_code == HTTPStatus.OK
    assert response.body == b"OK"
