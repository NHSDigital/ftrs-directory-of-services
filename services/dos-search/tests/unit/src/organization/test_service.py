from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle

from src.organization.service import OrganizationSearchService


@pytest.fixture
def mock_repository(organisation):
    with patch("src.organization.service.get_service_repository") as mock:
        mock_repo = mock.return_value
        mock_repo.get_first_record_by_ods_code.return_value = organisation
        yield mock_repo


@pytest.fixture
def mock_bundle_mapper():
    with patch("src.organization.service.BundleMapper") as mock_class:
        mock_mapper = mock_class.return_value
        mock_bundle = Bundle.model_validate(
            {"resourceType": "Bundle", "type": "searchset", "id": "test-bundle"}
        )
        mock_mapper.map_to_fhir.return_value = mock_bundle
        yield mock_mapper


@pytest.fixture
def organization_search_service(mock_repository, mock_bundle_mapper):
    return OrganizationSearchService()


class TestOrganizationSearchService:
    def test_init(self, mock_repository, mock_bundle_mapper):
        # Act
        service = OrganizationSearchService()

        # Assert
        assert service.repository == mock_repository
        assert service.mapper == mock_bundle_mapper

    def test_endpoints_by_ods_success(
        self,
        organization_search_service,
        mock_repository,
        mock_bundle_mapper,
        organisation,
    ):
        # Arrange
        ods_code = "O123"
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organisation, ods_code)
        assert result == expected_bundle

    def test_endpoints_by_ods_not_found(
        self, organization_search_service, mock_repository, mock_bundle_mapper
    ):
        # Arrange
        ods_code = "UNKNOWN"
        organisation = None
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value
        mock_repository.get_first_record_by_ods_code.return_value = None

        # Act
        result = organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organisation, ods_code)
        assert result == expected_bundle

    def test_endpoints_by_ods_repository_exception(
        self, organization_search_service, mock_repository, mock_bundle_mapper
    ):
        # Arrange
        ods_code = "O123"
        expected_exc = Exception("Repository error")
        mock_repository.get_first_record_by_ods_code.side_effect = expected_exc

        # Act
        with pytest.raises(Exception, match=expected_exc.args[0]) as exc_info:
            organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_not_called()
        assert exc_info.value == expected_exc

    def test_endpoints_by_ods_mapper_exception(
        self,
        organization_search_service,
        mock_repository,
        mock_bundle_mapper,
        organisation,
    ):
        # Arrange
        ods_code = "O123"
        expected_exc = Exception("Mapper error")
        mock_bundle_mapper.map_to_fhir.side_effect = expected_exc

        # Act
        with pytest.raises(Exception, match=expected_exc.args[0]) as exc_info:
            organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once_with(organisation, ods_code)
        assert exc_info.value == expected_exc
