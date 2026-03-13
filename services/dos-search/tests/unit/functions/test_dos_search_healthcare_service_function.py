from collections.abc import Generator
from unittest.mock import ANY, MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM
from functions.dos_search_healthcare_service_function import (
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
def mock_error_util() -> Generator[MagicMock, None, None]:
    with patch("functions.dos_search_healthcare_service_function.error_util") as mock:
        mock.create_validation_error_operation_outcome.return_value = (
            OperationOutcome.model_construct(id="validation-error")
        )
        mock.create_resource_internal_server_error.return_value = (
            OperationOutcome.model_construct(id="internal-error")
        )
        mock.create_resource_service_unavailable_error.return_value = (
            OperationOutcome.model_construct(id="service-unavailable-error")
        )
        yield mock


@pytest.fixture
def mock_ftrs_service() -> Generator[MagicMock, None, None]:
    with patch(
        "functions.dos_search_healthcare_service_function.HealthcareServicesByOdsService"
    ) as mock_class:
        yield mock_class.return_value


@pytest.fixture
def mock_logger() -> Generator[MagicMock, None, None]:
    with patch("functions.dos_search_healthcare_service_function.logger") as mock:
        yield mock


@pytest.fixture
def mock_feature_flag_is_enabled() -> Generator[MagicMock, None, None]:
    with patch("ftrs_common.feature_flags.feature_flag_handlers.is_enabled") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def lambda_context() -> MagicMock:
    return MagicMock()


@pytest.fixture
def bundle() -> Bundle:
    return Bundle.model_construct(id="test-bundle", type="searchset")


EXPECTED_MULTI_VALUE_HEADERS = {
    header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
}


def _build_event(ods_code: str) -> dict[str, object]:
    return {
        "path": "/HealthcareService",
        "httpMethod": "GET",
        "queryStringParameters": {
            "organization.identifier": f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}",
        },
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
    mock_ftrs_service: MagicMock,
    mock_logger: MagicMock,
    mock_feature_flag_is_enabled: MagicMock,
    bundle: Bundle,
) -> None:
    mock_ftrs_service.healthcare_services_by_ods.return_value = bundle
    event = _build_event("ABC123")

    response = lambda_handler(event, lambda_context)

    mock_request_context.setup_request.assert_called_once()
    mock_request_context.middleware_logger.thread_safe_clear_keys.assert_called_once()
    mock_feature_flag_is_enabled.assert_called_once_with(
        "dos_search_healthcare_service_enabled",
        False,
    )
    mock_ftrs_service.healthcare_services_by_ods.assert_called_once_with("ABC123")
    mock_logger.log.assert_any_call(
        DosSearchLogBase.DOS_SEARCH_014,
        feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
        feature_flag_status="enabled",
        dos_message_category="FEATURE_FLAG",
    )
    assert_response(
        response,
        expected_status_code=200,
        expected_body=bundle.model_dump_json(),
    )


def test_lambda_handler_with_feature_flag_disabled(
    lambda_context: MagicMock,
    mock_request_context: MagicMock,
    mock_error_util: MagicMock,
    mock_ftrs_service: MagicMock,
    mock_logger: MagicMock,
    mock_feature_flag_is_enabled: MagicMock,
) -> None:
    mock_feature_flag_is_enabled.return_value = False
    event = _build_event("ABC123")

    response = lambda_handler(event, lambda_context)

    mock_request_context.setup_request.assert_called_once()
    mock_request_context.middleware_logger.thread_safe_clear_keys.assert_called_once()
    mock_feature_flag_is_enabled.assert_called_once_with(
        "dos_search_healthcare_service_enabled",
        False,
    )
    mock_ftrs_service.healthcare_services_by_ods.assert_not_called()
    mock_error_util.create_resource_service_unavailable_error.assert_called_once()
    mock_logger.log.assert_any_call(
        DosSearchLogBase.DOS_SEARCH_013,
        feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
        feature_flag_status="disabled",
        dos_message_category="FEATURE_FLAG",
        dos_response_time=ANY,
        dos_response_size=68,
    )
    assert_response(
        response,
        expected_status_code=503,
        expected_body=mock_error_util.create_resource_service_unavailable_error.return_value.model_dump_json(),
    )
