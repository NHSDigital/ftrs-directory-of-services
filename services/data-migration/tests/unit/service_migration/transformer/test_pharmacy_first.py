from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from ftrs_data_layer.domain.legacy import Service
from pytest_mock import MockerFixture

from common.cache import DoSMetadataCache
from service_migration.exceptions import ParentPharmacyNotFoundError
from service_migration.models import ServiceMigrationState
from service_migration.transformer.pharmacy_first import PharmacyFirstTransformer


@pytest.fixture(autouse=True)
def mock_feature_flags(mocker: MockerFixture) -> MagicMock:
    """Mock the feature flags to prevent AppConfig initialization."""
    return mocker.patch(
        "service_migration.transformer.pharmacy_first.is_enabled",
        return_value=True,
    )


@pytest.mark.parametrize(
    "service_type_id, ods_code, name, expected_result, expected_message",
    [
        (
            132,
            "FXX99M06",
            "PF++: Test Service",
            True,
            None,
        ),  # Valid case with M06 suffix
        (
            132,
            "A1B2CM06DSP",
            "PF++: Test Service",
            True,
            None,
        ),  # Valid case with M06DSP suffix
        (
            132,
            "FXX99M06DSP",
            "PF++: Test Service",
            True,
            None,
        ),  # Valid case with M06DSP suffix
        (
            13,
            "FXX99M06",
            "PF++: Test Service",
            False,
            "Service type is not a Pharmacy First type (132)",
        ),  # Wrong type
        (
            132,
            None,
            "PF++: Test Service",
            False,
            "Service does not have an ODS code",
        ),  # No ODS code
        (
            132,
            "FXX99",
            "PF++: Test Service",
            False,
            "ODS code does not end with required suffixes (M06DSP, M06)",
        ),  # Missing suffix
        (
            132,
            "FXX99CON",
            "PF++: Test Service",
            False,
            "ODS code does not end with required suffixes (M06DSP, M06)",
        ),  # Wrong suffix
        (
            132,
            "FXX99M06",
            "Test Service",
            False,
            "Service name does not start with the required prefix ('PF++:')",
        ),  # Wrong name prefix
        (
            132,
            "FXX99M06",
            None,
            False,
            "Service name does not start with the required prefix ('PF++:')",
        ),  # None name
        (
            132,
            "FXX99M06",
            "PF+: Test Service",
            False,
            "Service name does not start with the required prefix ('PF++:')",
        ),  # Wrong prefix PF+ instead of PF++
        (
            132,
            "FXX99M06",
            "pf++: Test Service",
            False,
            "Service name does not start with the required prefix ('PF++:')",
        ),  # Case-sensitive check
        (
            132,
            "FXX99M06",
            "Pharmacy First: Test Service",
            False,
            "Service name does not start with the required prefix ('PF++:')",
        ),  # Wrong prefix format
    ],
)
def test_is_service_supported(
    mock_legacy_service: Service,
    service_type_id: int,
    ods_code: str | None,
    name: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """Test that is_service_supported correctly validates Pharmacy First services."""
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = ods_code
    mock_legacy_service.name = name

    is_supported, message = PharmacyFirstTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == expected_result
    assert message == expected_message


def test_is_service_not_supported_when_pharmacy_feature_flag_disabled(
    mocker: MockerFixture,
    mock_legacy_service: Service,
) -> None:
    """Test that service is not supported when the pharmacy feature flag is disabled."""
    mocker.patch(
        "service_migration.transformer.pharmacy_first.is_enabled",
        return_value=False,
    )

    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"

    is_supported, message = PharmacyFirstTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported is False
    assert message == "Pharmacy First service selection is disabled by feature flag"


@pytest.mark.parametrize(
    "status_id, expected_result, expected_message",
    [
        (1, True, None),
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
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"
    mock_legacy_service.statusid = status_id

    should_include, message = PharmacyFirstTransformer.should_include_service(
        mock_legacy_service
    )

    assert should_include == expected_result
    assert message == expected_message


def test_should_include_service_inactive_with_existing_state(
    mock_legacy_service: Service,
) -> None:
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"
    mock_legacy_service.statusid = 2

    existing_state = ServiceMigrationState.init(service_id=mock_legacy_service.id)

    should_include, message = PharmacyFirstTransformer.should_include_service(
        mock_legacy_service,
        existing_state,
    )

    assert should_include is True
    assert message is None


def test_transform_creates_only_healthcare_service(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that transform creates only a HealthcareService linked to the parent org/location."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"
    mock_legacy_service.statusid = 1

    parent_org_id = uuid4()
    parent_loc_id = uuid4()

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    transformer.parent_organisation_id = parent_org_id
    transformer.parent_location_id = parent_loc_id

    result = transformer.transform(mock_legacy_service)

    assert result.organisation == []
    assert result.location == []
    assert len(result.healthcare_service) == 1

    hs = result.healthcare_service[0]
    assert hs.category == HealthcareServiceCategory.PHARMACY_SERVICES
    assert hs.type == HealthcareServiceType.PHARMACY_FIRST
    assert hs.providedBy == parent_org_id
    assert hs.location == parent_loc_id


def test_transform_parent_ids_are_none_by_default(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that parent_organisation_id and parent_location_id default to None on construction."""
    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)

    assert transformer.parent_organisation_id is None
    assert transformer.parent_location_id is None


def test_resolve_parent_uses_existing_state_record_with_m06_suffix(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """When a state record already exists for the parent, return its org/loc IDs immediately (M06 suffix)."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"

    parent_service = MagicMock(spec=Service)
    parent_service.id = 99

    parent_org_id = uuid4()
    parent_loc_id = uuid4()
    state = ServiceMigrationState.init(service_id=99)
    state = state.model_copy(
        update={"organisation_id": parent_org_id, "location_id": parent_loc_id}
    )

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(
        transformer, "_find_parent_service", return_value=parent_service
    )
    mock_get_state_record = MagicMock(return_value=state)

    result_parent, result_org_id, result_loc_id = transformer.resolve_parent(
        mock_legacy_service, MagicMock(), mock_get_state_record
    )

    assert result_parent is None
    assert result_org_id == parent_org_id
    assert result_loc_id == parent_loc_id
    mock_get_state_record.assert_called_once_with(parent_service.id)


def test_resolve_parent_uses_existing_state_record_with_m06dsp_suffix(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """When a state record already exists for the parent, return its org/loc IDs immediately (M06DSP suffix)."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06DSP"
    mock_legacy_service.name = "PF++: Test Service"

    parent_service = MagicMock(spec=Service)
    parent_service.id = 99

    parent_org_id = uuid4()
    parent_loc_id = uuid4()
    state = ServiceMigrationState.init(service_id=99)
    state = state.model_copy(
        update={"organisation_id": parent_org_id, "location_id": parent_loc_id}
    )

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(
        transformer, "_find_parent_service", return_value=parent_service
    )
    mock_get_state_record = MagicMock(return_value=state)

    result_parent, result_org_id, result_loc_id = transformer.resolve_parent(
        mock_legacy_service, MagicMock(), mock_get_state_record
    )

    assert result_parent is None
    assert result_org_id == parent_org_id
    assert result_loc_id == parent_loc_id
    mock_get_state_record.assert_called_once_with(parent_service.id)


def test_resolve_parent_returns_parent_service_when_state_absent(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """When the parent exists in DoS but has no state record, return the parent service for migration."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"

    parent_service = MagicMock(spec=Service)
    parent_service.id = 99

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(
        transformer, "_find_parent_service", return_value=parent_service
    )
    mock_get_state_record = MagicMock(return_value=None)

    result_parent, result_org_id, result_loc_id = transformer.resolve_parent(
        mock_legacy_service, MagicMock(), mock_get_state_record
    )

    assert result_parent is parent_service
    assert result_org_id is None
    assert result_loc_id is None


def test_resolve_parent_raises_when_no_parent_found_in_dos(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """When no parent pharmacy exists in the legacy DoS DB, raise ParentPharmacyNotFoundError."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06"
    mock_legacy_service.name = "PF++: Test Service"
    mock_legacy_service.id = 42

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(transformer, "_find_parent_service", return_value=None)
    mock_get_state_record = MagicMock()

    with pytest.raises(ParentPharmacyNotFoundError) as exc_info:
        transformer.resolve_parent(
            mock_legacy_service, MagicMock(), mock_get_state_record
        )

    assert exc_info.value.record_id == mock_legacy_service.id
    assert exc_info.value.ods_code == "FXX99"
    assert exc_info.value.requeue is False
    mock_get_state_record.assert_not_called()


def test_resolve_parent_derives_correct_base_ods_code_with_m06(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """Test that the base ODS code is correctly derived by stripping the M06 suffix."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "A1B2CM06"
    mock_legacy_service.name = "PF++: Test Service"

    parent_service = MagicMock(spec=Service)
    parent_service.id = 99

    find_parent_mock = mocker.patch.object(
        PharmacyFirstTransformer,
        "_find_parent_service",
        return_value=parent_service,
    )

    parent_org_id = uuid4()
    parent_loc_id = uuid4()
    state = ServiceMigrationState.init(service_id=99)
    state = state.model_copy(
        update={"organisation_id": parent_org_id, "location_id": parent_loc_id}
    )

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mock_engine = MagicMock()

    transformer.resolve_parent(
        mock_legacy_service, mock_engine, MagicMock(return_value=state)
    )

    find_parent_mock.assert_called_once_with(mock_engine, "A1B2C")


def test_resolve_parent_derives_correct_base_ods_code_with_m06dsp(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """Test that the base ODS code is correctly derived by stripping the M06DSP suffix."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "A1B2CM06DSP"
    mock_legacy_service.name = "PF++: Test Service"

    parent_service = MagicMock(spec=Service)
    parent_service.id = 99

    find_parent_mock = mocker.patch.object(
        PharmacyFirstTransformer,
        "_find_parent_service",
        return_value=parent_service,
    )

    parent_org_id = uuid4()
    parent_loc_id = uuid4()
    state = ServiceMigrationState.init(service_id=99)
    state = state.model_copy(
        update={"organisation_id": parent_org_id, "location_id": parent_loc_id}
    )

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mock_engine = MagicMock()

    transformer.resolve_parent(
        mock_legacy_service, mock_engine, MagicMock(return_value=state)
    )

    find_parent_mock.assert_called_once_with(mock_engine, "A1B2C")


def test_resolve_parent_correctly_detects_longer_suffix_first(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """Test that M06DSP is checked before M06 to avoid false positives."""
    mock_legacy_service.typeid = 132
    mock_legacy_service.odscode = "FXX99M06DSP"
    mock_legacy_service.name = "PF++: Test Service"

    parent_service = MagicMock(spec=Service)
    parent_service.id = 99

    find_parent_mock = mocker.patch.object(
        PharmacyFirstTransformer,
        "_find_parent_service",
        return_value=parent_service,
    )

    parent_org_id = uuid4()
    parent_loc_id = uuid4()
    state = ServiceMigrationState.init(service_id=99)
    state = state.model_copy(
        update={"organisation_id": parent_org_id, "location_id": parent_loc_id}
    )

    transformer = PharmacyFirstTransformer(MockLogger(), mock_metadata_cache)
    mock_engine = MagicMock()

    transformer.resolve_parent(
        mock_legacy_service, mock_engine, MagicMock(return_value=state)
    )

    # Should strip M06DSP (6 chars), not M06 (3 chars)
    # FXX99M06DSP -> FXX99 (5 chars base)
    find_parent_mock.assert_called_once_with(mock_engine, "FXX99")
