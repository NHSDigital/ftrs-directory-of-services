from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fhir.resources.R4B.bundle import Bundle
from fhir.resources.R4B.healthcareservice import (
    HealthcareService as FhirHealthcareService,
)
from ftrs_data_layer.domain import HealthcareService
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)

from functions.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM
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
def mock_healthcare_service() -> HealthcareService:
    return HealthcareService(
        id=uuid4(),
        identifier_oldDoS_uid=None,
        active=True,
        category=HealthcareServiceCategory.GP_SERVICES,
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        providedBy=None,
        location=None,
        name="Test Healthcare Service",
        telecom=None,
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
        endpoints=[],
        referralMethod=[],
    )


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
        mock_healthcare_service: HealthcareService,
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
        assert f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|{ods_code}" in result.link[0].url

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
    ) -> None:
        # Arrange
        ods_code = "O123"
        mock_hs_1 = HealthcareService(
            id=uuid4(),
            identifier_oldDoS_uid=None,
            active=True,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=None,
            location=None,
            name="Healthcare Service 1",
            telecom=None,
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )

        mock_hs_2 = HealthcareService(
            id=uuid4(),
            identifier_oldDoS_uid=None,
            active=True,
            category=HealthcareServiceCategory.GP_SERVICES,
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            providedBy=None,
            location=None,
            name="Healthcare Service 2",
            telecom=None,
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )

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
        mock_healthcare_service: HealthcareService,
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
        mock_healthcare_service: HealthcareService,
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
        mock_healthcare_service: HealthcareService,
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
        assert result.entry[0].resource.id == str(mock_healthcare_service.id)

    @patch(
        "functions.ftrs_service.fhir_mapper.healthcare_service_bundle_mapper.get_fhir_url"
    )
    def test_map_to_fhir_uses_correct_fhir_url(
        self,
        mock_get_fhir_url: MagicMock,
        healthcare_service_bundle_mapper: HealthcareServiceBundleMapper,
        mock_healthcare_service: HealthcareService,
    ) -> None:
        # Arrange
        ods_code = "O123"
        mock_get_fhir_url.return_value = "https://test.fhir.url/HealthcareService"
        healthcare_services = [mock_healthcare_service]

        # Act
        healthcare_service_bundle_mapper.map_to_fhir(healthcare_services, ods_code)

        # Assert
        mock_get_fhir_url.assert_called()
