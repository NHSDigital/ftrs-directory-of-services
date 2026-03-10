from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain.legacy import Service
from pytest_mock import MockerFixture

from common.cache import DoSMetadataCache
from service_migration.exceptions import ParentPharmacyNotFoundError
from service_migration.models import ServiceMigrationState
from service_migration.transformer.pharmacy_blood_pressure_check import (
    PharmacyBPCheckTransformer,
)


@pytest.fixture(autouse=True)
def mock_feature_flags(mocker: MockerFixture) -> MagicMock:
    """Mock the feature flags to prevent AppConfig initialization."""
    return mocker.patch(
        "service_migration.transformer.pharmacy_blood_pressure_check.is_enabled",
        return_value=True,
    )


@pytest.mark.parametrize(
    "service_type_id, ods_code, expected_result, expected_message",
    [
        (
            148,
            "FXX99BPS",
            True,
            None,
        ),
        (
            148,
            "A1B2CBPS",
            True,
            None,
        ),
        (
            134,
            "FXX99BPS",
            False,
            "Service type is not a Pharmacy type (148)",
        ),
        (
            148,
            None,
            False,
            "Service does not have an ODS code",
        ),
        (
            148,
            "FXX99",
            False,
            "ODS code is not 8 characters",
        ),
        (
            148,
            "FXX99XYZ",
            False,
            "ODS code does not end with BPS",
        ),
        (
            148,
            "12345BPS",
            False,
            "ODS code does not match required format (F + 4 alphanumeric OR alternating letter-number)",
        ),
    ],
)
def test_is_service_supported(
    mock_legacy_service: Service,
    service_type_id: int,
    ods_code: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = ods_code

    is_supported, message = PharmacyBPCheckTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == expected_result
    assert message == expected_message


def test_is_service_not_supported_when_feature_flag_disabled(
    mock_legacy_service: Service,
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "service_migration.transformer.pharmacy_blood_pressure_check.is_enabled",
        return_value=False,
    )

    mock_legacy_service.typeid = 148
    mock_legacy_service.odscode = "FXX99BPS"

    is_supported, message = PharmacyBPCheckTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported is False
    assert message == "Pharmacy service selection is disabled by feature flag"


@pytest.mark.parametrize(
    "statusid, service_name, expected_result, expected_message",
    [
        (1, "BP Check: Test Service", True, None),
        (1, "BP: Test Service", True, None),
        (
            1,
            "bp check: Test Service",
            False,
            "Service name does not start with required prefix (BP Check: or BP:)",
        ),
        (
            1,
            "Test Service",
            False,
            "Service name does not start with required prefix (BP Check: or BP:)",
        ),
        (1, None, False, "Service name is missing"),
        (2, "BP Check: Test Service", False, "Service is not active"),
        (3, "BP Check: Test Service", False, "Service is not active"),
    ],
)
def test_should_include_service(
    mock_legacy_service: Service,
    statusid: int,
    service_name: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    mock_legacy_service.statusid = statusid
    mock_legacy_service.name = service_name

    should_include, message = PharmacyBPCheckTransformer.should_include_service(
        mock_legacy_service
    )

    assert should_include == expected_result
    assert message == expected_message


def test_transform_uses_parent_ids_from_transformer_instance(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """Test that transform() uses parent IDs set on the transformer instance."""
    parent_org_id = uuid4()
    parent_location_id = uuid4()

    transformer = PharmacyBPCheckTransformer(MockLogger(), mock_metadata_cache)
    # Processor sets these before calling transform()
    transformer.parent_organisation_id = parent_org_id
    transformer.parent_location_id = parent_location_id

    mock_legacy_service.typeid = 148
    mock_legacy_service.odscode = "FXX99BPS"
    mock_legacy_service.name = "BP: Test Service"

    result = transformer.transform(mock_legacy_service)

    assert len(result.organisation) == 0
    assert len(result.location) == 0
    assert len(result.healthcare_service) == 1
    assert result.healthcare_service[0].providedBy == parent_org_id
    assert result.healthcare_service[0].location == parent_location_id
    assert (
        result.healthcare_service[0].category
        == HealthcareServiceCategory.PHARMACY_SERVICES
    )
    assert (
        result.healthcare_service[0].type == HealthcareServiceType.BLOOD_PRESSURE_CHECK
    )


def test_resolve_parent_returns_existing_state_ids(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """Test resolve_parent returns IDs when parent state exists."""
    parent_org_id = uuid4()
    parent_location_id = uuid4()

    parent_service = Service(
        **mock_legacy_service.model_dump(mode="python", warnings=False)
    )
    parent_service.id = 12345
    parent_service.typeid = 148
    parent_service.odscode = "FXX99"

    state = ServiceMigrationState.init(service_id=parent_service.id)
    state.organisation_id = parent_org_id
    state.location_id = parent_location_id

    mock_engine = MagicMock()
    mock_get_state = MagicMock(return_value=state)

    transformer = PharmacyBPCheckTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(
        transformer, "_find_parent_service", return_value=parent_service
    )

    mock_legacy_service.typeid = 148
    mock_legacy_service.odscode = "FXX99BPS"

    parent_svc, org_id, loc_id = transformer.resolve_parent(
        mock_legacy_service, mock_engine, mock_get_state
    )

    assert parent_svc is None  # Parent already migrated
    assert org_id == parent_org_id
    assert loc_id == parent_location_id
    mock_get_state.assert_called_once_with(parent_service.id)


def test_resolve_parent_returns_service_when_state_missing(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """Test resolve_parent returns parent service when state doesn't exist."""
    parent_service = Service(
        **mock_legacy_service.model_dump(mode="python", warnings=False)
    )
    parent_service.id = 12345
    parent_service.typeid = 148
    parent_service.odscode = "FXX99"

    mock_engine = MagicMock()
    mock_get_state = MagicMock(return_value=None)

    transformer = PharmacyBPCheckTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(
        transformer, "_find_parent_service", return_value=parent_service
    )

    mock_legacy_service.typeid = 148
    mock_legacy_service.odscode = "FXX99BPS"

    parent_svc, org_id, loc_id = transformer.resolve_parent(
        mock_legacy_service, mock_engine, mock_get_state
    )

    assert parent_svc == parent_service  # Parent needs migrating
    assert org_id is None
    assert loc_id is None
    mock_get_state.assert_called_once_with(parent_service.id)


def test_resolve_parent_derives_correct_base_ods_code(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    parent_service = Service(
        **mock_legacy_service.model_dump(mode="python", warnings=False)
    )
    parent_service.id = 12345
    parent_service.typeid = 148
    parent_service.odscode = "A1B2C"

    mock_engine = MagicMock()
    mock_get_state = MagicMock(return_value=None)

    transformer = PharmacyBPCheckTransformer(MockLogger(), mock_metadata_cache)
    find_parent = mocker.patch.object(
        transformer, "_find_parent_service", return_value=parent_service
    )

    mock_legacy_service.typeid = 148
    mock_legacy_service.odscode = "A1B2CBPS"

    transformer.resolve_parent(mock_legacy_service, mock_engine, mock_get_state)

    find_parent.assert_called_once_with(mock_engine, "A1B2C")


def test_resolve_parent_raises_when_parent_not_found(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    mocker: MockerFixture,
) -> None:
    """Test resolve_parent raises ParentPharmacyNotFoundError when parent doesn't exist."""
    mock_engine = MagicMock()
    mock_get_state = MagicMock()

    transformer = PharmacyBPCheckTransformer(MockLogger(), mock_metadata_cache)
    mocker.patch.object(transformer, "_find_parent_service", return_value=None)

    test_service_id = 99999
    mock_legacy_service.id = test_service_id
    mock_legacy_service.typeid = 148
    mock_legacy_service.odscode = "FXX99BPS"

    with pytest.raises(ParentPharmacyNotFoundError) as exc_info:
        transformer.resolve_parent(mock_legacy_service, mock_engine, mock_get_state)

    assert exc_info.value.record_id == test_service_id
    assert exc_info.value.ods_code == "FXX99"
    assert exc_info.value.requeue is False
