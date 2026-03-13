from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.organization import Organization as FhirOrganization

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
def mock_organization_mapper():
    with patch("src.organization.service.OrganizationMapper") as mock_class:
        mock_mapper = mock_class.return_value
        mock_org = FhirOrganization.model_validate(
            {
                "id": "org-123",
                "identifier": [
                    {
                        "use": "official",
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "ABC123",
                    }
                ],
                "name": "Test Organization",
                "active": True,
            }
        )
        mock_mapper.map_to_fhir_organization.return_value = mock_org
        yield mock_mapper


@pytest.fixture
def mock_endpoint_mapper():
    with patch("src.organization.service.EndpointMapper") as mock_class:
        mock_mapper = mock_class.return_value
        mock_mapper.map_to_fhir_endpoints.return_value = []
        yield mock_mapper


@pytest.fixture
def organization_search_service(
    mock_repository: MagicMock,
    mock_bundle_mapper: MagicMock,
    mock_organization_mapper: MagicMock,
    mock_endpoint_mapper: MagicMock,
) -> OrganizationSearchService:
    return OrganizationSearchService()


class TestOrganizationSearchService:
    def test_init(
        self,
        mock_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
        mock_organization_mapper: MagicMock,
        mock_endpoint_mapper: MagicMock,
    ) -> None:
        # Act
        service = OrganizationSearchService()

        # Assert
        assert service.repository == mock_repository
        assert service.bundle_mapper == mock_bundle_mapper
        assert service.organization_mapper == mock_organization_mapper
        assert service.endpoint_mapper == mock_endpoint_mapper

    def test_endpoints_by_ods_success(
        self,
        organization_search_service: OrganizationSearchService,
        mock_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
        mock_organization_mapper: MagicMock,
        mock_endpoint_mapper: MagicMock,
        organisation,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value

        # Act
        result = organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_organization_mapper.map_to_fhir_organization.assert_called_once_with(
            organisation
        )
        mock_endpoint_mapper.map_to_fhir_endpoints.assert_called_once_with(organisation)
        mock_bundle_mapper.map_to_fhir.assert_called_once()
        assert result == expected_bundle

    def test_endpoints_by_ods_not_found(
        self,
        organization_search_service: OrganizationSearchService,
        mock_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
        mock_organization_mapper: MagicMock,
        mock_endpoint_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "UNKNOWN"
        expected_bundle = mock_bundle_mapper.map_to_fhir.return_value
        mock_repository.get_first_record_by_ods_code.return_value = None

        # Act
        result = organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_organization_mapper.map_to_fhir_organization.assert_not_called()
        mock_endpoint_mapper.map_to_fhir_endpoints.assert_not_called()
        mock_bundle_mapper.map_to_fhir.assert_called_once()
        # Resources list should be empty
        call_args = mock_bundle_mapper.map_to_fhir.call_args
        assert call_args[0][0] == []
        assert result == expected_bundle

    def test_endpoints_by_ods_repository_exception(
        self,
        organization_search_service: OrganizationSearchService,
        mock_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
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
        organization_search_service: OrganizationSearchService,
        mock_repository: MagicMock,
        mock_bundle_mapper: MagicMock,
        organisation,
    ) -> None:
        # Arrange
        ods_code = "ABC123"
        expected_exc = Exception("Mapper error")
        mock_bundle_mapper.map_to_fhir.side_effect = expected_exc

        # Act
        with pytest.raises(Exception, match=expected_exc.args[0]) as exc_info:
            organization_search_service.endpoints_by_ods(ods_code)

        # Assert
        mock_repository.get_first_record_by_ods_code.assert_called_once_with(ods_code)
        mock_bundle_mapper.map_to_fhir.assert_called_once()
        assert exc_info.value == expected_exc

    def test_create_resources_with_organisation(
        self,
        organization_search_service: OrganizationSearchService,
        mock_organization_mapper: MagicMock,
        mock_endpoint_mapper: MagicMock,
        organisation,
    ) -> None:
        # Act
        resources = organization_search_service._create_resources(organisation)

        # Assert
        mock_organization_mapper.map_to_fhir_organization.assert_called_once_with(
            organisation
        )
        mock_endpoint_mapper.map_to_fhir_endpoints.assert_called_once_with(organisation)
        assert len(resources) >= 1
        assert (
            resources[0]
            == mock_organization_mapper.map_to_fhir_organization.return_value
        )

    def test_create_resources_with_none(
        self,
        organization_search_service: OrganizationSearchService,
        mock_organization_mapper: MagicMock,
        mock_endpoint_mapper: MagicMock,
    ) -> None:
        # Act
        resources = organization_search_service._create_resources(None)

        # Assert
        mock_organization_mapper.map_to_fhir_organization.assert_not_called()
        mock_endpoint_mapper.map_to_fhir_endpoints.assert_not_called()
        assert resources == []

    @patch("src.organization.service.get_fhir_url")
    def test_build_self_url(self, mock_get_fhir_url: MagicMock) -> None:
        # Arrange
        mock_get_fhir_url.return_value = (
            "https://dos-search.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization"
        )
        ods_code = "ABC123"

        # Act
        url = OrganizationSearchService._build_self_url(ods_code)

        # Assert
        assert "Organization" in url
        assert ods_code in url
        assert "_revinclude=Endpoint:organization" in url
