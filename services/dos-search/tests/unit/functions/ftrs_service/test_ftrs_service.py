from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle

from functions.ftrs_service.ftrs_service import FtrsService


@pytest.fixture
def mock_repository(organisation):
    with patch("functions.ftrs_service.ftrs_service.get_service_repository") as mock:
        mock_repo = mock.return_value
        mock_repo.get_first_record_by_ods_code.return_value = organisation
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
def mock_healthcare_service_bundle_mapper():
    with patch(
        "functions.ftrs_service.ftrs_service.HealthcareServiceBundleMapper"
    ) as mock_mapper_class:
        mock_mapper = mock_mapper_class.return_value
        mock_mapper.map_to_fhir.return_value = Bundle.model_construct(
            id="healthcare-service-bundle"
        )
        yield mock_mapper


@pytest.fixture
def ftrs_service_with_healthcare(
    mock_repository,
    mock_bundle_mapper,
    mock_healthcare_service_bundle_mapper,
):
    with patch(
        "functions.ftrs_service.ftrs_service.get_service_repository"
    ) as mock_get_repo:
        mock_healthcare_repo = MagicMock()
        mock_get_repo.side_effect = [mock_repository, mock_healthcare_repo]
        service = FtrsService()
        service.repository = mock_repository
        service.healthcare_service_repository = mock_healthcare_repo
        service.mapper = mock_bundle_mapper
        service.healthcare_service_mapper = mock_healthcare_service_bundle_mapper
        yield service


@pytest.fixture
def ftrs_service(mock_repository, mock_bundle_mapper):
    return FtrsService()


class TestFtrsService:
    def test_init(self, mock_repository, mock_bundle_mapper):
        # Act
        service = FtrsService()

        # Assert
        assert service.repository == mock_repository
        assert service.mapper == mock_bundle_mapper

    def test_endpoints_by_ods_success(
        self, ftrs_service, mock_repository, mock_bundle_mapper, organisation
    ):
        # Arrange
        ods_code = "O123"
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organisation, ods_code)
        assert result == expected_bundle

    def test_endpoints_by_ods_not_found(
        self, ftrs_service, mock_repository, mock_bundle_mapper
    ):
        # Arrange
        ods_code = "UNKNOWN"
        organisation = None
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value
        mock_repository.get_first_record_by_ods_code.return_value = None

        # Act
        result = ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organisation, ods_code)
        assert result == expected_bundle

    def test_endpoints_by_ods_repository_exception(
        self, ftrs_service, mock_repository, mock_bundle_mapper
    ):
        # Arrange
        ods_code = "O123"
        expected_exc = Exception("Repository error")
        mock_repository.get_first_record_by_ods_code.side_effect = expected_exc

        # Act
        with pytest.raises(Exception, match=expected_exc.args[0]) as exc_info:
            ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_not_called()
        assert exc_info.value == expected_exc

    def test_endpoints_by_ods_mapper_exception(
        self, ftrs_service, mock_repository, mock_bundle_mapper, organisation
    ):
        # Arrange
        ods_code = "O123"
        expected_exc = Exception("Mapper error")
        mock_bundle_mapper.map_to_fhir.side_effect = expected_exc

        # Act
        with pytest.raises(Exception, match=expected_exc.args[0]) as exc_info:
            ftrs_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organisation, ods_code)
        assert exc_info.value == expected_exc


class TestFtrsServiceHealthcareServices:
    def test_healthcare_services_by_ods_success(
        self,
        ftrs_service_with_healthcare: FtrsService,
        organisation: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        mock_healthcare_services = [MagicMock(), MagicMock()]
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.return_value = [
            organisation
        ]
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.return_value = mock_healthcare_services
        expected_bundle = ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.assert_called_once_with(
            ods_code
        )
        ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.assert_called_once()
        assert result == expected_bundle

    def test_healthcare_services_by_ods_no_organisation_found(
        self,
        ftrs_service_with_healthcare: FtrsService,
    ) -> None:
        # Arrange
        ods_code = "NOTFOUND"
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.return_value = []
        expected_bundle = ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.assert_called_once_with(
            ods_code
        )
        ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.assert_called_once_with(
            [], ods_code
        )
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.assert_not_called()
        assert result == expected_bundle

    def test_healthcare_services_by_ods_no_healthcare_services_found(
        self,
        ftrs_service_with_healthcare: FtrsService,
        organisation: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.return_value = [
            organisation
        ]
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.return_value = []
        expected_bundle = ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.return_value

        # Act
        result = ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.assert_called_once()
        assert result == expected_bundle

    def test_healthcare_services_by_ods_multiple_organisations(
        self,
        ftrs_service_with_healthcare: FtrsService,
        organisation: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        org1 = MagicMock()
        org1.id = "org-1"
        org2 = MagicMock()
        org2.id = "org-2"
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.return_value = [
            org1,
            org2,
        ]

        mock_hs_1 = MagicMock()
        mock_hs_2 = MagicMock()
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.side_effect = [
            [mock_hs_1],
            [mock_hs_2],
        ]

        # Act
        ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)

        # Assert
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.assert_called_once_with(
            ods_code
        )
        assert (
            ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.call_count
            == 2
        )
        ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.assert_called_once()

    def test_healthcare_services_by_ods_repository_exception(
        self,
        ftrs_service_with_healthcare: FtrsService,
    ) -> None:
        # Arrange
        ods_code = "O123"
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.side_effect = (
            Exception("Database error")
        )

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)

        ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.assert_not_called()

    def test_healthcare_services_by_ods_healthcare_repo_exception(
        self,
        ftrs_service_with_healthcare: FtrsService,
        organisation: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.return_value = [
            organisation
        ]
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.side_effect = Exception(
            "Healthcare service database error"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Healthcare service database error"):
            ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)

        ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.assert_not_called()

    def test_healthcare_services_by_ods_mapper_exception(
        self,
        ftrs_service_with_healthcare: FtrsService,
        organisation: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        ftrs_service_with_healthcare.repository._get_records_by_ods_code.return_value = [
            organisation
        ]
        ftrs_service_with_healthcare.healthcare_service_repository.get_records_by_provided_by.return_value = []
        ftrs_service_with_healthcare.healthcare_service_mapper.map_to_fhir.side_effect = Exception(
            "Mapping error"
        )

        # Act & Assert
        with pytest.raises(Exception, match="Mapping error"):
            ftrs_service_with_healthcare.healthcare_services_by_ods(ods_code)
