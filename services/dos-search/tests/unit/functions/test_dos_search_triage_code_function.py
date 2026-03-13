from collections.abc import Generator
from unittest.mock import ANY, MagicMock, patch

import pytest
from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.dos_search_triage_code_function import (
    DEFAULT_RESPONSE_HEADERS,
    lambda_handler,
)
from functions.logbase import DosSearchLogBase


@pytest.fixture
def mock_request_context(
    mock_setup_request: MagicMock,
) -> Generator[MagicMock, None, None]:
    with (
        patch("functions.request_context_middleware.logger") as mock_middleware_logger,
    ):
        mock_middleware_logger.thread_safe_clear_keys.return_value = None
        context = MagicMock()
        context.setup_request = mock_setup_request
        context.middleware_logger = mock_middleware_logger
        yield context


@pytest.fixture
def mock_logger() -> Generator[MagicMock, None, None]:
    with patch("functions.dos_search_triage_code_function.logger") as mock:
        yield mock


@pytest.fixture
def mock_feature_flag_is_enabled() -> Generator[MagicMock, None, None]:
    with patch("ftrs_common.feature_flags.feature_flag_handlers.is_enabled") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def lambda_context() -> MagicMock:
    return MagicMock()


EXPECTED_MULTI_VALUE_HEADERS = {
    header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
}


def _build_event(http_method: str = "POST") -> dict[str, object]:
    return {
        "path": "/triage_code",
        "httpMethod": http_method,
        "queryStringParameters": {},
        "requestContext": {"requestId": "req-id"},
        "headers": {},
    }


def assert_response(
    response: dict[str, object],
    expected_status_code: int,
    expected_body: str,
) -> None:
    assert response["statusCode"] == expected_status_code
    assert response["multiValueHeaders"] == EXPECTED_MULTI_VALUE_HEADERS
    assert response["body"] == expected_body


def test_lambda_handler_with_feature_flag_enabled(
    lambda_context: MagicMock,
    mock_request_context: MagicMock,
    mock_logger: MagicMock,
    mock_feature_flag_is_enabled: MagicMock,
) -> None:
    event = _build_event()

    response = lambda_handler(event, lambda_context)

    expected_resource = OperationOutcome.model_validate(
        {
            "issue": [
                {
                    "severity": "warning",
                    "code": "not-supported",
                    "diagnostics": (
                        "Triage code search endpoint is not yet implemented"
                    ),
                }
            ]
        }
    )
    mock_request_context.setup_request.assert_called_once()
    mock_request_context.middleware_logger.thread_safe_clear_keys.assert_called_once()
    mock_feature_flag_is_enabled.assert_called_once_with(
        "dos_search_triage_code_enabled",
        False,
    )
    mock_logger.log.assert_any_call(
        DosSearchLogBase.DOS_SEARCH_017,
        feature_flag="DOS_SEARCH_TRIAGE_CODE_ENABLED",
        feature_flag_status="enabled",
        dos_message_category="FEATURE_FLAG",
    )
    mock_logger.log.assert_any_call(
        DosSearchLogBase.DOS_SEARCH_015,
        dos_message_category="REQUEST",
    )
    mock_logger.log.assert_any_call(
        DosSearchLogBase.DOS_SEARCH_018,
        dos_response_time=ANY,
        dos_response_size=len(expected_resource.model_dump_json().encode("utf-8")),
        dos_message_category="METRICS",
    )
    assert_response(
        response,
        expected_status_code=501,
        expected_body=expected_resource.model_dump_json(),
    )


def test_lambda_handler_with_feature_flag_disabled(
    lambda_context: MagicMock,
    mock_request_context: MagicMock,
    mock_logger: MagicMock,
    mock_feature_flag_is_enabled: MagicMock,
) -> None:
    mock_feature_flag_is_enabled.return_value = False
    event = _build_event()

    response = lambda_handler(event, lambda_context)

    expected_resource = OperationOutcome.model_validate(
        {
            "issue": [
                {
                    "severity": "fatal",
                    "code": "exception",
                    "diagnostics": (
                        "Service Unavailable: Triage code search endpoint is currently disabled"
                    ),
                }
            ]
        }
    )
    mock_request_context.setup_request.assert_called_once()
    mock_request_context.middleware_logger.thread_safe_clear_keys.assert_called_once()
    mock_feature_flag_is_enabled.assert_called_once_with(
        "dos_search_triage_code_enabled",
        False,
    )
    mock_logger.log.assert_any_call(
        DosSearchLogBase.DOS_SEARCH_016,
        feature_flag="DOS_SEARCH_TRIAGE_CODE_ENABLED",
        feature_flag_status="disabled",
        dos_message_category="FEATURE_FLAG",
        dos_response_time=ANY,
        dos_response_size=len(expected_resource.model_dump_json().encode("utf-8")),
    )
    assert_response(
        response,
        expected_status_code=503,
        expected_body=expected_resource.model_dump_json(),
    )


def test_lambda_handler_rejects_get_requests(
    lambda_context: MagicMock,
    mock_request_context: MagicMock,
    mock_logger: MagicMock,
    mock_feature_flag_is_enabled: MagicMock,
) -> None:
    event = _build_event(http_method="GET")

    response = lambda_handler(event, lambda_context)

    mock_request_context.setup_request.assert_called_once()
    mock_request_context.middleware_logger.thread_safe_clear_keys.assert_called_once()
    mock_feature_flag_is_enabled.assert_not_called()
    mock_logger.log.assert_not_called()
    assert response["statusCode"] == 404
