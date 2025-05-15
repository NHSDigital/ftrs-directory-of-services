from unittest.mock import MagicMock, patch

import pytest
from pytest_lazy_fixtures import lf

from functions.gp_search_function import lambda_handler


@pytest.fixture
def mock_ftrs_service():
    with patch("functions.gp_search_function.FtrsService") as mock_class:
        mock_service = mock_class.return_value
        yield mock_service


@pytest.fixture
def event():
    return {"odsCode": "O123"}


@pytest.fixture
def lambda_context():
    return MagicMock()


@pytest.fixture
def mock_bundle():
    mock_bundle = MagicMock()
    mock_bundle.get_resource_type.return_value = "Bundle"
    mock_bundle.model_dump_json.return_value = (
        '{"resourceType": "Bundle", "id": "test-id"}'
    )
    return mock_bundle


@pytest.fixture
def mock_operation_outcome():
    mock_operation_outcome = MagicMock()
    mock_operation_outcome.get_resource_type.return_value = "OperationOutcome"
    mock_operation_outcome.model_dump_json.return_value = (
        '{"resourceType": "OperationOutcome", "id": "error-id"}'
    )

    return mock_operation_outcome


class TestLambdaHandler:
    @pytest.mark.parametrize(
        ("mock_fhir_resource", "expected_status_code"),
        [
            (lf("mock_bundle"), 200),
            (lf("mock_operation_outcome"), 500),
        ],
    )
    def test_lambda_handler(
        self,
        lambda_context,
        mock_ftrs_service,
        event,
        mock_fhir_resource,
        expected_status_code,
    ):
        # Arrange
        mock_ftrs_service.endpoints_by_ods.return_value = mock_fhir_resource

        # Act
        response = lambda_handler(event, lambda_context)

        # Assert
        mock_ftrs_service.endpoints_by_ods.assert_called_once_with(event["odsCode"])
        mock_fhir_resource.get_resource_type.assert_called_once()
        mock_fhir_resource.model_dump_json.assert_called_once()

        assert response["statusCode"] == expected_status_code
        assert response["headers"] == {"Content-Type": "application/fhir+json"}
        assert response["body"] == mock_fhir_resource.model_dump_json.return_value
