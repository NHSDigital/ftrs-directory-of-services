from unittest.mock import ANY, MagicMock, call, patch

import pytest
from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from src.common.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)
from src.common.logbase import DosSearchLogBase
from src.organization.handler import (
    DEFAULT_RESPONSE_HEADERS,
    lambda_handler,
)


@pytest.fixture
def mock_error_util():
    with patch("src.organization.handler.error_util") as mock:
        mock_validation_error = OperationOutcome.model_construct(id="validation-error")
        mock_internal_error = OperationOutcome.model_construct(id="internal-error")
        mock_invalid_header = OperationOutcome.model_construct(id="invalid-header")
        mock_invalid_version_header = OperationOutcome.model_construct(
            id="invalid-version-header"
        )
        mock_missing_mandatory_header = OperationOutcome.model_construct(
            id="missing-mandatory-header"
        )

        mock.create_validation_error_operation_outcome.return_value = (
            mock_validation_error
        )
        mock.create_resource_internal_server_error.return_value = mock_internal_error
        mock.create_invalid_header_operation_outcome.return_value = mock_invalid_header
        mock.create_invalid_version_operation_outcome.return_value = (
            mock_invalid_version_header
        )
        mock.create_missing_mandatory_header_operation_outcome.return_value = (
            mock_missing_mandatory_header
        )

        yield mock


@pytest.fixture
def mock_organization_search_service():
    with patch("src.organization.handler.OrganizationSearchService") as mock_class:
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
            "identifier": f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123",
            "_revinclude": REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
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


class TestOrganizationLambdaHandler:
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
        mock_organization_search_service,
        mock_setup_request,
        mock_get_response_size_and_duration,
        mock_logger,
        ods_code,
        event,
        bundle,
    ):
        # Arrange
        mock_organization_search_service.endpoints_by_ods.return_value = bundle

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_organization_search_service.endpoints_by_ods.assert_called_once_with(
            ods_code
        )

        mock_setup_request.assert_called_once_with(ANY, ANY)
        mock_get_response_size_and_duration.assert_called_once_with(bundle, ANY, ANY)

        mock_logger.assert_has_calls(
            [
                call.log(
                    DosSearchLogBase.DOS_SEARCH_002,
                    ods_code=ods_code,
                    dos_message_category="REQUEST",
                ),
                call.log(
                    DosSearchLogBase.DOS_SEARCH_003,
                    dos_response_time=ANY,
                    dos_response_size=len(bundle.model_dump_json().encode("utf-8")),
                    dos_message_category="METRICS",
                ),
                call.log(
                    DosSearchLogBase.DOS_SEARCH_004,
                    status_code=200,
                    body=ANY,
                    dos_message_category="RESPONSE",
                ),
            ]
        )

        assert_response(
            response, expected_status_code=200, expected_body=bundle.model_dump_json()
        )

    @pytest.mark.parametrize(
        "model_to_throw_validation_error",
        [
            "OrganizationHeaders",
            "OrganizationQueryParams",
        ],
    )
    def test_lambda_handler_with_request_validation_error(
        self,
        lambda_context,
        mock_error_util,
        mock_setup_request,
        mock_get_response_size_and_duration,
        mock_logger,
        event,
        model_to_throw_validation_error,
    ):
        # Arrange
        validation_error = ValidationError.from_exception_data("ValidationError", [])
        response_size = len(  # Override mocked response size to use this case's error model
            mock_error_util.create_validation_error_operation_outcome.return_value.model_dump_json().encode(
                "utf-8"
            )
        )
        mock_get_response_size_and_duration.return_value = (response_size, 1)

        # Act
        with patch(
            f"src.organization.handler.{model_to_throw_validation_error}.model_validate",
            side_effect=validation_error,
        ):
            response = lambda_handler(event, lambda_context)

        # Assert
        mock_error_util.create_validation_error_operation_outcome.assert_called_once_with(
            validation_error
        )

        mock_setup_request.assert_called_once_with(ANY, ANY)
        mock_get_response_size_and_duration.assert_called_once_with(
            mock_error_util.create_validation_error_operation_outcome.return_value,
            ANY,
            ANY,
        )

        mock_logger.assert_has_calls(
            [
                call.log(
                    DosSearchLogBase.DOS_SEARCH_005,
                    validation_errors=validation_error.errors(),
                    dos_response_time="1ms",
                    dos_response_size=response_size,
                ),
                call.log(
                    DosSearchLogBase.DOS_SEARCH_004,
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

    @pytest.mark.parametrize(
        "exception",
        [
            Exception("Unexpected error"),
            ValidationError.from_exception_data("ValidationError", []),
        ],
        ids=["general_exception", "validation_error"],
    )
    def test_lambda_handler_with_exception_from_organization_search_service_endpoints_by_ods(
        self,
        lambda_context,
        mock_organization_search_service,
        event,
        ods_code,
        mock_error_util,
        mock_setup_request,
        mock_get_response_size_and_duration,
        mock_logger,
        bundle,
        exception,
    ):
        # Arrange
        mock_organization_search_service.endpoints_by_ods.side_effect = exception

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_organization_search_service.endpoints_by_ods.assert_called_once_with(
            ods_code
        )
        mock_error_util.create_resource_internal_server_error.assert_called_once()

        mock_setup_request.assert_called_once_with(ANY, ANY)
        mock_get_response_size_and_duration.assert_called_once_with(
            mock_error_util.create_resource_internal_server_error.return_value,
            ANY,
            ANY,
        )

        mock_logger.assert_has_calls(
            [
                call.log(
                    DosSearchLogBase.DOS_SEARCH_002,
                    ods_code=ods_code,
                    dos_message_category="REQUEST",
                ),
                call.log(
                    DosSearchLogBase.DOS_SEARCH_006,
                    dos_response_time="1ms",
                    dos_response_size=len(bundle.model_dump_json().encode("utf-8")),
                ),
                call.log(
                    DosSearchLogBase.DOS_SEARCH_004,
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
