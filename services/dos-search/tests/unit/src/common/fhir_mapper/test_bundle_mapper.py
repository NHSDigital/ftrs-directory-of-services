from unittest.mock import patch

import pytest
from fhir.resources.R4B.bundle import Bundle

from src.common.fhir_mapper.bundle_mapper import BundleMapper

API_NAME = "dos-search"
PRIMARY_RESOURCE_TYPE = "Organization"
SELF_URL = "https://dos-search.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization?identifier=https://fhir.nhs.uk/Id/ods-organization-code|O123&_revinclude=Endpoint:organization"  # gitleaks:allow


@pytest.fixture
def bundle_mapper() -> BundleMapper:
    return BundleMapper(api_name=API_NAME, primary_resource_type=PRIMARY_RESOURCE_TYPE)


@pytest.fixture
def mock_get_fhir_url():
    with patch("src.common.fhir_mapper.bundle_mapper.get_fhir_url") as mock:
        yield mock


class TestBundleMapper:
    def test_map_to_fhir_with_no_resources(self, bundle_mapper: BundleMapper) -> None:
        # Act
        bundle = bundle_mapper.map_to_fhir([], SELF_URL)

        # Assert
        assert isinstance(bundle, Bundle)
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 0
        assert len(bundle.link) == 1
        assert bundle.link[0].relation == "self"
        assert bundle.link[0].url == SELF_URL

    def test_map_to_fhir_with_organization_only(
        self, bundle_mapper: BundleMapper, create_fhir_organization, mock_get_fhir_url
    ) -> None:
        # Arrange
        org_resource = create_fhir_organization()
        mock_get_fhir_url.return_value = "https://dos-search.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000"  # gitleaks:allow

        # Act
        bundle = bundle_mapper.map_to_fhir([org_resource], SELF_URL)

        # Assert
        assert isinstance(bundle, Bundle)
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 1
        assert bundle.entry[0].resource == org_resource
        assert bundle.entry[0].search.mode == "match"

    def test_map_to_fhir_with_multiple_resources(
        self,
        bundle_mapper: BundleMapper,
        create_fhir_organization,
        create_fhir_endpoint,
        mock_get_fhir_url,
    ) -> None:
        # Arrange
        org_resource = create_fhir_organization()
        endpoint1 = create_fhir_endpoint()
        endpoint2 = create_fhir_endpoint()
        mock_get_fhir_url.return_value = "https://example.org/FHIR/R4/resource"

        # Act
        bundle = bundle_mapper.map_to_fhir(
            [org_resource, endpoint1, endpoint2], SELF_URL
        )

        # Assert
        assert isinstance(bundle, Bundle)
        assert bundle.type == "searchset"
        assert len(bundle.entry) == 3
        assert bundle.entry[0].resource == org_resource
        assert bundle.entry[1].resource == endpoint1
        assert bundle.entry[2].resource == endpoint2

    def test_create_entry_for_endpoint(
        self,
        bundle_mapper: BundleMapper,
        create_fhir_endpoint,
        mock_get_fhir_url,
    ) -> None:
        # Arrange
        endpoint_resource = create_fhir_endpoint()
        mock_get_fhir_url.return_value = (
            "https://example.org/FHIR/R4/Endpoint/endpoint-123"
        )

        # Act
        entry = bundle_mapper._create_entry(endpoint_resource)

        # Assert
        mock_get_fhir_url.assert_called_once_with(
            API_NAME, "Endpoint", endpoint_resource.id
        )
        assert entry["fullUrl"] == "https://example.org/FHIR/R4/Endpoint/endpoint-123"
        assert entry["resource"] == endpoint_resource
        assert entry["search"]["mode"] == "include"

    def test_create_entry_for_organization(
        self,
        bundle_mapper: BundleMapper,
        create_fhir_organization,
        mock_get_fhir_url,
    ) -> None:
        # Arrange
        organization_resource = create_fhir_organization()
        mock_get_fhir_url.return_value = "https://dos-search.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000"  # gitleaks:allow

        # Act
        entry = bundle_mapper._create_entry(organization_resource)

        # Assert
        mock_get_fhir_url.assert_called_once_with(
            API_NAME, "Organization", organization_resource.id
        )
        assert (
            entry["fullUrl"]
            == "https://dos-search.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000"  # gitleaks:allow
        )
        assert entry["resource"] == organization_resource
        assert entry["search"]["mode"] == "match"

    def test_get_search_mode_match_for_primary_type(
        self,
        bundle_mapper: BundleMapper,
        create_fhir_organization,
    ) -> None:
        # Arrange
        org_resource = create_fhir_organization()

        # Act & Assert
        assert bundle_mapper._get_search_mode(org_resource) == "match"

    def test_get_search_mode_include_for_non_primary_type(
        self,
        bundle_mapper: BundleMapper,
        create_fhir_endpoint,
    ) -> None:
        # Arrange
        endpoint_resource = create_fhir_endpoint()

        # Act & Assert
        assert bundle_mapper._get_search_mode(endpoint_resource) == "include"

    def test_get_search_mode_is_configurable(
        self, create_fhir_endpoint, create_fhir_organization
    ) -> None:
        # Arrange - create a mapper where Endpoint is the primary type
        mapper = BundleMapper(api_name=API_NAME, primary_resource_type="Endpoint")
        endpoint_resource = create_fhir_endpoint()
        org_resource = create_fhir_organization()

        # Act & Assert
        assert mapper._get_search_mode(endpoint_resource) == "match"
        assert mapper._get_search_mode(org_resource) == "include"

    def test_bundle_self_link_uses_provided_url(
        self, bundle_mapper: BundleMapper
    ) -> None:
        # Arrange
        custom_url = "https://example.org/FHIR/R4/HealthcareService?active=true"

        # Act
        bundle = bundle_mapper.map_to_fhir([], custom_url)

        # Assert
        assert bundle.link[0].url == custom_url

    def test_api_name_passed_to_get_fhir_url(
        self, create_fhir_organization, mock_get_fhir_url
    ) -> None:
        # Arrange
        custom_api = "crud-apis"
        mapper = BundleMapper(api_name=custom_api, primary_resource_type="Organization")
        org_resource = create_fhir_organization()
        mock_get_fhir_url.return_value = "https://crud-apis.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/org-id"  # gitleaks:allow

        # Act
        mapper.map_to_fhir([org_resource], SELF_URL)

        # Assert
        mock_get_fhir_url.assert_called_once_with(
            custom_api, "Organization", org_resource.id
        )
