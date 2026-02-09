from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.dos_search_healthcare_service_function import (
    DEFAULT_RESPONSE_HEADERS,
    lambda_handler,
)


@pytest.fixture
def mock_error_util():
    with patch("functions.dos_search_healthcare_service_function.error_util") as mock:
        mock_validation_error = OperationOutcome.model_construct(id="validation-error")
        mock_internal_error = OperationOutcome.model_construct(id="internal-error")

        mock.create_validation_error_operation_outcome.return_value = (
            mock_validation_error
        )
        mock.create_resource_internal_server_error.return_value = mock_internal_error

        yield mock


@pytest.fixture
def mock_ftrs_service():
    with patch(
        "functions.dos_search_healthcare_service_function.FtrsService"
    ) as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def mock_dos_logger(healthcare_service_bundle):
    with patch("functions.dos_search_healthcare_service_function.dos_logger") as mock:
        response_size = len(healthcare_service_bundle.model_dump_json().encode("utf-8"))
        response_time = 1
        mock.get_response_size_and_duration.return_value = (
            response_size,
            response_time,
        )
        yield mock


@pytest.fixture
def lambda_context() -> MagicMock:
    return MagicMock()


@pytest.fixture
def healthcare_service_bundle() -> Bundle:
    return Bundle.model_construct(id="healthcare-service-bundle", type="searchset")


@pytest.fixture
def ods_code() -> str:
    return "ABC123"


@pytest.fixture
def healthcare_service_event(ods_code: str) -> dict:
    return {
        "headers": {
            "NHSD-Correlation-ID": "request_id.correlation_id.message_id",
            "NHSD-Request-ID": "request_id",
        },
        "path": "/HealthcareService",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{ods_code}",
            "_include": "HealthcareService:location",
        },
        "pathParameters": None,
        "requestContext": {
            "requestId": "796bdcd6-c5b0-4862-af98-9d2b1b853703",
        },
        "body": None,
    }


EXPECTED_MULTI_VALUE_HEADERS = {
    header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
}


def _build_healthcare_service_event(
    ods_code: str = "ABC123",
    include: str = "HealthcareService:location",
    headers: dict[str, str] | None = None,
) -> dict:
    return {
        "path": "/HealthcareService",
        "httpMethod": "GET",
        "queryStringParameters": {
            "identifier": f"odsOrganisationCode|{ods_code}",
            "_include": include,
        },
        "requestContext": {"requestId": "req-id"},
        "headers": headers or {},
    }


def assert_response(
    response: dict,
    expected_status_code: int,
    expected_body: str,
) -> None:
    assert response["statusCode"] == expected_status_code
    assert response["multiValueHeaders"] == EXPECTED_MULTI_VALUE_HEADERS
    assert response["body"] == expected_body


class TestHealthcareServiceLambdaHandler:
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
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_dos_logger: MagicMock,
        healthcare_service_bundle: Bundle,
        ods_code: str,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.return_value = (
            healthcare_service_bundle
        )
        event = _build_healthcare_service_event(ods_code=ods_code)

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.healthcare_services_by_ods.assert_called_once_with(
            ods_code.upper()
        )
        assert_response(
            response,
            expected_status_code=200,
            expected_body=healthcare_service_bundle.model_dump_json(),
        )

    def test_lambda_handler_with_validation_error(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        validation_error = ValidationError.from_exception_data("ValidationError", [])
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = _build_healthcare_service_event()

        # Act
        with patch(
            "functions.dos_search_healthcare_service_function.HealthcareServiceQueryParams.model_validate",
            side_effect=validation_error,
        ):
            response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once_with(
            validation_error
        )
        assert_response(
            response,
            expected_status_code=400,
            expected_body=mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json(),
        )

    def test_lambda_handler_with_general_exception(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
        healthcare_service_bundle: Bundle,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.side_effect = Exception(
            "Unexpected error"
        )
        event = _build_healthcare_service_event()

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.healthcare_services_by_ods.assert_called_once_with("ABC123")
        mock_error_util.create_resource_internal_server_error.assert_called_once()
        assert_response(
            response,
            expected_status_code=500,
            expected_body=mock_error_util.create_resource_internal_server_error.return_value.model_dump_json(),
        )

    def test_lambda_handler_with_empty_event(self, lambda_context: MagicMock) -> None:
        # Arrange
        empty_event = {}

        # Act & Assert
        with pytest.raises(KeyError, match="httpMethod"):
            lambda_handler(empty_event, lambda_context)

    def test_lambda_handler_missing_identifier(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = {
            "path": "/HealthcareService",
            "httpMethod": "GET",
            "queryStringParameters": {
                "_include": "HealthcareService:location",
            },
            "requestContext": {"requestId": "req-id"},
            "headers": {},
        }

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once()
        assert response["statusCode"] == 400

    def test_lambda_handler_missing_include(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = {
            "path": "/HealthcareService",
            "httpMethod": "GET",
            "queryStringParameters": {
                "identifier": "odsOrganisationCode|ABC123",
            },
            "requestContext": {"requestId": "req-id"},
            "headers": {},
        }

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once()
        assert response["statusCode"] == 400

    def test_lambda_handler_invalid_identifier_system(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = _build_healthcare_service_event()
        event["queryStringParameters"]["identifier"] = "wrongSystem|ABC123"

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once()
        assert response["statusCode"] == 400

    def test_lambda_handler_invalid_ods_code_format(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = _build_healthcare_service_event()
        event["queryStringParameters"]["identifier"] = (
            "odsOrganisationCode|AB"  # too short
        )

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once()
        assert response["statusCode"] == 400

    def test_lambda_handler_logs_request(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_dos_logger: MagicMock,
        healthcare_service_bundle: Bundle,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.return_value = (
            healthcare_service_bundle
        )
        event = _build_healthcare_service_event(ods_code="ABC123")

        # Act
        lambda_handler(event, lambda_context)

        # Assert
        mock_dos_logger.init.assert_called_once()
        mock_dos_logger.info.assert_any_call(
            "Received request for healthcare service",
            ods_code="ABC123",
            dos_message_category="REQUEST",
        )

    def test_lambda_handler_logs_validation_error(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        validation_error = ValidationError.from_exception_data("ValidationError", [])
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = _build_healthcare_service_event()

        # Act
        with patch(
            "functions.dos_search_healthcare_service_function.HealthcareServiceQueryParams.model_validate",
            side_effect=validation_error,
        ):
            lambda_handler(event, lambda_context)

        # Assert
        mock_dos_logger.warning.assert_called_once_with(
            "Validation error occurred",
            validation_errors=validation_error.errors(),
            dos_response_time="1ms",
            dos_response_size=response_size,
        )

    def test_lambda_handler_logs_internal_error(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.side_effect = Exception(
            "DB connection failed"
        )
        event = _build_healthcare_service_event()

        # Act
        lambda_handler(event, lambda_context)

        # Assert
        mock_dos_logger.exception.assert_called_once()
        assert "Internal server error occurred" in str(
            mock_dos_logger.exception.call_args
        )

    def test_lambda_handler_returns_correct_content_type(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_dos_logger: MagicMock,
        healthcare_service_bundle: Bundle,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.return_value = (
            healthcare_service_bundle
        )
        event = _build_healthcare_service_event()

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        assert response["multiValueHeaders"]["Content-Type"] == [
            "application/fhir+json"
        ]

    def test_lambda_handler_with_null_query_params(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_dos_logger: MagicMock,
    ) -> None:
        # Arrange
        response_size = len(
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_dos_logger.get_response_size_and_duration.return_value = (
            response_size,
            1,
        )
        event = {
            "path": "/HealthcareService",
            "httpMethod": "GET",
            "queryStringParameters": None,
            "requestContext": {"requestId": "req-id"},
            "headers": {},
        }

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once()
        assert response["statusCode"] == 400
