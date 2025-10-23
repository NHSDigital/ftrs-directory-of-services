from ftrs_common.utils.request_id import (
    REQUEST_ID_HEADER,
    add_request_id_header,
    fetch_or_set_request_id,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle request IDs in requests and responses.

    This middleware:
    1. Extracts the request ID from the request headers or generates a new one
    2. Sets the request ID in the current context
    3. Adds the request ID to the response headers
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER)
        fetch_or_set_request_id(request_id)
        response = await call_next(request)
        return add_request_id_header(response, request_id)
