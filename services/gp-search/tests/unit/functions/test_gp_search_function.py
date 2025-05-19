from unittest.mock import MagicMock, patch

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
def event():
    return {"odsCode": "ABC123"}


@pytest.fixture
def lambda_context():
    return MagicMock()


@pytest.fixture
def bundle():
    return Bundle.model_construct(id="bundle-id")


def assert_response(
    response,
    expected_status_code,
    expected_body,
):
    assert response["statusCode"] == expected_status_code
    assert response["headers"] == {"Content-Type": "application/fhir+json"}
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
        ods_code,
        bundle,
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.return_value = bundle
        event = {"odsCode": ods_code}

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(event["odsCode"])

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    def test_lambda_handler_with_lowercase_ods_code(
        self, lambda_context, mock_ftrs_service, bundle
    ):
        # Arrange
        event = {"odsCode": "abc123"}  # Lowercase ODS code
        mock_ftrs_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with("ABC123")

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    @pytest.mark.parametrize(
        ("invalid_event", "expected_error_message"),
        [
            ({}, "data must contain ['odsCode'] properties"),
            (
                {"odsCode": ""},
                "data.odsCode must be longer than or equal to 5 characters",
            ),
            (
                {"odsCode": "ABC1"},
                "data.odsCode must be longer than or equal to 5 characters",
            ),
            (
                {"odsCode": "ABCD123456789"},
                "data.odsCode must be shorter than or equal to 12 characters",
            ),
            ({"odsCode": "ABC-123"}, "data.odsCode must match pattern ^[A-Z0-9]+$"),
        ],
        ids=[
            "event empty",
            "odsCode empty",
            "odsCode too short",
            "odsCode too long",
            "odsCode non-alphanumeric",
        ],
    )
    def test_lambda_handler_with_invalid_event(
        self,
        lambda_context,
        mock_ftrs_service,
        mock_error_util,
        invalid_event,
        expected_error_message,
    ):
        # Act
        response = lambda_handler(invalid_event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_not_called()
        mock_error_util.create_resource_validation_error.assert_called_once()
        assert_response(
            response,
            expected_status_code=422,
            expected_body=mock_error_util.create_resource_validation_error.return_value.model_dump_json(),
        )

        exception = mock_error_util.create_resource_validation_error.call_args[0][0]
        assert exception.validation_message == expected_error_message

    def test_lambda_handler_with_general_exception(
        self, lambda_context, mock_ftrs_service, event, mock_error_util
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.side_effect = Exception("Unexpected error")

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(event["odsCode"])
        mock_error_util.create_resource_internal_server_error.assert_called_once()
        assert_response(
            response,
            expected_status_code=500,
            expected_body=mock_error_util.create_resource_internal_server_error.return_value.model_dump_json(),
        )
