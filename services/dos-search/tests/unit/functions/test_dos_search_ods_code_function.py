from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.libraries.dos_search_ods_code_function import (
    DEFAULT_RESPONSE_HEADERS,
    lambda_handler,
)


@pytest.fixture
def mock_error_util() -> object:
    with patch("functions.libraries.dos_search_ods_code_function.error_util") as mock:
        mock_validation_error = OperationOutcome.model_construct(id="validation-error")
        mock_internal_error = OperationOutcome.model_construct(id="internal-error")
        mock_invalid_header = OperationOutcome.model_construct(id="invalid-header")

        mock.create_validation_error_operation_outcome.return_value = (
            mock_validation_error
        )
        mock.create_resource_internal_server_error.return_value = mock_internal_error
        mock.create_invalid_header_operation_outcome.return_value = mock_invalid_header

        yield mock


@pytest.fixture
def mock_ftrs_service() -> object:
    with patch(
        "functions.libraries.dos_search_ods_code_function.FtrsService"
    ) as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def mock_logger() -> object:
    with patch("functions.libraries.dos_search_ods_code_function.logger") as mock:
        yield mock


@pytest.fixture
def event(ods_code: str) -> dict:
    return {
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{ods_code}",
            "_revinclude": "Endpoint:organization",
        },
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "body": None,
    }


@pytest.fixture
def ods_code() -> str:
    return "ABC123"


@pytest.fixture
def lambda_context() -> object:
    return MagicMock()


@pytest.fixture
def bundle() -> Bundle:
    return Bundle.model_construct(id="bundle-id")


EXPECTED_MULTI_VALUE_HEADERS = {
    header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
}


def _build_event_with_headers(headers: dict[str, str]) -> dict:
    return {
        "path": "/Organization",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": "odsOrganisationCode|ABC123",
            "_revinclude": "Endpoint:organization",
        },
        "requestContext": {"requestId": "req-id"},
        "headers": headers,
    }


def assert_response(
    response: dict,
    expected_status_code: int,
    expected_body: str,
) -> None:
    assert response["statusCode"] == expected_status_code
    assert response["multiValueHeaders"] == EXPECTED_MULTI_VALUE_HEADERS
    assert response["body"] == expected_body


class TestLambdaHandler:
    @pytest.mark.parametrize(
        "header_name",
        [
            "Authorization",
            "Content-Type",
            "NHSD-Correlation-ID",
            "nhsd-correlation-id",
            "NHSD-Request-ID",
            "nhsd-request-id",
            "NHSD-Message-Id",
            "NHSD-Api-Version",
            "NHSD-End-User-Role",
            "NHSD-Client-Id",
            "NHSD-Connecting-Party-App-Name",
            "Accept",
            "Accept-Encoding",
            "Accept-Language",
            "User-Agent",
            "Host",
            "X-Amzn-Trace-Id",
            "X-Forwarded-For",
            "X-Forwarded-Port",
            "X-Forwarded-Proto",
        ],
    )
    def test_lambda_handler_allows_valid_custom_headers(
        self,
        header_name: str,
        lambda_context: object,
        mock_ftrs_service: object,
        mock_logger: object,
        bundle: Bundle,
    ) -> None:
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        event_with_headers = _build_event_with_headers({header_name: "value"})

        response = lambda_handler(event_with_headers, lambda_context)

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    def test_lambda_handler_rejects_invalid_custom_headers(
        self,
        lambda_context: object,
        mock_logger: object,
        mock_error_util: object,
    ) -> None:
        event_with_headers = _build_event_with_headers(
            {"X-NHSD-UNKNOWN": "abc", "Authorization": "token"}
        )

        response = lambda_handler(event_with_headers, lambda_context)

        mock_error_util.create_invalid_header_operation_outcome.assert_called_once_with(
            ["x-nhsd-unknown"]
        )
        mock_logger.warning.assert_called_with(
            "Invalid request headers supplied",
            extra={"invalid_headers": ["x-nhsd-unknown"]},
        )
        assert_response(
            response,
            expected_status_code=400,
            expected_body=mock_error_util.create_invalid_header_operation_outcome.return_value.model_dump_json(),
        )

    @pytest.mark.parametrize(
        "ods_code",
        [
            "ABC12",
            "ABC123456789",
            "ABC123",
            "ABCDEF",
            "123456",
        ],
        ids=[
            "odsCode minimum length",
            "odsCode maximum length",
            "odsCode alphanumeric",
            "odsCode only uppercase characters",
            "odsCode only numbers",
        ],
    )
    def test_lambda_handler_with_valid_event(
        self,
        lambda_context: object,
        mock_ftrs_service: object,
        mock_logger: object,
        ods_code: str,
        event: dict,
        bundle: Bundle,
    ) -> None:
        # Arrange
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_logger.assert_has_calls(
            [
                call.append_keys(ods_code=ods_code),
                call.info("Successfully processed"),
                call.info("Creating response", extra={"status_code": 200}),
            ]
        )

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    def test_lambda_handler_with_validation_error(
        self,
        lambda_context: object,
        mock_error_util: object,
        mock_logger: object,
        event: dict,
    ) -> None:
        # Arrange
        validation_error = ValidationError.from_exception_data("ValidationError", [])

        # Act
        with patch(
            "functions.libraries.dos_search_ods_code_function.OrganizationQueryParams.model_validate",
            side_effect=validation_error,
        ):
            response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once_with(
            validation_error
        )

        mock_logger.assert_has_calls(
            [
                call.warning(
                    "Validation error occurred",
                    extra={"validation_errors": validation_error.errors()},
                ),
                call.info("Creating response", extra={"status_code": 400}),
            ]
        )

        assert_response(
            response,
            expected_status_code=400,
            expected_body=mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json(),
        )

    def test_lambda_handler_with_general_exception(
        self,
        lambda_context: object,
        mock_ftrs_service: object,
        event: dict,
        ods_code: str,
        mock_error_util: object,
        mock_logger: object,
    ) -> None:
        # Arrange
        mock_ftrs_service.endpoints_by_ods.side_effect = Exception("Unexpected error")

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_error_util.create_resource_internal_server_error.assert_called_once()

        mock_logger.assert_has_calls(
            [
                call.append_keys(ods_code=ods_code),
                call.exception("Internal server error occurred"),
                call.info("Creating response", extra={"status_code": 500}),
            ]
        )

        assert_response(
            response,
            expected_status_code=500,
            expected_body=mock_error_util.create_resource_internal_server_error.return_value.model_dump_json(),
        )

    def test_lambda_handler_with_empty_event(self, lambda_context: object) -> None:
        # Arrange
        empty_event = {}

        # Act & Assert
        with pytest.raises(KeyError, match="httpMethod"):
            lambda_handler(empty_event, lambda_context)
