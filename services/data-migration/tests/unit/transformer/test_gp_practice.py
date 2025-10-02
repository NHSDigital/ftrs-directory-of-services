import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain.legacy import Service

from pipeline.transformer.gp_practice import GPPracticeTransformer
from pipeline.utils.cache import DoSMetadataCache


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "service_type_id": 100,
            "ods_code": "A12345",
            "name": "Name",
            "expected_result": True,
            "expected_message": None,
        },  # Valid GP Practice
        {
            "service_type_id": 200,
            "ods_code": "A12345",
            "name": "Name",
            "expected_result": False,
            "expected_message": "Service type is not GP Practice (100)",
        },
        {
            "service_type_id": 100,
            "ods_code": None,
            "name": "Name",
            "expected_result": False,
            "expected_message": "Service does not have an ODS code",
        },
        {
            "service_type_id": 100,
            "ods_code": "X12345",
            "name": "Name",
            "expected_result": False,
            "expected_message": "ODS code does not match the required format",
        },
        # potential GP Practice misclassification of PLT is handled
        {
            "service_type_id": 100,
            "ods_code": "G12345",
            "name": "PLT - GP COVER",
            "expected_result": False,
            "expected_message": "Service name is PLT specific",
        },  # Invalid since it's GP protected learning Time
    ],
)
def test_is_service_supported(
    mock_legacy_service: Service,
    test_data: dict,
) -> None:
    """
    Test that is_service_supported returns True for a valid GP profile
    """
    mock_legacy_service.typeid = test_data["service_type_id"]
    mock_legacy_service.odscode = test_data["ods_code"]
    mock_legacy_service.name = test_data["name"]

    is_supported, message = GPPracticeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == test_data["expected_result"]
    assert message == test_data["expected_message"]


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
    """
    Test that should_include_service returns True for a valid GP profile
    """
    mock_legacy_service.typeid = 100  # GP Practice type ID
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
    # When creating the transformer in the test:
    validation_issues = []
    transformer = GPPracticeTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service, validation_issues)

    assert len(result.organisation) == 1
    assert result.organisation[0].identifier_ODS_ODSCode == "A12345"
    assert result.organisation[0].name == "Test Service"

    assert len(result.location) == 1

    assert len(result.healthcare_service) == 1
    assert (
        result.healthcare_service[0].category == HealthcareServiceCategory.GP_SERVICES
    )
    assert (
        result.healthcare_service[0].type
        == HealthcareServiceType.GP_CONSULTATION_SERVICE
    )
