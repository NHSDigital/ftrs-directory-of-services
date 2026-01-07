import pytest
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain.legacy.data_models import ServiceData

from service_migration.dependencies import ServiceMigrationDependencies
from service_migration.transformer.gp_practice import GPPracticeTransformer


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
    mock_legacy_service: ServiceData,
    service_type_id: int,
    ods_code: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """
    Test that is_service_supported returns True for a valid GP profile
    """
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = ods_code

    is_supported, message = GPPracticeTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == expected_result
    assert message == expected_message


@pytest.mark.parametrize(
    "status_id, expected_result, expected_message",
    [
        (1, True, None),  # Active service
        (2, False, "Service is not active"),
        (3, False, "Service is not active"),
    ],
)
def test_should_include_service(
    mock_legacy_service: ServiceData,
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
    mock_dependencies: ServiceMigrationDependencies,
    mock_legacy_service: ServiceData,
) -> None:
    """
    Test that transform method correctly transforms a GP practice service.
    """
    mock_legacy_service.publicname = "GP - Remove this text"  # GP Public Name
    mock_legacy_service.typeid = 100  # GP Practice type ID
    mock_legacy_service.odscode = "A12345"  # Valid ODS code
    mock_legacy_service.statusid = 1  # Active status

    # When creating the transformer in the test:
    transformer = GPPracticeTransformer(mock_dependencies)

    validation_result = transformer.validator.validate(mock_legacy_service)
    result = transformer.transform(validation_result.sanitised)

    assert result.organisation is not None
    assert result.organisation.identifier_ODS_ODSCode == "A12345"
    assert result.organisation.name == "GP"

    assert result.location is not None

    assert result.healthcare_service is not None
    assert result.healthcare_service.category == HealthcareServiceCategory.GP_SERVICES
    assert (
        result.healthcare_service.type == HealthcareServiceType.GP_CONSULTATION_SERVICE
    )

    assert result.validation_issues == validation_result.issues


# TODO: Replace with equivalent fatal validation test
# def test_transform_with_empty_publicname(
#     mock_legacy_service: ServiceData,
#     mock_metadata_cache: DoSMetadataCache,
# ) -> None:
#     """
#     Test that transform method raises and exception when it transforms a GP practice service without a publicname.
#     """
#         mock_legacy_service.name = "GP - Text Not Removed"  # GP Name
#         mock_legacy_service.publicname = None
#         mock_legacy_service.typeid = 100  # GP Practice type ID
#         mock_legacy_service.odscode = "A12345"  # Valid ODS code
#         mock_legacy_service.statusid = 1  # Active status
#         validation_issues = []
#         transformer = GPPracticeTransformer(MockLogger(), mock_metadata_cache)
#         transformer.transform(mock_legacy_service, validation_issues)
