from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle

from functions.ftrs_service.healthcare_services_by_ods import (
    HealthcareServicesByOdsService,
)


@pytest.fixture
def mock_organisation() -> MagicMock:
    mock = MagicMock()
    mock.id = "org-123"
    return mock


@pytest.fixture
def mock_healthcare_service_repository() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_organisation_repository(mock_healthcare_service_repository: MagicMock):
    with patch(
        "functions.ftrs_service.healthcare_services_by_ods.get_service_repository"
    ) as mock_get_repo:
        mock_org_repo = MagicMock()
        # First call returns org repo, second call returns healthcare service repo
        mock_get_repo.side_effect = [mock_org_repo, mock_healthcare_service_repository]
        yield mock_org_repo, mock_healthcare_service_repository


@pytest.fixture
def mock_healthcare_service_bundle_mapper():
    with patch(
        "functions.ftrs_service.healthcare_services_by_ods.HealthcareServiceBundleMapper"
    ) as mock_mapper_class:
        mock_mapper = mock_mapper_class.return_value
        mock_bundle = Bundle.model_validate(
            {"resourceType": "Bundle", "type": "searchset", "id": "test-bundle"}
        )
        mock_mapper.map_to_fhir.return_value = mock_bundle
        yield mock_mapper


@pytest.fixture
def ftrs_service(
    mock_organisation_repository: tuple,
    mock_healthcare_service_bundle_mapper: MagicMock,
) -> HealthcareServicesByOdsService:
    service = HealthcareServicesByOdsService()
    return service


class TestFtrsServiceHealthcareServices:
    def test_healthcare_services_by_ods_success(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_healthcare_service_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        mock_healthcare_service = MagicMock()
        ftrs_service.repository._get_records_by_ods_code.return_value = [
            mock_organisation
        ]
        mock_healthcare_service_repository.get_records_by_provided_by.return_value = [
            mock_healthcare_service
        ]

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service.repository._get_records_by_ods_code.assert_called_once_with(
            ods_code
        )
        mock_healthcare_service_repository.get_records_by_provided_by.assert_called_once_with(
            str(mock_organisation.id)
        )
        mock_healthcare_service_bundle_mapper.map_to_fhir.assert_called_once_with(
            [mock_healthcare_service], ods_code
        )
        assert isinstance(result, Bundle)

    def test_healthcare_services_by_ods_no_organisation_found(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_healthcare_service_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "UNKNOWN"
        ftrs_service.repository._get_records_by_ods_code.return_value = []

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service.repository._get_records_by_ods_code.assert_called_once_with(
            ods_code
        )
        mock_healthcare_service_bundle_mapper.map_to_fhir.assert_called_once_with(
            [], ods_code
        )
        assert isinstance(result, Bundle)

    def test_healthcare_services_by_ods_no_healthcare_services_found(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_healthcare_service_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        ftrs_service.repository._get_records_by_ods_code.return_value = [
            mock_organisation
        ]
        mock_healthcare_service_repository.get_records_by_provided_by.return_value = []

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        mock_healthcare_service_bundle_mapper.map_to_fhir.assert_called_once_with(
            [], ods_code
        )
        assert isinstance(result, Bundle)

    def test_healthcare_services_by_ods_multiple_organisations(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_healthcare_service_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        mock_org_2 = MagicMock()
        mock_org_2.id = "org-456"
        mock_healthcare_service_1 = MagicMock()
        mock_healthcare_service_2 = MagicMock()

        ftrs_service.repository._get_records_by_ods_code.return_value = [
            mock_organisation,
            mock_org_2,
        ]
        mock_healthcare_service_repository.get_records_by_provided_by.side_effect = [
            [mock_healthcare_service_1],
            [mock_healthcare_service_2],
        ]

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        assert (
            mock_healthcare_service_repository.get_records_by_provided_by.call_count
            == 2
        )
        mock_healthcare_service_bundle_mapper.map_to_fhir.assert_called_once_with(
            [mock_healthcare_service_1, mock_healthcare_service_2], ods_code
        )
        assert isinstance(result, Bundle)

    def test_healthcare_services_by_ods_repository_exception(
        self,
        ftrs_service: HealthcareServicesByOdsService,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Repository error")
        ftrs_service.repository._get_records_by_ods_code.side_effect = expected_exc

        # Act & Assert
        with pytest.raises(Exception, match="Repository error"):
            ftrs_service.healthcare_services_by_ods(ods_code)

    def test_healthcare_services_by_ods_healthcare_repo_exception(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Healthcare repo error")
        ftrs_service.repository._get_records_by_ods_code.return_value = [
            mock_organisation
        ]
        mock_healthcare_service_repository.get_records_by_provided_by.side_effect = (
            expected_exc
        )

        # Act & Assert
        with pytest.raises(Exception, match="Healthcare repo error"):
            ftrs_service.healthcare_services_by_ods(ods_code)

    def test_healthcare_services_by_ods_mapper_exception(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_healthcare_service_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Mapper error")
        ftrs_service.repository._get_records_by_ods_code.return_value = [
            mock_organisation
        ]
        mock_healthcare_service_repository.get_records_by_provided_by.return_value = []
        mock_healthcare_service_bundle_mapper.map_to_fhir.side_effect = expected_exc

        # Act & Assert
        with pytest.raises(Exception, match="Mapper error"):
            ftrs_service.healthcare_services_by_ods(ods_code)
