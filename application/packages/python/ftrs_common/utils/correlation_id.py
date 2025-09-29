import contextvars
import uuid
from contextlib import contextmanager
from typing import Generator, Optional, Protocol, TypeVar

CORRELATION_ID_HEADER = "X-Correlation-ID"

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
    """Protocol for request objects that have headers."""

    @property
    def headers(self) -> dict: ...


class ResponseLike(Protocol):
    """Protocol for response objects that have headers."""

    @property
    def headers(self) -> dict: ...


T = TypeVar("T")


def ensure_correlation_id(existing: str | None = None) -> str:
    """
    Ensure a correlation ID exists in context and return it.
    - If an explicit (valid) existing value is provided, use it.
    - Else reuse context value if present.
    - Else generate, set, return.
    """
    if existing:
        set_correlation_id(existing)
        return existing
    current = get_correlation_id()
    if current:
        return current
    new_id = generate_correlation_id()
    set_correlation_id(new_id)
    return new_id


def extract_correlation_id(request: RequestLike) -> str:
    correlation_id = request.headers.get(CORRELATION_ID_HEADER)
    return ensure_correlation_id(correlation_id)


def add_correlation_id_header(response: T, correlation_id: Optional[str] = None) -> T:
    correlation_id = ensure_correlation_id(correlation_id)
    if hasattr(response, "headers"):
        response.headers[CORRELATION_ID_HEADER] = correlation_id
    return response
