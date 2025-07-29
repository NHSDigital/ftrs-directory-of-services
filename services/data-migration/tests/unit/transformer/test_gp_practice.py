import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain.legacy import Service, ServiceStatusEnum

from pipeline.transformer.gp_practice import GPPracticeTransformer
from pipeline.utils.cache import DoSMetadataCache


@pytest.mark.parametrize(
    "service_type_id, ods_code, expected_result, expected_message",
    [
        (100, "A12345", True, None),  # Valid GP Practice
        (200, "A12345", False, "Service type is not GP Practice (100)"),
        (100, None, False, "Service does not have an ODS code"),
        (100, "X12345", False, "ODS code does not match the required format"),
        (100, "A1234", False, "ODS code does not match the required format"),
    ],
)
def test_is_service_supported(
    mock_legacy_service: Service,
    service_type_id: int,
    ods_code: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """
    Test that is_service_supported returns True for a valid GP profile
    """
    mock_legacy_service.type.id = service_type_id
    mock_legacy_service.odscode = ods_code

    is_supported, message = GPPracticeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == expected_result
    assert message == expected_message


@pytest.mark.parametrize(
    "status_id, expected_result, expected_message",
    [
        (ServiceStatusEnum.ACTIVE, True, None),  # Active service
        (ServiceStatusEnum.CLOSED, False, "Service is not active"),
        (ServiceStatusEnum.SUSPENDED, False, "Service is not active"),
    ],
)
def test_should_include_service(
    mock_legacy_service: Service,
    status_id: ServiceStatusEnum,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """
    Test that should_include_service returns True for a valid GP profile
    """
    mock_legacy_service.type.id = 100  # GP Practice type ID
    mock_legacy_service.odscode = "A12345"  # Valid ODS code
    mock_legacy_service.statusid = status_id

    should_include, message = GPPracticeTransformer.should_include_service(
        mock_legacy_service
    )

    assert should_include == expected_result
    assert message == expected_message


def test_transform(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    """
    Test that transform method correctly transforms a GP practice service.
    """
    mock_legacy_service.type.id = 100  # GP Practice type ID
    mock_legacy_service.odscode = "A12345"  # Valid ODS code
    mock_legacy_service.statusid = ServiceStatusEnum.ACTIVE

    transformer = GPPracticeTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service)

    assert result.organisation.identifier_ODS_ODSCode == "A12345"
    assert result.healthcare_service.category == HealthcareServiceCategory.GP_SERVICES
    assert (
        result.healthcare_service.type == HealthcareServiceType.GP_CONSULTATION_SERVICE
    )
