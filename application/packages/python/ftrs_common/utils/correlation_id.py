import contextvars
import uuid
from contextlib import contextmanager
from typing import Generator, Optional

from fastapi import Request, Response

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


def extract_correlation_id(request: Request) -> str:
    """Extract correlation ID from request headers or generate a new one."""
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = generate_correlation_id()
    return correlation_id


def add_correlation_id_header(
    response: Response, correlation_id: Optional[str] = None
) -> Response:
    """Add the correlation ID to the response headers."""
    if correlation_id is None:
        correlation_id = get_correlation_id()

    if correlation_id:
        response.headers["X-Correlation-ID"] = correlation_id

    return response
