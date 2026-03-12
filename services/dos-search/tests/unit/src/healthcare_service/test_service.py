from unittest.mock import ANY, MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)

from src.healthcare_service.service import (
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
        "src.healthcare_service.service.get_service_repository"
    ) as mock_get_repo:
        mock_org_repo = MagicMock()
        # First call returns org repo, second call returns healthcare service repo
        mock_get_repo.side_effect = [mock_org_repo, mock_healthcare_service_repository]
        yield mock_org_repo, mock_healthcare_service_repository


@pytest.fixture
def mock_bundle_mapper() -> MagicMock:
    with patch("src.healthcare_service.service.BundleMapper") as mock_class:
        mock_mapper = mock_class.return_value
        mock_bundle = Bundle.model_validate(
            {"resourceType": "Bundle", "type": "searchset", "id": "test-bundle"}
        )
        mock_mapper.map_to_fhir.return_value = mock_bundle
        yield mock_mapper


@pytest.fixture
def mock_healthcare_service_mapper() -> MagicMock:
    with patch("src.healthcare_service.service.HealthcareServiceMapper") as mock_class:
        mock_mapper = mock_class.return_value
        mock_fhir_hs = FhirHealthcareService.model_validate({"id": "hs-123"})
        mock_mapper.map_to_fhir_healthcare_service.return_value = mock_fhir_hs
        yield mock_mapper


@pytest.fixture
def ftrs_service(
    mock_organisation_repository: tuple,
    mock_bundle_mapper: MagicMock,
    mock_healthcare_service_mapper: MagicMock,
) -> HealthcareServicesByOdsService:
    return HealthcareServicesByOdsService()


class TestFtrsServiceHealthcareServices:
    def test_init(
        self,
        mock_organisation_repository: tuple,
        mock_bundle_mapper: MagicMock,
        mock_healthcare_service_mapper: MagicMock,
    ) -> None:
        # Act
        mock_org_repo, mock_hs_repo = mock_organisation_repository
        service = HealthcareServicesByOdsService()

        # Assert
        assert service.repository == mock_org_repo
        assert service.healthcare_service_repository == mock_hs_repo
        assert service.bundle_mapper == mock_bundle_mapper
        assert service.healthcare_service_mapper == mock_healthcare_service_mapper

    def test_healthcare_services_by_ods_success(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
        mock_healthcare_service_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        mock_healthcare_service = MagicMock()
        ftrs_service.repository.get_by_ods_code.return_value = [mock_organisation]
        mock_healthcare_service_repository.get_records_by_provided_by.return_value = [
            mock_healthcare_service
        ]
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service.repository.get_by_ods_code.assert_called_once_with(ods_code)
        mock_healthcare_service_repository.get_records_by_provided_by.assert_called_once_with(
            str(mock_organisation.id)
        )
        mock_healthcare_service_mapper.map_to_fhir_healthcare_service.assert_called_once_with(
            mock_healthcare_service
        )
        mock_bundle_mapper.map_to_fhir.assert_called_once()
        assert result == expected_bundle

    def test_healthcare_services_by_ods_no_organisation_found(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "UNKNOWN"
        ftrs_service.repository.get_by_ods_code.return_value = []
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service.repository.get_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with([], ANY)
        assert result == expected_bundle

    def test_healthcare_services_by_ods_no_healthcare_services_found(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        ftrs_service.repository.get_by_ods_code.return_value = [mock_organisation]
        mock_healthcare_service_repository.get_records_by_provided_by.return_value = []
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        mock_bundle_mapper.map_to_fhir.assert_called_once_with([], ANY)
        assert result == expected_bundle

    def test_healthcare_services_by_ods_multiple_organisations(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
        mock_healthcare_service_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        mock_org_2 = MagicMock()
        mock_org_2.id = "org-456"
        mock_healthcare_service_1 = MagicMock()
        mock_healthcare_service_2 = MagicMock()
        mock_fhir_hs_1 = FhirHealthcareService.model_validate({"id": "hs-1"})
        mock_fhir_hs_2 = FhirHealthcareService.model_validate({"id": "hs-2"})

        ftrs_service.repository.get_by_ods_code.return_value = [
            mock_organisation,
            mock_org_2,
        ]
        mock_healthcare_service_repository.get_records_by_provided_by.side_effect = [
            [mock_healthcare_service_1],
            [mock_healthcare_service_2],
        ]
        mock_healthcare_service_mapper.map_to_fhir_healthcare_service.side_effect = [
            mock_fhir_hs_1,
            mock_fhir_hs_2,
        ]

        # Act
        result = ftrs_service.healthcare_services_by_ods(ods_code)

        # Assert
        assert (
            mock_healthcare_service_repository.get_records_by_provided_by.call_count
            == 2
        )
        assert (
            mock_healthcare_service_mapper.map_to_fhir_healthcare_service.call_count
            == 2
        )
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(
            [mock_fhir_hs_1, mock_fhir_hs_2],
            ANY,
        )
        assert isinstance(result, Bundle)

    def test_healthcare_services_by_ods_repository_exception(
        self,
        ftrs_service: HealthcareServicesByOdsService,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Repository error")
        ftrs_service.repository.get_by_ods_code.side_effect = expected_exc

        # Act & Assert
        with pytest.raises(Exception, match="Repository error") as exc_info:
            ftrs_service.healthcare_services_by_ods(ods_code)

        assert exc_info.value == expected_exc

    def test_healthcare_services_by_ods_healthcare_repo_exception(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Healthcare repo error")
        ftrs_service.repository.get_by_ods_code.return_value = [mock_organisation]
        mock_healthcare_service_repository.get_records_by_provided_by.side_effect = (
            expected_exc
        )

        # Act & Assert
        with pytest.raises(Exception, match="Healthcare repo error") as exc_info:
            ftrs_service.healthcare_services_by_ods(ods_code)

        assert exc_info.value == expected_exc

    def test_healthcare_services_by_ods_mapper_exception(
        self,
        ftrs_service: HealthcareServicesByOdsService,
        mock_organisation: MagicMock,
        mock_healthcare_service_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Mapper error")
        ftrs_service.repository.get_by_ods_code.return_value = [mock_organisation]
        mock_healthcare_service_repository.get_records_by_provided_by.return_value = []
        mock_bundle_mapper.map_to_fhir.side_effect = expected_exc

        # Act & Assert
        with pytest.raises(Exception, match="Mapper error") as exc_info:
            ftrs_service.healthcare_services_by_ods(ods_code)

        assert exc_info.value == expected_exc
