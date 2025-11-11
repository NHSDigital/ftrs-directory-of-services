from ftrs_common.utils.request_id import (
    REQUEST_ID_HEADER,
    add_request_id_header,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle request IDs in requests and responses.

    This middleware:
    1. Extracts the request ID from the request headers if present
    2. Adds the request ID to the response headers only if it was in the request
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER)
        response = await call_next(request)

        if request_id:
            return add_request_id_header(response, request_id)

        return response
