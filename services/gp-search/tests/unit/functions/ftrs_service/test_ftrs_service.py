from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.operationoutcome import OperationOutcome

from functions.ftrs_service.ftrs_service import FtrsService


@pytest.fixture
def mock_config():
    with patch("functions.ftrs_service.ftrs_service.get_config") as mock:
        mock.return_value = {
            "DYNAMODB_TABLE_NAME": "test-table",
            "FHIR_BASE_URL": "https://test-base-url.org",
        }
        yield mock


@pytest.fixture
def mock_repository(organization_record):
    with patch("functions.ftrs_service.ftrs_service.DynamoRepository") as mock_class:
        mock_repo = mock_class.return_value
        mock_repo.get_first_record_by_ods_code.return_value = organization_record
        yield mock_repo


@pytest.fixture
def mock_bundle_mapper():
    with patch("functions.ftrs_service.ftrs_service.BundleMapper") as mock_class:
        mock_mapper = mock_class.return_value
        mock_bundle = Bundle.model_validate(
            {"resourceType": "Bundle", "type": "searchset", "id": "test-bundle"}
        )
        mock_mapper.map_to_fhir.return_value = mock_bundle
        yield mock_mapper


@pytest.fixture
def ftrs_service(mock_config, mock_repository, mock_bundle_mapper):
    return FtrsService()


class TestFtrsService:
    def test_init(self, mock_config, mock_repository, mock_bundle_mapper):
        # Act
        service = FtrsService()

        # Assert
        assert service.repository == mock_repository
        assert service.mapper == mock_bundle_mapper

    def test_endpoints_by_ods_success(
        self, ftrs_service, mock_repository, mock_bundle_mapper, organization_record
    ):
        # Arrange
        ods_code = "O123"
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(
            organization_record, ods_code
        )
        assert result == expected_bundle

    def test_endpoints_by_ods_not_found(
        self, ftrs_service, mock_repository, mock_bundle_mapper
    ):
        # Arrange
        ods_code = "UNKNOWN"
        organization_record = None
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value
        mock_repository.get_first_record_by_ods_code.return_value = None

        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(
            organization_record, ods_code
        )
        assert result == expected_bundle

    def test_endpoints_by_ods_exception(
        self, ftrs_service, mock_repository, mock_bundle_mapper
    ):
        # Arrange
        ods_code = "O123"
        mock_repository.get_first_record_by_ods_code.side_effect = Exception(
            "Test exception"
        )

        # Create a mock OperationOutcome for the error
        error_outcome = OperationOutcome.model_validate(
            {
                "id": "internal-server-error",
                "issue": [
                    {
                        "severity": "error",
                        "code": "internal",
                        "details": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                                    "code": "INTERNAL_SERVER_ERROR",
                                    "display": f"Internal server error while processing ODS code '{ods_code}'",
                                },
                            ]
                        },
                    }
                ],
            }
        )

        # Patch the _create_error_resource method to return our mock
        with patch.object(
            ftrs_service, "_create_error_resource", return_value=error_outcome
        ):
            # Act
            result = ftrs_service.endpoints_by_ods(ods_code)

            # Assert
            mock_repository.get_first_record_by_ods_code.assert_called_once_with(
                ods_code
            )
            mock_bundle_mapper.map_to_fhir.assert_not_called()
            assert isinstance(result, OperationOutcome)
            assert result.issue[0].severity == "error"
            assert result.issue[0].code == "internal"

    def test_endpoints_by_ods_mapping_exception(
        self, ftrs_service, mock_repository, mock_bundle_mapper, organization_record
    ):
        # Arrange
        ods_code = "O123"
        mock_bundle_mapper.map_to_fhir.side_effect = Exception("Mapping error")

        # Create a mock OperationOutcome for the error
        error_outcome = OperationOutcome.model_validate(
            {
                "id": "internal-server-error",
                "issue": [
                    {
                        "severity": "error",
                        "code": "internal",
                        "details": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/operation-outcome",
                                    "code": "INTERNAL_SERVER_ERROR",
                                    "display": f"Internal server error while processing ODS code '{ods_code}'",
                                },
                            ]
                        },
                    }
                ],
            }
        )

        # Patch the _create_error_resource method to return our mock
        with patch.object(
            ftrs_service, "_create_error_resource", return_value=error_outcome
        ):
            # Act
            result = ftrs_service.endpoints_by_ods(ods_code)

            # Assert
            mock_repository.get_first_record_by_ods_code.assert_called_once_with(
                ods_code
            )
            mock_bundle_mapper.map_to_fhir.assert_called_once_with(
                organization_record, ods_code
            )
            assert isinstance(result, OperationOutcome)

    def test_create_error_resource(self, ftrs_service):
        # Arrange
        ods_code = "TEST123"

        # Act
        result = ftrs_service._create_error_resource(ods_code)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert result.id == "internal-server-error"
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "internal"
        assert hasattr(result.issue[0], "details")
        assert hasattr(result.issue[0].details, "coding")
        assert len(result.issue[0].details.coding) > 0
        assert result.issue[0].details.coding[0].code == "INTERNAL_SERVER_ERROR"
        assert ods_code in result.issue[0].details.coding[0].display
