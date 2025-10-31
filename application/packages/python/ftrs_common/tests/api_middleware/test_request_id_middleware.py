from unittest.mock import AsyncMock, MagicMock

import pytest
from ftrs_common.api_middleware.request_id_middleware import RequestIdMiddleware
from ftrs_common.utils.request_id import REQUEST_ID_HEADER


@pytest.fixture
def middleware() -> RequestIdMiddleware:
    """Create a RequestIdMiddleware instance."""
    return RequestIdMiddleware(app=MagicMock())


@pytest.fixture
def mock_request() -> MagicMock:
    """Create a mock request."""
    request = MagicMock()
    request.headers = {}
    return request


@pytest.fixture
def mock_call_next() -> AsyncMock:
    """Create a mock call_next function."""
    mock_response = MagicMock()
    mock_response.headers = {}
    call_next = AsyncMock(return_value=mock_response)
    return call_next


@pytest.mark.asyncio
async def test_middleware_adds_request_id_header_when_present_in_request(
    middleware: RequestIdMiddleware,
    mock_request: MagicMock,
    mock_call_next: AsyncMock,
) -> None:
    """Test that the middleware adds the request ID to the response when present in the request."""
    request_id = "test-request-id-123"
    mock_request.headers = {REQUEST_ID_HEADER: request_id}

    response = await middleware.dispatch(mock_request, mock_call_next)

    mock_call_next.assert_called_once_with(mock_request)
    assert response.headers[REQUEST_ID_HEADER] == request_id


@pytest.mark.asyncio
async def test_middleware_does_not_add_request_id_header_when_not_in_request(
    middleware: RequestIdMiddleware,
    mock_request: MagicMock,
    mock_call_next: AsyncMock,
) -> None:
    """Test that the middleware does not add the request ID to the response when not in the request."""
    mock_request.headers = {}

    response = await middleware.dispatch(mock_request, mock_call_next)

    mock_call_next.assert_called_once_with(mock_request)
    assert REQUEST_ID_HEADER not in response.headers


@pytest.mark.asyncio
async def test_middleware_processes_request_even_without_request_id(
    middleware: RequestIdMiddleware,
    mock_request: MagicMock,
    mock_call_next: AsyncMock,
) -> None:
    """Test that the middleware allows requests to be processed even without a request ID."""
    mock_request.headers = {}

    response = await middleware.dispatch(mock_request, mock_call_next)

    mock_call_next.assert_called_once_with(mock_request)
    assert response is not None


@pytest.mark.asyncio
async def test_middleware_preserves_request_id_from_request_headers(
    middleware: RequestIdMiddleware,
    mock_request: MagicMock,
    mock_call_next: AsyncMock,
) -> None:
    """Test that the middleware preserves the exact request ID from the request headers."""
    request_id = "uuid-1234-5678-abcd"
    mock_request.headers = {REQUEST_ID_HEADER: request_id}

    response = await middleware.dispatch(mock_request, mock_call_next)

    mock_call_next.assert_called_once_with(mock_request)
    assert response.headers[REQUEST_ID_HEADER] == request_id


@pytest.mark.asyncio
async def test_middleware_handles_empty_string_request_id(
    middleware: RequestIdMiddleware,
    mock_request: MagicMock,
    mock_call_next: AsyncMock,
) -> None:
    """Test that the middleware handles an empty string request ID."""
    mock_request.headers = {REQUEST_ID_HEADER: ""}

    response = await middleware.dispatch(mock_request, mock_call_next)

    mock_call_next.assert_called_once_with(mock_request)
    assert REQUEST_ID_HEADER not in response.headers


@pytest.mark.asyncio
async def test_middleware_calls_next_handler_exactly_once(
    middleware: RequestIdMiddleware,
    mock_request: MagicMock,
    mock_call_next: AsyncMock,
) -> None:
    """Test that call_next is invoked exactly once regardless of request ID presence."""
    request_id = "test-id"
    mock_request.headers = {REQUEST_ID_HEADER: request_id}

    await middleware.dispatch(mock_request, mock_call_next)

    assert mock_call_next.call_count == 1
