# import asyncio
# from http import HTTPStatus

# import pytest
# from ftrs_common.api_middleware.request_id_middleware import RequestIdMiddleware
# from ftrs_common.utils.request_id import REQUEST_ID_HEADER, get_request_id
# from starlette.requests import Request
# from starlette.responses import Response


# class DummyCallNext:
#     """Simple class to mock the call_next parameter in middleware."""

#     async def __call__(self, request: Request) -> Response:
#         return Response("OK", status_code=200)


# @pytest.mark.asyncio
# async def test_middleware_extracts_request_id_from_headers() -> None:
#     """Test that middleware extracts request ID from request headers."""
#     middleware = RequestIdMiddleware(DummyCallNext())
#     test_request_id = "test-request-id"
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [(REQUEST_ID_HEADER.lower().encode(), test_request_id.encode())],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, DummyCallNext())

#     assert response.headers[REQUEST_ID_HEADER] == test_request_id
#     assert get_request_id() == test_request_id


# @pytest.mark.asyncio
# async def test_middleware_generates_request_id_when_missing() -> None:
#     """Test that middleware generates a request ID when not present in headers."""
#     middleware = RequestIdMiddleware(DummyCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, DummyCallNext())

#     assert REQUEST_ID_HEADER in response.headers
#     assert response.headers[REQUEST_ID_HEADER] is not None


# @pytest.mark.asyncio
# async def test_middleware_uses_same_id_throughout_request() -> None:
#     """Test that the same request ID is used throughout request processing."""
#     generated_request_id = None

#     class CustomCallNext:
#         async def __call__(self, request: Request) -> Response:
#             nonlocal generated_request_id
#             generated_request_id = get_request_id()
#             return Response("OK", status_code=200)

#     middleware = RequestIdMiddleware(CustomCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, CustomCallNext())

#     assert generated_request_id is not None
#     assert response.headers[REQUEST_ID_HEADER] == generated_request_id


# @pytest.mark.asyncio
# async def test_middleware_preserves_request_id_from_headers() -> None:
#     """Test that middleware preserves and uses the request ID from headers."""
#     received_request_id = None
#     test_request_id = "test-request-id-from-header"

#     class CustomCallNext:
#         async def __call__(self, request: Request) -> Response:
#             nonlocal received_request_id
#             received_request_id = get_request_id()
#             return Response("OK", status_code=200)

#     middleware = RequestIdMiddleware(CustomCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [(REQUEST_ID_HEADER.lower().encode(), test_request_id.encode())],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, CustomCallNext())

#     assert received_request_id == test_request_id
#     assert response.headers[REQUEST_ID_HEADER] == test_request_id


# @pytest.mark.asyncio
# async def test_middleware_adds_request_id_to_response_headers() -> None:
#     """Test that middleware adds the request ID to response headers."""

#     class CustomCallNext:
#         async def __call__(self, request: Request) -> Response:
#             return Response("OK", status_code=200)

#     middleware = RequestIdMiddleware(CustomCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, CustomCallNext())

#     assert REQUEST_ID_HEADER in response.headers
#     assert response.headers[REQUEST_ID_HEADER] is not None


# @pytest.mark.asyncio
# async def test_middleware_with_error_response() -> None:
#     """Test that middleware adds request ID even when the next middleware returns an error."""

#     class ErrorCallNext:
#         async def __call__(self, request: Request) -> Response:
#             return Response("Error", status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

#     middleware = RequestIdMiddleware(ErrorCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, ErrorCallNext())

#     assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
#     assert REQUEST_ID_HEADER in response.headers
#     assert response.headers[REQUEST_ID_HEADER] is not None


# @pytest.mark.asyncio
# async def test_middleware_with_custom_response_headers() -> None:
#     """Test that middleware works with responses that already have custom headers."""

#     class CustomHeaderCallNext:
#         async def __call__(self, request: Request) -> Response:
#             response = Response("OK", status_code=200)
#             response.headers["Custom-Header"] = "custom-value"
#             return response

#     middleware = RequestIdMiddleware(CustomHeaderCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, CustomHeaderCallNext())

#     assert "Custom-Header" in response.headers
#     assert response.headers["Custom-Header"] == "custom-value"
#     assert REQUEST_ID_HEADER in response.headers


# @pytest.mark.asyncio
# async def test_middleware_chain_with_request_id() -> None:
#     """Test that request ID is preserved through multiple middleware in a chain."""

#     class FirstMiddleware:
#         async def __call__(self, request: Request) -> Response:
#             request_id = get_request_id()
#             response = Response("OK", status_code=200)
#             response.headers["Middleware-1-Request-ID"] = request_id or "none"
#             return response

#     middleware = RequestIdMiddleware(FirstMiddleware())
#     test_request_id = "test-chain-request-id"
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [(REQUEST_ID_HEADER.lower().encode(), test_request_id.encode())],
#         "path": "/",
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, FirstMiddleware())

#     assert response.headers["Middleware-1-Request-ID"] == test_request_id
#     assert response.headers[REQUEST_ID_HEADER] == test_request_id


# @pytest.mark.asyncio
# async def test_middleware_extracts_request_id_from_aws_event() -> None:
#     """Test that middleware can extract request ID from AWS Lambda event context."""
#     aws_request_id = "aws-lambda-request-id"

#     class CustomCallNext:
#         async def __call__(self, request: Request) -> Response:
#             return Response("OK", status_code=200)

#     middleware = RequestIdMiddleware(CustomCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#         "aws.event": {"requestContext": {"requestId": aws_request_id}},
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, CustomCallNext())

#     assert response.headers[REQUEST_ID_HEADER] == aws_request_id
#     assert get_request_id() == aws_request_id


# @pytest.mark.asyncio
# async def test_middleware_prioritizes_header_over_aws_event() -> None:
#     """Test that middleware prioritizes X-Request-ID header over AWS event request ID."""
#     header_request_id = "header-request-id"
#     aws_request_id = "aws-request-id"

#     class CustomCallNext:
#         async def __call__(self, request: Request) -> Response:
#             return Response("OK", status_code=200)

#     middleware = RequestIdMiddleware(CustomCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [(REQUEST_ID_HEADER.lower().encode(), header_request_id.encode())],
#         "path": "/",
#         "aws.event": {"requestContext": {"requestId": aws_request_id}},
#     }
#     request = Request(scope, receive=lambda: None)

#     response = await middleware.dispatch(request, CustomCallNext())

#     assert response.headers[REQUEST_ID_HEADER] == header_request_id
#     assert get_request_id() == header_request_id


# @pytest.mark.asyncio
# async def test_middleware_generates_different_ids_for_different_requests() -> None:
#     """Test that two different requests generate different request IDs."""

#     class CustomCallNext:
#         async def __call__(self, request: Request) -> Response:
#             return Response("OK", status_code=200)

#     middleware = RequestIdMiddleware(CustomCallNext())
#     scope = {
#         "type": "http",
#         "method": "GET",
#         "headers": [],
#         "path": "/",
#     }

#     async def make_request() -> str:
#         """Simulate a single request in its own context."""
#         request = Request(scope, receive=lambda: None)
#         response = await middleware.dispatch(request, CustomCallNext())
#         return response.headers[REQUEST_ID_HEADER]

#     # Run each request in a separate context (simulating separate HTTP requests)
#     request_id_1 = await asyncio.create_task(make_request())
#     request_id_2 = await asyncio.create_task(make_request())

#     assert request_id_1 is not None
#     assert request_id_2 is not None
#     assert request_id_1 != request_id_2
