from unittest.mock import ANY, MagicMock, call, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.dos_search_ods_code_function import lambda_handler


@pytest.fixture
def mock_error_util():
    with patch("functions.dos_search_ods_code_function.error_util") as mock:
        mock_validation_error = OperationOutcome.model_construct(id="validation-error")
        mock_internal_error = OperationOutcome.model_construct(id="internal-error")

        mock.create_validation_error_operation_outcome.return_value = (
            mock_validation_error
        )
        mock.create_resource_internal_server_error.return_value = mock_internal_error

        yield mock


@pytest.fixture
def mock_ftrs_service():
    with patch("functions.dos_search_ods_code_function.FtrsService") as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def mock_logger():
    with patch("functions.dos_search_ods_code_function.ftrs_logger") as mock:
        yield mock


@pytest.fixture
def event(ods_code):
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
def ods_code():
    return "ABC123"


@pytest.fixture
def lambda_context():
    return MagicMock()


@pytest.fixture
def bundle():
    return Bundle.model_construct(id="bundle-id")


@pytest.fixture
def log_data():
    return {
        "ftrs_nhsd_correlation_id": "FTRS_LOG_PLACEHOLDER",
        "nhsd_correlation_id": "FTRS_LOG_PLACEHOLDER",
        "ftrs_nhsd_request_id": "FTRS_LOG_PLACEHOLDER",
        "nhsd_request_id": "FTRS_LOG_PLACEHOLDER",
        "ftrs_message_id": "FTRS_LOG_PLACEHOLDER",
        "nhsd_message_id": "FTRS_LOG_PLACEHOLDER",
        "ftrs_message_category": "LOGGING",
        "ftrs_environment": "dos-search",
        "ftrs_api_version": "FTRS_LOG_PLACEHOLDER",
        "ftrs_lambda_version": "FTRS_LOG_PLACEHOLDER",
        "ftrs_response_time": "FTRS_LOG_PLACEHOLDER",
        "ftrs_response_size": "FTRS_LOG_PLACEHOLDER",
        "Opt_ftrs_end_user_role": "FTRS_LOG_PLACEHOLDER",
        "Opt_ftrs_client_id": "FTRS_LOG_PLACEHOLDER",
        "Opt_ftrs_application_name": "FTRS_LOG_PLACEHOLDER",
        "Opt_ftrs_request_parms": {},
    }


def assert_response(
    response,
    expected_status_code,
    expected_body,
):
    assert response["statusCode"] == expected_status_code
    assert response["multiValueHeaders"] == {"Content-Type": ["application/fhir+json"]}
    assert response["body"] == expected_body


class TestLambdaHandler:
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
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_logger.assert_has_calls(
            [
                call.info(
                    "Received request for odsCode", log_data=log_data, ods_code=ods_code
                ),
                call.info(
                    "Successfully processed",
                    log_data=log_data,
                    ftrs_response_time=ANY,
                    ftrs_response_size=ANY,
                ),
                call.info("Creating response", log_data=None, status_code=200),
            ]
        )

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    def test_lambda_handler_with_validation_error(
        self, lambda_context, mock_error_util, mock_logger, event, log_data
    ):
        # Arrange
        validation_error = ValidationError.from_exception_data("ValidationError", [])

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
                call.warning(
                    "Validation error occurred",
                    log_data=log_data,
                    validation_errors=validation_error.errors(),
                ),
                call.info("Creating response", log_data=None, status_code=400),
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
        log_data,
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.side_effect = Exception("Unexpected error")

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_error_util.create_resource_internal_server_error.assert_called_once()

        (print("Test easily searchable: ", event),)
        mock_logger.assert_has_calls(
            [
                call.info(
                    "Received request for odsCode", log_data=log_data, ods_code=ods_code
                ),
                call.exception("Internal server error occurred", log_data=log_data),
                call.info("Creating response", log_data=None, status_code=500),
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
