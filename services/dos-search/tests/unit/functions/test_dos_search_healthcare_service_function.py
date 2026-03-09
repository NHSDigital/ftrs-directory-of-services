from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome

with patch("ftrs_common.feature_flags.FeatureFlagsClient") as mock_client_class:
    mock_client_class.return_value.is_enabled.return_value = True

    from ftrs_common.feature_flags import FeatureFlag

    from functions.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM
    from functions.dos_search_healthcare_service_function import (
        DEFAULT_RESPONSE_HEADERS,
        lambda_handler,
    )


@pytest.fixture
def mock_error_util():
    with patch("functions.dos_search_healthcare_service_function.error_util") as mock:
        mock_validation_error = OperationOutcome.model_construct(id="validation-error")
        mock_internal_error = OperationOutcome.model_construct(id="internal-error")
        mock_service_unavailable_error = OperationOutcome.model_construct(
            id="service-unavailable-error"
        )

        mock.create_validation_error_operation_outcome.return_value = (
            mock_validation_error
        )
        mock.create_resource_internal_server_error.return_value = mock_internal_error
        mock.create_resource_service_unavailable_error.return_value = (
            mock_service_unavailable_error
        )

        yield mock


@pytest.fixture
def mock_ftrs_service():
    with patch(
        "functions.dos_search_healthcare_service_function.HealthcareServicesByOdsService"
    ) as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def mock_logger():
    with patch("functions.dos_search_healthcare_service_function.logger") as mock:
        mock.get_response_size_and_duration.return_value = (100, 1)
        yield mock


@pytest.fixture
def lambda_context() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_feature_flags_client():
    with patch(
        "functions.dos_search_healthcare_service_function.FEATURE_FLAGS_CLIENT"
    ) as mock:
        mock.is_enabled.return_value = True
        yield mock


@pytest.fixture
def bundle() -> Bundle:
    return Bundle.model_construct(id="test-bundle", type="searchset")


EXPECTED_MULTI_VALUE_HEADERS = {
    header: [value] for header, value in DEFAULT_RESPONSE_HEADERS.items()
}


def _build_event(ods_code: str) -> dict:
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
        mock_logger: MagicMock,
        ods_code: str,
        bundle: Bundle,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.return_value = bundle
        event = _build_event(ods_code)

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.healthcare_services_by_ods.assert_called_once_with(ods_code)
        assert_response(
            response,
            expected_status_code=200,
            expected_body=bundle.model_dump_json(),
        )

    def test_lambda_handler_with_validation_error(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        # Arrange
        event = {
            "path": "/HealthcareService",
            "httpMethod": "GET",
            "queryStringParameters": {
                "identifier": "invalid|ABC",
            },
            "requestContext": {"requestId": "req-id"},
            "headers": {},
        }

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once()
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
        mock_logger: MagicMock,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.side_effect = Exception(
            "Unexpected error"
        )
        event = _build_event("ABC123")

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

    def test_lambda_handler_logs_request(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_logger: MagicMock,
        bundle: Bundle,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.return_value = bundle
        event = _build_event("ABC123")

        # Act
        lambda_handler(event, lambda_context)

        # Assert
        mock_logger.info.assert_any_call(
            "Received request for healthcare service",
            ods_code="ABC123",
            dos_message_category="REQUEST",
        )

    def test_lambda_handler_logs_internal_error(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_error_util: MagicMock,
        mock_logger: MagicMock,
    ) -> None:
        # Arrange
        mock_ftrs_service.healthcare_services_by_ods.side_effect = Exception(
            "Test error"
        )
        event = _build_event("ABC123")

        # Act
        lambda_handler(event, lambda_context)

        # Assert
        mock_logger.exception.assert_called_once()

    def test_lambda_handler_with_feature_flag_enabled(
        self,
        lambda_context: MagicMock,
        mock_ftrs_service: MagicMock,
        mock_logger: MagicMock,
        mock_feature_flags_client: MagicMock,
        bundle: Bundle,
    ) -> None:
        # Arrange
        mock_feature_flags_client.is_enabled.return_value = True
        mock_ftrs_service.healthcare_services_by_ods.return_value = bundle
        event = _build_event("ABC123")

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_feature_flags_client.is_enabled.assert_called_once_with(
            FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED
        )
        mock_logger.info.assert_any_call(
            "Healthcare Service search endpoint is enabled via feature flag",
            feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
            feature_flag_status="enabled",
            dos_message_category="FEATURE_FLAG",
        )
        assert response["statusCode"] == 200
        assert_response(
            response,
            expected_status_code=200,
            expected_body=bundle.model_dump_json(),
        )

    def test_lambda_handler_with_feature_flag_disabled(
        self,
        lambda_context: MagicMock,
        mock_error_util: MagicMock,
        mock_logger: MagicMock,
        mock_feature_flags_client: MagicMock,
    ) -> None:
        # Arrange
        mock_feature_flags_client.is_enabled.return_value = False
        event = _build_event("ABC123")

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_feature_flags_client.is_enabled.assert_called_once_with(
            FeatureFlag.DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED
        )
        mock_logger.warning.assert_called_with(
            "Service unavailable - Healthcare Service search endpoint is disabled via feature flag",
            feature_flag="DOS_SEARCH_HEALTHCARE_SERVICE_ENABLED",
            feature_flag_status="disabled",
            dos_message_category="FEATURE_FLAG",
            dos_response_time="0ms",
            dos_response_size=68,
        )
        mock_error_util.create_resource_service_unavailable_error.assert_called_once()
        assert response["statusCode"] == 503
        assert_response(
            response,
            expected_status_code=503,
            expected_body=mock_error_util.create_resource_service_unavailable_error.return_value.model_dump_json(),
        )
