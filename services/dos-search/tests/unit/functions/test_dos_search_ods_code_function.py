from unittest.mock import ANY, MagicMock, call, patch

import pytest
from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.dos_search_ods_code_function import (
    DEFAULT_RESPONSE_HEADERS,
    lambda_handler,
)


@pytest.fixture
def mock_error_util():
    with patch("functions.dos_search_ods_code_function.error_util") as mock:
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
def mock_ftrs_service():
    with patch("functions.dos_search_ods_code_function.FtrsService") as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def lambda_context():
    return MagicMock()


EXPECTED_MULTI_VALUE_HEADERS = {
    header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
}


def _build_event_with_headers(headers: dict[str, str]):
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
    response,
    expected_status_code,
    expected_body,
):
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
            "version",
            "end-user-role",
            "application-id",
            "application-name",
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
        header_name,
        lambda_context,
        mock_ftrs_service,
        mock_logger,
        bundle,
    ):
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        event_with_headers = _build_event_with_headers({header_name: "value"})

        response = lambda_handler(event_with_headers, lambda_context)

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    def test_lambda_handler_rejects_invalid_custom_headers(
        self,
        lambda_context,
        mock_logger,
        mock_error_util,
    ):
        event_with_headers = _build_event_with_headers(
            {"X-NHSD-UNKNOWN": "abc", "Authorization": "token"}
        )

        response = lambda_handler(event_with_headers, lambda_context)

        mock_error_util.create_invalid_header_operation_outcome.assert_called_once_with(
            ["x-nhsd-unknown"]
        )
        mock_logger.warning.assert_called_with(
            "Invalid request headers supplied",
            invalid_headers=["x-nhsd-unknown"],
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
        lambda_context,
        mock_ftrs_service,
        mock_logger,
        ods_code,
        event,
        bundle,
        log_data,
        details,
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_logger.assert_has_calls(
            [
                call.init(ANY),
                call.info(
                    "Received request for odsCode",
                    ods_code=ods_code,
                    dos_message_category="REQUEST",
                ),
                call.get_response_size_and_duration(bundle, ANY),
                call.info(
                    "Successfully processed: Logging response time & size",
                    dos_response_time=ANY,
                    dos_response_size=len(bundle.model_dump_json().encode("utf-8")),
                    dos_message_category="METRICS",
                ),
                call.info(
                    "Creating response",
                    status_code=200,
                    body=ANY,
                    dos_message_category="RESPONSE",
                ),
            ]
        )

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    def test_lambda_handler_with_validation_error(
        self, lambda_context, mock_error_util, mock_logger, event, log_data, details
    ):
        # Arrange
        validation_error = ValidationError.from_exception_data("ValidationError", [])
        response_size = len(  # Override mocked response size to use this case's error model
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_logger.get_response_size_and_duration.return_value = (response_size, 1)

        # Act
        with patch(
            "functions.dos_search_ods_code_function.OrganizationQueryParams.model_validate",
            side_effect=validation_error,
        ):
            response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once_with(
            validation_error
        )

        mock_logger.assert_has_calls(
            [
                call.init(ANY),
                call.get_response_size_and_duration(
                    mock_error_util.create_validation_error_operation_outcome.return_value,
                    ANY,
                ),
                call.warning(
                    "Validation error occurred: Logging response time & size",
                    validation_errors=validation_error.errors(),
                    dos_response_time="1ms",
                    dos_response_size=response_size,
                ),
                call.info(
                    "Creating response",
                    status_code=400,
                    body=ANY,
                    dos_message_category="RESPONSE",
                ),
            ]
        )

        assert_response(
            response,
            expected_status_code=400,
            expected_body=mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json(),
        )

    def test_lambda_handler_with_general_exception(
        self,
        lambda_context,
        mock_ftrs_service,
        event,
        ods_code,
        mock_error_util,
        mock_logger,
        bundle,
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.side_effect = Exception("Unexpected error")

        # Act
        response = lambda_handler(event, lambda_context)
        print("easy search", response)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_error_util.create_resource_internal_server_error.assert_called_once()
        mock_logger.assert_has_calls(
            [
                call.init(ANY),
                call.info(
                    "Received request for odsCode",
                    ods_code=ods_code,
                    dos_message_category="REQUEST",
                ),
                call.get_response_size_and_duration(
                    mock_error_util.create_resource_internal_server_error.return_value,
                    ANY,
                ),
                call.exception(
                    "Internal server error occurred: Logging response time & size",
                    dos_response_time="1ms",
                    dos_response_size=len(bundle.model_dump_json().encode("utf-8")),
                ),
                call.info(
                    "Creating response",
                    status_code=500,
                    body=ANY,
                    dos_message_category="RESPONSE",
                ),
            ]
        )

        assert_response(
            response,
            expected_status_code=500,
            expected_body=mock_error_util.create_resource_internal_server_error.return_value.model_dump_json(),
        )

    def test_lambda_handler_with_empty_event(self, lambda_context):
        # Arrange
        empty_event = {}

        # Act & Assert
        with pytest.raises(KeyError, match="httpMethod"):
            lambda_handler(empty_event, lambda_context)
