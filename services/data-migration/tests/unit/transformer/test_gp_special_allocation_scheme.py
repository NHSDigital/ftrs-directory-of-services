import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from ftrs_data_layer.domain.legacy import Service

from pipeline.transformer.gp_special_allocation_scheme import (
    GPSpecialAllocationSchemeTransformer,
)
from pipeline.utils.cache import DoSMetadataCache


@pytest.mark.parametrize(
    "test_data",
    [
        # Invalid service type
        {
            "service_type_id": 200,  # invalid service type
            "ods_code": "A12345",
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "Service typeid 200 is not supported",
        },
        # Invalid ODS code
        {
            "service_type_id": 100,
            "ods_code": None,
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "Service does not have an ODS code",
            # no ODS Code
        },
        {
            "service_type_id": 100,
            "ods_code": "A1234",
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (6 chars, 1 letter + 5 digits)",
            # ODS code too short
        },
        {
            "service_type_id": 100,
            "ods_code": "A123456",
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (6 chars, 1 letter + 5 digits)",
            # ODS code too long
        },
        {
            "service_type_id": 100,
            "ods_code": "112345",
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (6 chars, 1 letter + 5 digits)",
            # ODS code starts with digit
        },
        {
            "service_type_id": 100,
            "ods_code": "a12345",
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (6 chars, 1 letter + 5 digits)",
            # ODS code contains lowercase letter
        },
        {
            "service_type_id": 100,
            "ods_code": "A12B45",
            "name": "Special Allocation Scheme",
            "expected_result": False,
            "expected_message": "ODS code does not match the required format (6 chars, 1 letter + 5 digits)",
            # ODS code contains non-digit characters after first letter
        },
        # Invalid name
        {
            "service_type_id": 100,
            "ods_code": "A12345",
            "name": "Name",
            "expected_result": False,
            "expected_message": "Service name does not contain 'SAS' or 'Special Allocation Scheme'",
        },
    ],
)
def test_is_service_supported_invalid_services(
    mock_legacy_service: Service,
    test_data: dict,
) -> None:
    mock_legacy_service.typeid = test_data["service_type_id"]
    mock_legacy_service.odscode = test_data["ods_code"]
    mock_legacy_service.name = test_data["name"]

    is_supported, message = GPSpecialAllocationSchemeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == test_data["expected_result"]
    assert message == test_data["expected_message"]


@pytest.mark.parametrize(
    "test_data",
    [
        # Valid GP Special Allocation Scheme Services
        {
            "service_type_id": 100,
            "ods_code": "G12345",
            "name": "Special Allocation Scheme",
            "expected_result": True,
            "expected_message": None,
        },
        {
            "service_type_id": 100,
            "ods_code": "H67890",
            "name": "GP - SAS",
            "expected_result": True,
            "expected_message": None,
        },
    ],
)
def test_is_service_supported_valid_services(
    mock_legacy_service: Service,
    test_data: dict,
) -> None:
    mock_legacy_service.typeid = test_data["service_type_id"]
    mock_legacy_service.odscode = test_data["ods_code"]
    mock_legacy_service.name = test_data["name"]

    is_supported, message = GPSpecialAllocationSchemeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == test_data["expected_result"]
    assert message == test_data["expected_message"]


@pytest.mark.parametrize(
    "status_id, expected_result, expected_message",
    [
        (1, True, None),  # Active service
        (2, False, "Service is not 'active'"),
    ],
)
def test_should_include_service(
    mock_legacy_service: Service,
    status_id: int,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    mock_legacy_service.typeid = 100
    mock_legacy_service.odscode = "A12345"
    mock_legacy_service.statusid = status_id

    should_include, message = (
        GPSpecialAllocationSchemeTransformer.should_include_service(mock_legacy_service)
    )

    assert should_include == expected_result
    assert message == expected_message


def test_transform(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """
    Test that transform method correctly transforms a GP Special Allocation Scheme Service
    """
    mock_legacy_service.typeid = 100  # GP Practice
    mock_legacy_service.odscode = "G12345"  # GP Practice
    mock_legacy_service.name = "GP - Name - Special Allocation Scheme"
    mock_legacy_service.statusid = 1  # Active status

    transformer = GPSpecialAllocationSchemeTransformer(
        MockLogger(), mock_metadata_cache
    )
    result = transformer.transform(mock_legacy_service)

    # TODO: organisation and location not linked yet, test this, & when public name is empty for organisation.name
    assert len(result.organisation) == 0
    assert len(result.location) == 0

    assert len(result.healthcare_service) == 1
    assert result.healthcare_service[0].name == "GP - Name - Special Allocation Scheme"
    assert (
        result.healthcare_service[0].category == HealthcareServiceCategory.GP_SERVICES
    )
    assert result.healthcare_service[0].type == HealthcareServiceType.SAS_SERVICE
