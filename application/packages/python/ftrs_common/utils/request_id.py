import contextvars
import uuid
from contextlib import contextmanager
from typing import Generator, Optional

REQUEST_ID_HEADER = "X-Request-ID"

# Context variable to store request ID throughout request processing
current_request_id = contextvars.ContextVar("request_id", default=None)


def generate_request_id() -> str:
    """Generate a new UUID v4 request ID."""
    return str(uuid.uuid4())


def get_request_id() -> Optional[str]:
    """Get the current request ID from context, or None if not set."""
    return current_request_id.get()


def set_request_id(request_id: Optional[str]) -> None:
    """Set the request ID in the current context."""
    if request_id:
        current_request_id.set(request_id)


@contextmanager
def request_id_context(request_id: Optional[str] = None) -> Generator:
    """Context manager to set and clear request ID."""
    token = None
    if request_id:
        token = current_request_id.set(request_id)
    try:
        yield
    finally:
        if token:
            current_request_id.reset(token)


def fetch_or_set_request_id(
    context_id: str | None = None, header_id: str | None = None
) -> str:
    """
    Ensure a request ID exists in context and return it.
    - If an explicit (valid) existing value is provided, use it.
    - Else reuse context value if present.
    - Else generate, set, return.
    """
    if header_id:
        set_request_id(header_id)
        return header_id
    elif context_id:
        set_request_id(context_id)
        return context_id
    current = get_request_id()
    if current:
        return current
    new_id = generate_request_id()
    set_request_id(new_id)
    return new_id


def add_request_id_header(response: dict, request_id: Optional[str] = None) -> dict:
    """Add request ID to response headers."""
    request_id = fetch_or_set_request_id(request_id)
    if hasattr(response, "headers"):
        response.headers[REQUEST_ID_HEADER] = request_id
    return response
