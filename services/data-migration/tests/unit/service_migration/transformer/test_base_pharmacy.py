from unittest.mock import MagicMock

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from ftrs_data_layer.domain.legacy import Service
from pytest_mock import MockerFixture

from common.cache import DoSMetadataCache
from service_migration.models import ServiceMigrationState
from service_migration.transformer.base_pharmacy import BasePharmacyTransformer


@pytest.fixture(autouse=True)
def mock_feature_flags(mocker: MockerFixture) -> MagicMock:
    """Mock the feature flags to prevent AppConfig initialization."""
    return mocker.patch(
        "service_migration.transformer.base_pharmacy.is_enabled",
        return_value=True,
    )


@pytest.mark.parametrize(
    "service_type_id, ods_code, expected_result, expected_message",
    [
        (13, "FXX99", True, None),  # Valid Community Pharmacy with F-prefix
        (13, "A1B2C", True, None),  # Valid Community Pharmacy with alternating pattern
        (13, "F1234", True, None),  # Valid Community Pharmacy with F and numbers
        (13, "FABCD", True, None),  # Valid Community Pharmacy with F and letters
        (134, "FXX99", True, None),  # Valid Distance Selling Pharmacy with F-prefix
        (
            134,
            "A1B2C",
            True,
            None,
        ),  # Valid Distance Selling Pharmacy with alternating pattern
        (
            134,
            "F1234",
            True,
            None,
        ),  # Valid Distance Selling Pharmacy with F and numbers
        (
            134,
            "FABCD",
            True,
            None,
        ),  # Valid Distance Selling Pharmacy with F and letters
        (
            100,
            "FXX99",
            False,
            "Service type is not a Pharmacy type (13, 134)",
        ),  # Wrong service type
        (13, None, False, "Service does not have an ODS code"),  # No ODS code
        (13, "FXXX", False, "ODS code is not 5 characters"),  # Too short
        (13, "FXXXXX", False, "ODS code is not 5 characters"),  # Too long
        (
            13,
            "XXXXX",
            False,
            "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
        ),  # Wrong format
        (
            13,
            "12345",
            False,
            "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
        ),  # Numbers only
        (
            13,
            "A12BC",
            False,
            "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
        ),  # Wrong alternating pattern
    ],
)
def test_is_service_supported(
    mock_legacy_service: Service,
    service_type_id: int,
    ods_code: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """Test that is_service_supported correctly validates Pharmacy services."""
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = ods_code

    is_supported, message = BasePharmacyTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == expected_result
    assert message == expected_message


def test_is_service_not_supported_when_feature_flag_disabled(
    mocker: MockerFixture,
    mock_legacy_service: Service,
) -> None:
    """Test that service is not supported when feature flag is disabled."""
    mocker.patch(
        "service_migration.transformer.base_pharmacy.is_enabled",
        return_value=False,
    )

    mock_legacy_service.typeid = 13  # Community Pharmacy type ID
    mock_legacy_service.odscode = "FXX99"  # Valid ODS code

    is_supported, message = BasePharmacyTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported is False
    assert message == "Pharmacy service selection is disabled by feature flag"


@pytest.mark.parametrize(
    "status_id, expected_result, expected_message",
    [
        (1, True, None),  # Active service
        (2, False, "Service is not active"),
        (3, False, "Service is not active"),
    ],
)
def test_should_include_service(
    mock_legacy_service: Service,
    status_id: int,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """Test that should_include_service validates active status."""
    mock_legacy_service.typeid = 13  # Community Pharmacy type ID
    mock_legacy_service.odscode = "FXX99"  # Valid ODS code
    mock_legacy_service.statusid = status_id

    should_include, message = BasePharmacyTransformer.should_include_service(
        mock_legacy_service
    )

    assert should_include == expected_result
    assert message == expected_message


def test_should_include_service_inactive_with_existing_state(
    mock_legacy_service: Service,
) -> None:
    mock_legacy_service.typeid = 13
    mock_legacy_service.odscode = "FXX99"
    mock_legacy_service.statusid = 2

    existing_state = ServiceMigrationState.init(service_id=mock_legacy_service.id)

    should_include, message = BasePharmacyTransformer.should_include_service(
        mock_legacy_service,
        existing_state,
    )

    assert should_include is True
    assert message is None


@pytest.mark.parametrize(
    "service_type_id, organisation_type",
    [
        (13, "Community Pharmacy"),  # Community Pharmacy
        (134, "Distance Selling Pharmacy"),  # Distance Selling Pharmacy
    ],
)
def test_transform_creates_all_entities(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    service_type_id: int,
    organisation_type: str,
) -> None:
    """Test that transform creates organisation, location, and healthcare_service."""
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = "FXX99"  # Valid ODS code
    mock_legacy_service.statusid = 1  # Active status

    transformer = BasePharmacyTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service)

    # All resources should be created
    assert len(result.organisation) == 1
    assert len(result.location) == 1
    assert len(result.healthcare_service) == 1

    # Verify organisation details
    assert result.organisation[0].identifier_ODS_ODSCode == "FXX99"
    assert result.organisation[0].name == "Public Test Service"
    assert (
        result.organisation[0].type == organisation_type
    )  # From service_type metadata

    # Verify healthcare service details
    assert (
        result.healthcare_service[0].category
        == HealthcareServiceCategory.PHARMACY_SERVICES
    )
    assert result.healthcare_service[0].type == HealthcareServiceType.ESSENTIAL_SERVICES


@pytest.mark.parametrize(
    "service_type_id",
    [13, 134],
)
def test_transform_endpoints_excluded_from_organisation(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    service_type_id: int,
) -> None:
    """Test that organisation endpoints are explicitly excluded even when source data contains endpoints."""
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = "FXX99"  # Valid ODS code
    mock_legacy_service.statusid = 1  # Active status
    # Ensure source data has endpoints to confirm the override strips them
    assert len(mock_legacy_service.endpoints) > 0, (
        "Fixture must have endpoints for this test to be meaningful"
    )

    transformer = BasePharmacyTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service)

    # Verify organisation has no endpoints regardless of source data
    assert len(result.organisation) == 1
    assert result.organisation[0].endpoints == []
    # Endpoints are assigned to the healthcare service instead
    assert len(result.healthcare_service[0].endpoints) == len(
        mock_legacy_service.endpoints
    )


@pytest.mark.parametrize(
    "service_type_id",
    [13, 134],
)
def test_transform_healthcare_service_endpoints_linked_correctly(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    service_type_id: int,
) -> None:
    """Test that HS endpoints have correct managedByOrganisation and service linkage."""
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = "FXX99"
    mock_legacy_service.statusid = 1
    assert len(mock_legacy_service.endpoints) > 0

    transformer = BasePharmacyTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service)

    org_id = result.organisation[0].id
    hs_id = result.healthcare_service[0].id
    for endpoint in result.healthcare_service[0].endpoints:
        assert endpoint.managedByOrganisation == org_id
        assert endpoint.service == hs_id


@pytest.mark.parametrize(
    "service_type_id",
    [13, 134],
)
def test_transform_healthcare_service_has_no_endpoints_when_service_has_none(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    service_type_id: int,
) -> None:
    """Test that HS endpoints list is empty when the source service has no endpoints."""
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = "FXX99"
    mock_legacy_service.statusid = 1
    mock_legacy_service.endpoints = []

    transformer = BasePharmacyTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service)

    assert result.healthcare_service[0].endpoints == []
