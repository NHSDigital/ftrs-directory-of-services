import uuid

from aws_lambda_powertools.logging import Logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class PowertoolsCorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that works with AWS Lambda Powertools correlation ID system.

    This middleware:
    1. Extracts the correlation ID from request headers or generates a new one
    2. Adds it to response headers
    3. Makes it available to the AWS Lambda Powertools logger
    """

    def __init__(self, app: any, logger: Logger = None) -> None:
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Extract correlation ID from headers or generate a new one
        correlation_id_value = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )

        # Append correlation ID to logger if available
        if self.logger:
            self.logger.append_keys(correlation_id=correlation_id_value)

        # Process the request
        response = await call_next(request)

        # Add to response headers
        response.headers["X-Correlation-ID"] = correlation_id_value

        return response
