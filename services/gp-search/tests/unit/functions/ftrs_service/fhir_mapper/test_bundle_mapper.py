from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.organization import Organization as FhirOrganization

from functions.ftrs_service.fhir_mapper.bundle_mapper import BundleMapper


@pytest.fixture
def bundle_mapper():
    return BundleMapper()


@pytest.fixture
def mock_get_fhir_url():
    with patch("functions.ftrs_service.fhir_mapper.bundle_mapper.get_fhir_url") as mock:
        yield mock


class TestBundleMapper:
    def test_map_to_fhir_with_no_endpoints(self, bundle_mapper, create_organisation):
        # Arrange - Create a new organization record with no endpoints instead of modifying the existing one
        org_value = create_organisation(endpoints=[])
        ods_code = "O123"

        # Create mock organization resource
        org_resource = FhirOrganization.model_validate(
            {
                "id": "org-123",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "O123",
                    }
                ],
                "name": "Test Organization",
                "active": True,
            }
        )

        # Mock the mapper methods
        with patch.object(
            bundle_mapper.organization_mapper,
            "map_to_fhir_organization",
            return_value=org_resource,
        ) as mock_org_mapper:
            with patch.object(
                bundle_mapper.endpoint_mapper, "map_to_fhir_endpoints", return_value=[]
            ) as mock_endpoint_mapper:
                # Act
                bundle = bundle_mapper.map_to_fhir(org_value, ods_code)

                # Assert
                mock_org_mapper.assert_called_once_with(org_value)
                mock_endpoint_mapper.assert_called_once_with(org_value)
                assert isinstance(bundle, Bundle)
                assert bundle.type == "searchset"
                assert len(bundle.entry) == 1  # Only organization, no endpoints
                assert bundle.entry[0].resource == org_resource

    def test_map_to_fhir_with_multiple_endpoints(
        self, bundle_mapper, organisation, create_fhir_endpoint
    ):
        # Arrange
        ods_code = "O123"

        # Create two mock endpoint resources
        endpoint1 = create_fhir_endpoint()
        endpoint2 = create_fhir_endpoint()

        # Create mock organization resource
        org_resource = FhirOrganization.model_validate(
            {
                "id": "org-123",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "O123",
                    }
                ],
                "name": "Test Organization",
                "active": True,
            }
        )

        # Mock the mapper methods
        with patch.object(
            bundle_mapper.organization_mapper,
            "map_to_fhir_organization",
            return_value=org_resource,
        ) as mock_org_mapper:
            with patch.object(
                bundle_mapper.endpoint_mapper,
                "map_to_fhir_endpoints",
                return_value=[endpoint1, endpoint2],
            ) as mock_endpoint_mapper:
                # Act
                bundle = bundle_mapper.map_to_fhir(organisation, ods_code)

                # Assert
                mock_org_mapper.assert_called_once_with(organisation)
                mock_endpoint_mapper.assert_called_once_with(organisation)
                assert isinstance(bundle, Bundle)
                assert bundle.type == "searchset"
                assert len(bundle.entry) == 3  # 1 organization + 2 endpoints
                assert bundle.entry[0].resource == org_resource
                assert bundle.entry[1].resource == endpoint1
                assert bundle.entry[2].resource == endpoint2

    def test_create_entry_for_endpoint(
        self, bundle_mapper, create_fhir_endpoint, mock_get_fhir_url
    ):
        # Arrange
        endpoint_resource = create_fhir_endpoint()
        mock_get_fhir_url.return_value = (
            "https://example.org/FHIR/R4/Endpoint/endpoint-123"
        )

        # Act
        entry = bundle_mapper._create_entry(endpoint_resource)

        # Assert
        assert entry["fullUrl"] == "https://example.org/FHIR/R4/Endpoint/endpoint-123"
        assert entry["resource"] == endpoint_resource
        assert entry["search"]["mode"] == "include"

    def test_create_entry_for_organization(
        self, bundle_mapper, create_fhir_organization, mock_get_fhir_url
    ):
        # Arrange
        organization_resource = create_fhir_organization()
        mock_get_fhir_url.return_value = "https://servicesearch.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000"  # gitleaks:allow

        # Act
        entry = bundle_mapper._create_entry(organization_resource)

        # Assert
        assert (
            entry["fullUrl"]
            == "https://servicesearch.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000"  # gitleaks:allow
        )
        assert entry["resource"] == organization_resource
        assert entry["search"]["mode"] == "match"

    def test_get_search_mode(
        self, bundle_mapper, create_fhir_endpoint, create_fhir_organization
    ):
        # Arrange
        endpoint_resource = create_fhir_endpoint()
        org_resource = create_fhir_organization()

        # Act & Assert
        # Check that Organizations get 'match' mode
        search_mode = bundle_mapper._get_search_mode(org_resource)
        assert search_mode == "match"

        # Check that other resources get 'include' mode
        search_mode = bundle_mapper._get_search_mode(endpoint_resource)
        assert search_mode == "include"

    def test_map_to_fhir_with_no_organisation(self, bundle_mapper):
        # Arrange
        ods_code = "O123"

        # Act
        bundle = bundle_mapper.map_to_fhir(None, ods_code)

        # Assert
        assert isinstance(bundle, Bundle)
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 0  # Empty bundle
        assert len(bundle.link) == 1
        assert bundle.link[0].relation == "self"
        assert ods_code in bundle.link[0].url

    def test_create_resources(
        self,
        bundle_mapper,
        organisation,
        create_fhir_endpoint,
        create_fhir_organization,
    ):
        # Arrange
        endpoint = create_fhir_endpoint()
        org = create_fhir_organization()

        # Mock the mapper methods
        with patch.object(
            bundle_mapper.organization_mapper,
            "map_to_fhir_organization",
            return_value=org,
        ) as mock_org_mapper:
            with patch.object(
                bundle_mapper.endpoint_mapper,
                "map_to_fhir_endpoints",
                return_value=[endpoint],
            ) as mock_endpoint_mapper:
                # Act
                resources = bundle_mapper._create_resources(organisation)

                # Assert
                mock_org_mapper.assert_called_once_with(organisation)
                mock_endpoint_mapper.assert_called_once_with(organisation)
                assert len(resources) == 2
                assert resources[0] == org
                assert resources[1] == endpoint
