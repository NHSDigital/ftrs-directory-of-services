import pytest
from ftrs_common.mocks.mock_logger import MockLogger
from ftrs_data_layer.domain import HealthcareServiceCategory, HealthcareServiceType
from ftrs_data_layer.domain.legacy import Service

from pipeline.transformer.gp_enhanced_access import GPEnhancedAccessTransformer
from pipeline.utils.cache import DoSMetadataCache


@pytest.mark.parametrize(
    "service_type_id, ods_code, expected_result, expected_message",
    [
        # Valid cases
        (136, "U12345", True, None),  # Valid GP Access Hub
        (152, "U67890", True, None),  # Valid PCN Enhanced Service
        (
            136,
            "U12345ABC",
            True,
            None,
        ),  # Valid with extra characters (first 6 retained)
        # Invalid service type
        (
            100,
            "U12345",
            False,
            "Service type is not GP Access Hub (136) or Primary Care Network (PCN) Enhanced Service (152)",
        ),
        (
            200,
            "U12345",
            False,
            "Service type is not GP Access Hub (136) or Primary Care Network (PCN) Enhanced Service (152)",
        ),
        # Missing ODS code
        (136, None, False, "Service does not have an ODS code"),
        (152, "", False, "Service does not have an ODS code"),
        # Invalid ODS code format
        (
            136,
            "A12345",
            False,
            "ODS code (first 6 characters) does not match the required format (Unnnnn)",
        ),
        (
            136,
            "U1234",
            False,
            "ODS code (first 6 characters) does not match the required format (Unnnnn)",
        ),
        (
            136,
            "U1234A",
            False,
            "ODS code (first 6 characters) does not match the required format (Unnnnn)",
        ),
        (
            136,
            "12345U",
            False,
            "ODS code (first 6 characters) does not match the required format (Unnnnn)",
        ),
        (
            152,
            "UU1234",
            False,
            "ODS code (first 6 characters) does not match the required format (Unnnnn)",
        ),
        (
            136,
            "u12345",
            False,
            "ODS code (first 6 characters) does not match the required format (Unnnnn)",
        ),  # lowercase
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
    Test that is_service_supported correctly validates GP Enhanced Access services.
    """
    mock_legacy_service.typeid = service_type_id
    mock_legacy_service.odscode = ods_code

    is_supported, message = GPEnhancedAccessTransformer.is_service_supported(
        mock_legacy_service
    )

    assert is_supported == expected_result
    assert message == expected_message


@pytest.mark.parametrize(
    "status_id, service_name, expected_result, expected_message",
    [
        # Valid cases - active status
        (1, "Enhanced Access Service", True, None),
        (1, "Primary Care Network Service", True, None),
        (1, None, True, None),  # No name
        (1, "", True, None),  # Empty name
        (1, "GP Protected Learning", True, None),  # Similar but not exact pattern
        (1, "ARI Service", True, None),  # Missing dash and space
        (1, "Primary Care CAS", True, None),  # Missing dash and space
        # Invalid status
        (2, "Enhanced Access Service", False, "Service is not active"),
        (3, "Enhanced Access Service", False, "Service is not active"),
        (0, "Enhanced Access Service", False, "Service is not active"),
        # Excluded name patterns
        (
            1,
            "GP Protected Learning Time (PLT) Service",
            False,
            "Service name contains excluded pattern: 'GP Protected Learning Time (PLT)'",
        ),
        (
            1,
            "ARI - Acute Respiratory Infection",
            False,
            "Service name contains excluded pattern: 'ARI - '",
        ),
        (
            1,
            "Primary Care CAS - Clinical Assessment",
            False,
            "Service name contains excluded pattern: 'Primary Care CAS - '",
        ),
        (
            1,
            "Some ARI - Service",
            False,
            "Service name contains excluded pattern: 'ARI - '",
        ),
        (
            1,
            "Enhanced GP Protected Learning Time (PLT)",
            False,
            "Service name contains excluded pattern: 'GP Protected Learning Time (PLT)'",
        ),
        (
            1,
            "Test Primary Care CAS - Service",
            False,
            "Service name contains excluded pattern: 'Primary Care CAS - '",
        ),
    ],
)
def test_should_include_service(
    mock_legacy_service: Service,
    status_id: int,
    service_name: str | None,
    expected_result: bool,
    expected_message: str | None,
) -> None:
    """
    Test that should_include_service correctly validates status and name criteria.
    """
    mock_legacy_service.typeid = 136  # Valid type ID
    mock_legacy_service.odscode = "U12345"  # Valid ODS code
    mock_legacy_service.statusid = status_id
    mock_legacy_service.name = service_name

    should_include, message = GPEnhancedAccessTransformer.should_include_service(
        mock_legacy_service
    )

    assert should_include == expected_result
    assert message == expected_message


@pytest.mark.parametrize(
    "test_data",
    [
        {
            "service_type_id": 136,
            "ods_code": "U12345",
            "service_name": "GP Enhanced Access Hub",
            "expected_category": HealthcareServiceCategory.GP_SERVICES,
            "expected_type": HealthcareServiceType.PCN_SERVICE,
        },  # GP Access Hub
        {
            "service_type_id": 152,
            "ods_code": "U67890",
            "service_name": "Primary Care Network Enhanced Access",
            "expected_category": HealthcareServiceCategory.GP_SERVICES,
            "expected_type": HealthcareServiceType.PCN_SERVICE,
        },  # PCN Enhanced Service
    ],
)
def test_transform_services(
    mock_legacy_service: Service,
    mock_metadata_cache: DoSMetadataCache,
    test_data: dict,
) -> None:
    """
    Test that transform method correctly transforms different GP Enhanced Access services.
    """
    mock_legacy_service.typeid = test_data["service_type_id"]
    mock_legacy_service.odscode = test_data["ods_code"]
    mock_legacy_service.statusid = 1  # Active status
    mock_legacy_service.name = test_data["service_name"]

    transformer = GPEnhancedAccessTransformer(MockLogger(), mock_metadata_cache)
    result = transformer.transform(mock_legacy_service)

    # Verify basic transformation - only healthcare service is created
    assert len(result.organisation) == 0  # Empty list
    assert len(result.location) == 0  # Empty list
    assert len(result.healthcare_service) == 1

    # Verify healthcare service properties
    assert result.healthcare_service[0].category == test_data["expected_category"]
    assert result.healthcare_service[0].type == test_data["expected_type"]
    assert result.healthcare_service[0].id is not None

    # Verify no organisation or location linkage
    assert result.healthcare_service[0].providedBy is None
    assert result.healthcare_service[0].location is None


@pytest.mark.parametrize(
    "ods_code, expected_match, pattern_description",
    [
        # Valid patterns
        ("U12345", True, "Standard valid format"),
        ("U00000", True, "All zeros"),
        ("U99999", True, "All nines"),
        ("U54321", True, "Mixed digits"),
        # Invalid patterns
        ("A12345", False, "Wrong starting letter"),
        ("B12345", False, "Another wrong starting letter"),
        ("U1234", False, "Too short (5 chars)"),
        ("U123456", False, "Too long (7 chars)"),
        ("u12345", False, "Lowercase U"),
        ("U12A45", False, "Letter in digit position"),
        ("U1B345", False, "Letter in second digit"),
        ("U123C5", False, "Letter in fourth digit"),
        ("12345U", False, "U at end instead of start"),
        ("UU1234", False, "Double U"),
        ("U-1234", False, "Hyphen in code"),
        ("U 1234", False, "Space in code"),
        ("", False, "Empty string"),
        ("UABCDE", False, "All letters after U"),
        ("123456", False, "No U at all"),
    ],
)
def test_regex_pattern_validation(
    ods_code: str, expected_match: bool, pattern_description: str
) -> None:
    """
    Test the ODS code regex pattern with various inputs.
    """
    regex = GPEnhancedAccessTransformer.GP_ENHANCED_ACCESS_ODS_CODE_REGEX

    match_result = regex.match(ods_code)

    if expected_match:
        assert match_result is not None, (
            f"Expected '{ods_code}' to match ({pattern_description})"
        )
    else:
        assert match_result is None, (
            f"Expected '{ods_code}' to NOT match ({pattern_description})"
        )
