from fastapi import Request, Response
from ftrs_common.utils.correlation_id import (
    add_correlation_id_header,
    extract_correlation_id,
    set_correlation_id,
)
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle correlation IDs in requests and responses.

    This middleware:
    1. Extracts the correlation ID from the request headers or generates a new one
    2. Sets the correlation ID in the current context
    3. Adds the correlation ID to the response headers
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        correlation_id = extract_correlation_id(request)
        set_correlation_id(correlation_id)

        response = await call_next(request)

        return add_correlation_id_header(response, correlation_id)
