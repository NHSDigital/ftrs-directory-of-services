from unittest.mock import MagicMock, call, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.gp_search_function import lambda_handler


@pytest.fixture
def mock_error_util():
    with patch("functions.gp_search_function.error_util") as mock:
        mock_validation_error = OperationOutcome.model_construct(id="validation-error")
        mock_internal_error = OperationOutcome.model_construct(id="internal-error")

        mock.create_resource_validation_error.return_value = mock_validation_error
        mock.create_resource_internal_server_error.return_value = mock_internal_error

        yield mock


@pytest.fixture
def mock_ftrs_service():
    with patch("functions.gp_search_function.FtrsService") as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def mock_logger():
    with patch("functions.gp_search_function.logger") as mock:
        yield mock


@pytest.fixture
def event(ods_code):
    return create_event(ods_code)


@pytest.fixture
def ods_code():
    return "ABC123"


@pytest.fixture
def lambda_context():
    return MagicMock()


@pytest.fixture
def bundle():
    return Bundle.model_construct(id="bundle-id")


def create_event(ods_code: str) -> dict:
    return {
        "path": "/organization",
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
    def test_lambda_handler_with_valid_ods_code(
        self,
        lambda_context,
        mock_ftrs_service,
        mock_logger,
        ods_code,
        event,
        bundle,
    ):
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

    def test_lambda_handler_with_lowercase_ods_code(
        self, lambda_context, mock_ftrs_service, mock_logger, bundle
    ):
        # Arrange
        event = create_event("abc123")  # Lowercase ODS code
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with("ABC123")
        mock_logger.assert_has_calls(
            [
                call.append_keys(ods_code="ABC123"),
                call.info("Successfully processed"),
                call.info("Creating response", extra={"status_code": 200}),
            ]
        )

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    @pytest.mark.skip(reason="Needs to be fixed")
    @pytest.mark.parametrize(
        ("ods_code", "expected_error_message"),
        [
            (
                "",
                "data.odsCode must be longer than or equal to 5 characters",
            ),
            (
                "ABC1",
                "data.odsCode must be longer than or equal to 5 characters",
            ),
            (
                "ABCD123456789",
                "data.odsCode must be shorter than or equal to 12 characters",
            ),
            (
                "ABC-123",
                "data.odsCode must match pattern ^[A-Z0-9]+$",
            ),
        ],
        ids=[
            "odsCode empty",
            "odsCode too short",
            "odsCode too long",
            "odsCode non-alphanumeric",
        ],
    )
    def test_lambda_handler_with_invalid_ods_code(
        self,
        lambda_context,
        mock_ftrs_service,
        mock_error_util,
        mock_logger,
        ods_code,
        event,
        expected_error_message,
    ):
        # Arrange
        event = create_event(ods_code)

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_not_called()
        mock_error_util.create_resource_validation_error.assert_called_once()

        exception = mock_error_util.create_resource_validation_error.call_args[0][0]
        assert exception.validation_message == expected_error_message

        mock_logger.assert_has_calls(
            [
                call.warning("Schema validation error occurred", exc_info=exception),
                call.info("Creating response", extra={"status_code": 422}),
            ]
        )

        assert_response(
            response,
            expected_status_code=422,
            expected_body=mock_error_util.create_resource_validation_error.return_value.model_dump_json(),
        )

    @pytest.mark.skip(reason="Needs to be fixed")
    def test_lambda_handler_with_general_exception(
        self,
        lambda_context,
        mock_ftrs_service,
        event,
        ods_code,
        mock_error_util,
        mock_logger,
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.side_effect = Exception("Unexpected error")

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(ods_code)
        mock_error_util.create_resource_internal_server_error.assert_called_once()

        mock_logger.assert_has_calls(
            [
                call.append_keys(ods_code=event["odsCode"]),
                call.exception("Internal server error occurred"),
                call.info("Creating response", extra={"status_code": 500}),
            ]
        )

        assert_response(
            response,
            expected_status_code=500,
            expected_body=mock_error_util.create_resource_internal_server_error.return_value.model_dump_json(),
        )
