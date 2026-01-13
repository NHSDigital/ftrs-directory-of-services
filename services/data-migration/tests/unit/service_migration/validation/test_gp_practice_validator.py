import pytest
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.legacy import Service

from service_migration.validation.service import GPPracticeValidator
from service_migration.validation.types import ValidationResult


@pytest.fixture
def mock_logger() -> Logger:
    """Provide a mock logger for testing."""
    return Logger.get(service="test-gp-practice-validator")


@pytest.fixture
def gp_practice_validator(mock_logger: Logger) -> GPPracticeValidator:
    """Provide a GPPracticeValidator instance with logger."""
    return GPPracticeValidator(logger=mock_logger)


@pytest.fixture
def valid_service() -> Service:
    """Provide a valid GP practice service."""
    return Service(
        id=12345,
        uid="test-uid-12345",
        name="Test GP Practice",
        publicname="Test GP Practice",
        address="123 Main Street$Building A$Hampshire",
        town="Southampton",
        postcode="SO1 1AA",
        email="test@nhs.net",
        publicphone="01234567890",
        nonpublicphone="01234567891",
        typeid=100,
        statusid=1,
    )


# ============================================================================
# validate() - Integration Tests
# ============================================================================


def test_validate_with_all_valid_fields(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation passes with all valid fields."""
    expected_id = 12345
    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert isinstance(result, ValidationResult)
    assert result.origin_record_id == expected_id
    assert result.is_valid is True
    assert result.should_continue is True
    assert len(result.issues) == 0
    assert result.sanitised.publicname == "Test GP Practice"
    assert result.sanitised.address is not None


def test_validate_with_invalid_name_and_all_address_fields_missing(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation captures multiple issues when all address fields missing."""
    valid_service.publicname = ""
    valid_service.address = ""
    valid_service.town = ""
    valid_service.postcode = ""
    expected_issue_count = 2

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid is False
    assert result.should_continue is False
    assert len(result.issues) == expected_issue_count

    # Check for publicname error
    name_issue = next(i for i in result.issues if i.code == "publicname_required")
    assert name_issue.severity == "error"
    assert name_issue.expression == ["publicname"]

    # Check for address error fatal (as needed to create location)
    address_issue = next(i for i in result.issues if i.code == "address_required")
    assert address_issue.severity == "fatal"
    assert address_issue.expression == ["address"]


def test_validate_with_fatal_address_issue(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation stops processing on fatal address issue."""
    valid_service.address = "Not Available"
    valid_service.town = ""
    valid_service.postcode = ""

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid is False
    assert result.should_continue is False
    assert len(result.issues) >= 1

    # Check for fatal address issue
    fatal_issue = next(i for i in result.issues if i.code == "invalid_address")
    assert fatal_issue.severity == "fatal"
    assert (
        fatal_issue.diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )


def test_validate_with_partial_address_town_only(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation passes when only town is provided."""
    valid_service.address = ""
    valid_service.town = "Southampton"
    valid_service.postcode = ""

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid is False
    assert result.should_continue is False
    assert len(result.issues) >= 1

    # Check for fatal address issue
    fatal_issue = next(i for i in result.issues if i.code == "invalid_address")
    assert fatal_issue.severity == "fatal"
    assert (
        fatal_issue.diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )


def test_validate_with_partial_address_postcode_only(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation passes when only postcode is provided."""
    valid_service.address = ""
    valid_service.town = ""
    valid_service.postcode = "SO1 1AA"

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid is False
    assert result.should_continue is False
    assert len(result.issues) >= 1

    # Check for fatal address issue
    fatal_issue = next(i for i in result.issues if i.code == "invalid_address")
    assert fatal_issue.severity == "fatal"
    assert (
        fatal_issue.diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )


def test_validate_with_partial_address_town_and_postcode(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation passes when town and postcode are provided without address."""
    valid_service.address = ""
    valid_service.town = "Southampton"
    valid_service.postcode = "SO1 1AA"

    result = gp_practice_validator.validate(valid_service)

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid is False
    assert result.should_continue is False
    assert len(result.issues) >= 1

    # Check for fatal address issue
    fatal_issue = next(i for i in result.issues if i.code == "invalid_address")
    assert fatal_issue.severity == "fatal"
    assert (
        fatal_issue.diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )


def test_validate_with_partial_valid_data(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test validation with some valid and some invalid fields."""
    valid_service.publicname = "Valid Name"
    valid_service.address = ""
    valid_service.town = ""
    valid_service.postcode = ""
    valid_service.email = "invalid-email"
    expected_issue_count = 2

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid is False
    assert result.should_continue is False
    assert len(result.issues) == expected_issue_count

    # Should have issues for address and email, but not name
    assert any(i.code == "address_required" for i in result.issues)
    assert any("email" in i.expression for i in result.issues)
    assert not any(i.code == "publicname_required" for i in result.issues)


def test_validate_collects_all_issues(
    gp_practice_validator: GPPracticeValidator, valid_service: Service
) -> None:
    """Test that all validation issues are collected."""
    valid_service.publicname = ""
    valid_service.address = ""
    valid_service.town = ""
    valid_service.postcode = ""
    valid_service.email = "invalid-email"
    valid_service.publicphone = "invalid-phone"
    expected_issue_count = 4

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    # Should have issues for: name, address, email, publicphone
    assert len(result.issues) >= expected_issue_count
    issue_codes = {issue.code for issue in result.issues}
    assert "publicname_required" in issue_codes
    assert "address_required" in issue_codes
    assert any("email" in issue.expression for issue in result.issues)
    assert any("publicphone" in issue.expression for issue in result.issues)


@pytest.mark.parametrize(
    "name,address,town,postcode,expected_valid,expected_continue",
    [
        ("Valid Name", "123 Main St$Hampshire", "Town", "POST", True, True),
        ("", "123 Main St$Hampshire", "Town", "POST", False, True),
        ("Valid Name", "", "Town", "POST", False, False),
        ("Valid Name", "", "", "POST", False, False),
        ("Valid Name", "", "Town", "", False, False),
        ("Valid Name", "", "", "", False, False),
        ("", "", "", "", False, False),
        ("Valid Name", "Not Available", "", "", False, False),
        ("", "Not Available", "", "", False, False),
    ],
)
def test_validate_is_valid_and_should_continue_logic(
    gp_practice_validator: GPPracticeValidator,
    valid_service: Service,
    name: str,
    address: str,
    town: str,
    postcode: str,
    expected_valid: bool,
    expected_continue: bool,
) -> None:
    """Test is_valid and should_continue properties with various inputs."""
    valid_service.publicname = name
    valid_service.address = address
    valid_service.town = town
    valid_service.postcode = postcode

    result = gp_practice_validator.validate(valid_service)

    assert result is not None
    assert result.is_valid == expected_valid
    assert result.should_continue == expected_continue


# ============================================================================
# validate_name() - Unit Tests
# ============================================================================


def test_valid_name(gp_practice_validator: GPPracticeValidator) -> None:
    """Test name validation passes with valid name."""
    name = "Test GP Practice"
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised == name
    assert len(result.issues) == 0


def test_valid_name_with_hyphen(gp_practice_validator: GPPracticeValidator) -> None:
    """Test name validation strips content after hyphen."""
    name = "Test GP Practice - Extra Info"
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised == "Test GP Practice"
    assert len(result.issues) == 0


def test_valid_name_with_trailing_whitespace(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test name validation removes trailing whitespace."""
    name = "Test GP Practice   "
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised == "Test GP Practice"
    assert len(result.issues) == 0


def test_valid_name_with_hyphen_and_trailing_whitespace(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test name validation handles hyphen and whitespace."""
    name = "Test GP Practice - Extra   "
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised == "Test GP Practice"
    assert len(result.issues) == 0


def test_invalid_name_empty_string(gp_practice_validator: GPPracticeValidator) -> None:
    """Test name validation fails with empty string."""
    name = ""
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "error"
    assert result.issues[0].code == "publicname_required"
    assert result.issues[0].diagnostics == "Public name is required for GP practices"
    assert result.issues[0].expression == ["publicname"]


def test_invalid_name_none(gp_practice_validator: GPPracticeValidator) -> None:
    """Test name validation fails with None."""
    name = None
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "error"
    assert result.issues[0].code == "publicname_required"


def test_invalid_name_whitespace_only(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test name validation fails with whitespace only."""
    name = "   "
    result = gp_practice_validator.validate_name(name)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "error"
    assert result.issues[0].code == "publicname_empty_after_sanitization"
    assert result.issues[0].diagnostics == "Name is empty after removing suffix"
    assert result.issues[0].expression == ["publicname"]


@pytest.mark.parametrize(
    "input_name,expected_sanitised",
    [
        ("GP Practice", "GP Practice"),
        ("GP Practice - Branch", "GP Practice"),
        ("GP Practice -", "GP Practice -"),
        ("GP Practice- Extra", "GP Practice- Extra"),
        ("GP Practice  - Extra  ", "GP Practice"),
        ("ABC", "ABC"),
        ("A-B-C", "A-B-C"),
        # GP prefix removal tests
        ("GP - Practice Name", "Practice Name"),
        ("GP -Practice Name", "Practice Name"),
        ("GP- Practice Name", "Practice Name"),
        ("GP-Practice Name", "Practice Name"),
        ("GP - Main Surgery", "Main Surgery"),
        ("GP-Surgery", "Surgery"),
    ],
)
def test_validate_name_with_various_formats(
    gp_practice_validator: GPPracticeValidator,
    input_name: str,
    expected_sanitised: str,
) -> None:
    """Test name validation with various input formats."""
    result = gp_practice_validator.validate_name(input_name)

    assert result is not None
    assert result.sanitised == expected_sanitised
    assert len(result.issues) == 0


# ============================================================================
# validate_location() - Unit Tests
# ============================================================================


def test_valid_location_full_address(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation passes with valid full address."""
    address = "123 Main Street$Building A$Hampshire"
    town = "Southampton"
    postcode = "SO1 1AA"

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is not None
    assert result.sanitised.line1 == "123 Main Street"
    assert result.sanitised.line2 == "Building A"
    assert result.sanitised.county == "Hampshire"
    assert result.sanitised.town == "Southampton"
    assert result.sanitised.postcode == "SO1 1AA"
    assert len(result.issues) == 0


def test_valid_location_town_only(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation passes with town only."""
    address = ""
    town = "Southampton"
    postcode = ""

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "fatal"
    assert result.issues[0].code == "invalid_address"
    assert (
        result.issues[0].diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )
    assert result.issues[0].expression == ["address"]


def test_valid_location_postcode_only(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation passes with postcode only."""
    address = ""
    town = ""
    postcode = "SO1 1AA"

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "fatal"
    assert result.issues[0].code == "invalid_address"
    assert (
        result.issues[0].diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )
    assert result.issues[0].expression == ["address"]


def test_valid_location_town_and_postcode(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation passes with town and postcode."""
    address = ""
    town = "Southampton"
    postcode = "SO1 1AA"

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "fatal"
    assert result.issues[0].code == "invalid_address"
    assert (
        result.issues[0].diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )
    assert result.issues[0].expression == ["address"]


def test_valid_location_multipart_address(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation with multi-segment address."""
    address = "123 Main St$Building A$Floor 2$Hampshire"
    town = "Southampton"
    postcode = "SO1 1AA"

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is not None
    assert result.sanitised.line1 == "123 Main St"
    assert result.sanitised.line2 == "Building A"
    assert result.sanitised.county == "Hampshire"
    assert len(result.issues) == 0


def test_invalid_location_all_fields_empty(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation fails when all fields are empty."""
    address = ""
    town = ""
    postcode = ""

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "fatal"
    assert result.issues[0].code == "address_required"
    assert (
        result.issues[0].diagnostics
        == "Address is required for GP practices to create a location"
    )
    assert result.issues[0].expression == ["address"]


def test_invalid_location_all_fields_none(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation fails when all fields are None."""
    address = None
    town = None
    postcode = None

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "address_required"


def test_invalid_location_not_available_no_town_postcode(
    gp_practice_validator: GPPracticeValidator,
) -> None:
    """Test location validation fails with 'Not Available' address and no town/postcode."""
    address = "Not Available"
    town = ""
    postcode = ""

    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "fatal"
    assert result.issues[0].code == "invalid_address"
    assert (
        result.issues[0].diagnostics
        == "Address was invalid or incomplete, could not be formatted for GP practices to create a location"
    )
    assert result.issues[0].expression == ["address"]


@pytest.mark.parametrize(
    "invalid_address,town,postcode",
    [
        ("Not Available", "", ""),
        ("Not available", "", ""),
    ],
)
def test_invalid_location_various_placeholders_no_fallback(
    gp_practice_validator: GPPracticeValidator,
    invalid_address: str,
    town: str,
    postcode: str,
) -> None:
    """Test location validation fails with various invalid address indicators."""
    result = gp_practice_validator.validate_location(invalid_address, town, postcode)

    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].severity == "fatal"
    assert result.issues[0].code == "invalid_address"


@pytest.mark.parametrize(
    "address,town,postcode,should_pass",
    [
        ("123 Main St", "Town", "POST", True),
        ("123 Main St", "", "POST", True),
        ("123 Main St", "Town", "", True),
        ("123 Main St", "", "", True),
        ("", "Town", "POST", False),
        ("", "Town", "", False),
        ("", "", "POST", False),
        ("", "", "", False),
        ("Not Available", "Town", "POST", False),
        ("Not Available", "Town", "", False),
        ("Not Available", "", "POST", False),
        ("Not Available", "", "", False),
    ],
)
def test_location_validation_with_combinations(
    gp_practice_validator: GPPracticeValidator,
    address: str,
    town: str,
    postcode: str,
    should_pass: bool,
) -> None:
    """Test location validation with various address/town/postcode combinations."""
    result = gp_practice_validator.validate_location(address, town, postcode)

    assert result is not None
    if should_pass:
        assert result.sanitised is not None
        assert len(result.issues) == 0
    else:
        assert result.sanitised is None
        assert len(result.issues) >= 1
