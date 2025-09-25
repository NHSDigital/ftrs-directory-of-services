import contextvars
import uuid
from contextlib import contextmanager
from typing import Generator, Optional, Protocol, TypeVar

# Context variable to store correlation ID throughout request processing
current_correlation_id = contextvars.ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    """Generate a new UUID v4 correlation ID."""
    return str(uuid.uuid4())


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context, or None if not set."""
    return current_correlation_id.get()


def set_correlation_id(correlation_id: Optional[str]) -> None:
    """Set the correlation ID in the current context."""
    if correlation_id:
        current_correlation_id.set(correlation_id)


@contextmanager
def correlation_id_context(correlation_id: Optional[str] = None) -> Generator:
    """Context manager to set and clear correlation ID."""
    token = None
    if correlation_id:
        token = current_correlation_id.set(correlation_id)
    try:
        yield
    finally:
        if token:
            current_correlation_id.reset(token)


# Define protocols for request and response-like objects without importing FastAPI
class RequestLike(Protocol):
    """Protocol for objects that have headers like a FastAPI Request."""

    @property
    def headers(self) -> dict: ...


class ResponseLike(Protocol):
    """Protocol for objects that have headers like a FastAPI Response."""

    @property
    def headers(self) -> dict: ...


T = TypeVar("T")


# FastAPI-specific functions, using Protocol types instead of direct imports
def extract_correlation_id(request: RequestLike) -> str:
    """
    Extract correlation ID from request headers or generate a new one.

    Args:
        request: An object with a headers attribute (like FastAPI Request)
    """
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = generate_correlation_id()
    return correlation_id


def add_correlation_id_header(response: T, correlation_id: Optional[str] = None) -> T:
    """
    Add the correlation ID to the response headers.

    Args:
        response: An object with a headers attribute (like FastAPI Response)
        correlation_id: The correlation ID to add, or None to use the current one
    """
    if correlation_id is None:
        correlation_id = get_correlation_id()

    if correlation_id and hasattr(response, "headers"):
        response.headers["X-Correlation-ID"] = correlation_id

    return response


# # Conditional import of FastAPI middleware
# try:
#     from fastapi import Request, Response
#     from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

#     class CorrelationIdMiddleware(BaseHTTPMiddleware):
#         """
#         Middleware to handle correlation IDs in requests and responses.
#         Only available if FastAPI is installed.
#         """

#         async def dispatch(
#             self, request: Request, call_next: RequestResponseEndpoint
#         ) -> Response:
#             correlation_id = extract_correlation_id(request)
#             set_correlation_id(correlation_id)

#             response = await call_next(request)

#             return add_correlation_id_header(response, correlation_id)

# except ImportError:
#     # FastAPI not available, middleware not defined
#     pass
