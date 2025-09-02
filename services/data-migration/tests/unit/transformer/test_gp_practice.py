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
            "service_type_id": 100,
            "ods_code": "H98765",
            "name": "SAS - Name",
            "expected_result": False,
            "expected_message": "Service fits GP Special Allocation Scheme criteria",
        },  # Invalid since it's GP Special Allocation Scheme
        {
            "service_type_id": 100,
            "ods_code": "H98765",
            "name": "Special Allocation Scheme - Name",
            "expected_result": False,
            "expected_message": "Service fits GP Special Allocation Scheme criteria",
        },  # Invalid since it's GP Special Allocation Scheme
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
    mock_legacy_service.publicname = "GP - Remove this text"  # GP Public Name
    mock_legacy_service.typeid = 100  # GP Practice type ID
    mock_legacy_service.odscode = "A12345"  # Valid ODS code
    mock_legacy_service.statusid = 1  # Active status

    # When creating the transformer in the test:
    validation_issues = []
    transformer = GPPracticeTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service, validation_issues)

    assert len(result.organisation) == 1
    assert result.organisation[0].identifier_ODS_ODSCode == "A12345"
    assert result.organisation[0].name == "GP"

    assert len(result.location) == 1

    assert len(result.healthcare_service) == 1
    assert (
        result.healthcare_service[0].category == HealthcareServiceCategory.GP_SERVICES
    )
    assert (
        result.healthcare_service[0].type
        == HealthcareServiceType.GP_CONSULTATION_SERVICE
    )


def test_transform_with_empty_publicname(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
) -> None:
    with pytest.raises(ValueError, match="publicname is not set"):
        """
        Test that transform method raises and exception when it transforms a GP practice service without a publicname.
        """
        mock_legacy_service.name = "GP - Text Not Removed"  # GP Name
        mock_legacy_service.publicname = None
        mock_legacy_service.typeid = 100  # GP Practice type ID
        mock_legacy_service.odscode = "A12345"  # Valid ODS code
        mock_legacy_service.statusid = 1  # Active status
        validation_issues = []
        transformer = GPPracticeTransformer(MockLogger(), mock_metadata_cache)
        transformer.transform(mock_legacy_service, validation_issues)
