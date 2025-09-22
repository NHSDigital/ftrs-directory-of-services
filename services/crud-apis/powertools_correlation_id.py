import uuid

from aws_lambda_powertools.utilities.correlation_ids import correlation_id
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class PowertoolsCorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that works with AWS Lambda Powertools correlation ID system.

    This middleware:
    1. Extracts the correlation ID from request headers or generates a new one
    2. Sets it in Lambda Powertools' correlation ID store
    3. Adds it to response headers
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract correlation ID from headers or generate a new one
        correlation_id_value = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )

        # Set in Lambda Powertools
        with correlation_id.set(correlation_id_value):
            # Process the request
            response = await call_next(request)

            # Add to response headers
            response.headers["X-Correlation-ID"] = correlation_id_value

            return response
