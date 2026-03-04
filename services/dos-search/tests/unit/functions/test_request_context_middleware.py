from unittest.mock import MagicMock, patch

import pytest
from aws_lambda_powertools.event_handler import Response

from functions.request_context_middleware import request_context_middleware


@pytest.fixture
def app():
    return MagicMock()


@pytest.fixture
def mock_setup_request():
    with patch("functions.request_context_middleware.setup_request") as mock:
        yield mock


@pytest.fixture
def mock_logger():
    with patch("functions.request_context_middleware.logger") as mock:
        yield mock


class TestRequestContextMiddleware:
    def test_calls_in_order_setup_then_next_then_clear(
        self, app, mock_setup_request, mock_logger
    ):
        call_order = []
        mock_setup_request.side_effect = lambda *a, **kw: call_order.append(
            "setup_request"
        )
        mock_logger.thread_safe_clear_keys.side_effect = lambda: call_order.append(
            "thread_safe_clear_keys"
        )
        next_middleware = MagicMock(
            side_effect=lambda *a: call_order.append("next_middleware")
            or MagicMock(spec=Response)
        )

        request_context_middleware(app, next_middleware)

        assert call_order == ["setup_request", "next_middleware", "thread_safe_clear_keys"]

    def test_returns_response_from_next_middleware(
        self, app, mock_setup_request, mock_logger
    ):
        expected_response = MagicMock(spec=Response)
        next_middleware = MagicMock(return_value=expected_response)

        result = request_context_middleware(app, next_middleware)

        assert result is expected_response

    def test_thread_safe_clear_keys_called_even_when_next_middleware_raises(
        self, app, mock_setup_request, mock_logger
    ):
        next_middleware = MagicMock(side_effect=RuntimeError("upstream error"))

        with pytest.raises(RuntimeError):
            request_context_middleware(app, next_middleware)

        mock_logger.thread_safe_clear_keys.assert_called_once()

    def test_setup_request_receives_current_event_and_logger(
        self, app, mock_setup_request, mock_logger
    ):
        next_middleware = MagicMock(return_value=MagicMock(spec=Response))

        request_context_middleware(app, next_middleware)

        mock_setup_request.assert_called_once_with(app.current_event, mock_logger)
