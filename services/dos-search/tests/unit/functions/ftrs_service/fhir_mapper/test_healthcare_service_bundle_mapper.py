from unittest.mock import MagicMock, patch

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)

from functions.ftrs_service.fhir_mapper.healthcare_service_bundle_mapper import (
    HealthcareServiceBundleMapper,
)


@pytest.fixture
def healthcare_service_bundle_mapper() -> HealthcareServiceBundleMapper:
    return HealthcareServiceBundleMapper()


@pytest.fixture
def mock_fhir_healthcare_service() -> FhirHealthcareService:
    return FhirHealthcareService.model_validate(
        {
            "id": "org-123",
            "name": "Test Healthcare Service",
            "active": True,
        }
    )


@pytest.fixture
def mock_healthcare_service() -> MagicMock:
    mock = MagicMock()
    mock.id = "org-123"
    mock.name = "Test Healthcare Service"
    mock.active = True
    mock.identifier_oldDoS_uid = None
    mock.providedBy = None
    mock.location = None
    mock.category = None
    mock.type = None
    mock.telecom = None
    return mock


class TestHealthcareServiceBundleMapper:
    def test_map_to_fhir_empty_list(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
    ) -> None:
        # Arrange
        ods_code = "O123"

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir([], ods_code)

        # Assert
        assert isinstance(result, Bundle)
        assert result.type == "searchset"
        assert result.total == 0
        assert result.entry == []

    def test_map_to_fhir_with_healthcare_services(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        healthcare_services = [mock_healthcare_service]

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir(
            healthcare_services, ods_code
        )

        # Assert
        assert isinstance(result, Bundle)
        assert result.type == "searchset"
        assert result.total == 1
        assert len(result.entry) == 1

    def test_map_to_fhir_bundle_has_link(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
    ) -> None:
        # Arrange
        ods_code = "ABC123"

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir([], ods_code)

        # Assert
        assert len(result.link) == 1
        assert result.link[0].relation == "self"
        assert "HealthcareService" in result.link[0].url
        assert f"odsOrganisationCode|{ods_code}" in result.link[0].url

    def test_map_to_fhir_bundle_has_id(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
    ) -> None:
        ods_code = "O123"

        result = healthcare_service_bundle_mapper.map_to_fhir([], ods_code)

        assert result.id is not None

    def test_map_to_fhir_multiple_healthcare_services(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        mock_hs_1 = MagicMock()
        mock_hs_1.id = "org-123"
        mock_hs_1.name = "Healthcare Service 1"
        mock_hs_1.active = True
        mock_hs_1.identifier_oldDoS_uid = None
        mock_hs_1.providedBy = None
        mock_hs_1.location = None
        mock_hs_1.category = None
        mock_hs_1.type = None
        mock_hs_1.telecom = None

        mock_hs_2 = MagicMock()
        mock_hs_2.id = "org-124"
        mock_hs_2.name = "Healthcare Service 2"
        mock_hs_2.active = True
        mock_hs_2.identifier_oldDoS_uid = None
        mock_hs_2.providedBy = None
        mock_hs_2.location = None
        mock_hs_2.category = None
        mock_hs_2.type = None
        mock_hs_2.telecom = None

        healthcare_services = [mock_hs_1, mock_hs_2]

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir(
            healthcare_services, ods_code
        )

        # Assert
        assert result.total == 2
        assert len(result.entry) == 2

    def test_map_to_fhir_entry_has_full_url(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        healthcare_services = [mock_healthcare_service]

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir(
            healthcare_services, ods_code
        )

        # Assert
        assert result.entry[0].fullUrl is not None
        assert "HealthcareService" in result.entry[0].fullUrl
        assert str(mock_healthcare_service.id) in result.entry[0].fullUrl

    def test_map_to_fhir_entry_has_search_mode_match(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        healthcare_services = [mock_healthcare_service]

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir(
            healthcare_services, ods_code
        )

        # Assert
        assert result.entry[0].search.mode == "match"

    def test_map_to_fhir_entry_resource_is_healthcare_service(
        self,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        healthcare_services = [mock_healthcare_service]

        # Act
        result = healthcare_service_bundle_mapper.map_to_fhir(
            healthcare_services, ods_code
        )

        # Assert
        assert isinstance(result.entry[0].resource, FhirHealthcareService)
        assert result.entry[0].resource.name == mock_healthcare_service.name

    @patch(
        "functions.ftrs_service.fhir_mapper.healthcare_service_bundle_mapper.get_fhir_url"
    )
    def test_map_to_fhir_uses_correct_fhir_url(
        self,
        mock_get_fhir_url: MagicMock,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: MagicMock,
    ) -> None:
        # Arrange
        ods_code = "O123"
        mock_get_fhir_url.return_value = "https://test.fhir.url/HealthcareService"
        healthcare_services = [mock_healthcare_service]

        # Act
        healthcare_service_bundle_mapper.map_to_fhir(healthcare_services, ods_code)

        # Assert
        mock_get_fhir_url.assert_called()
