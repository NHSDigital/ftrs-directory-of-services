import pytest

from pipeline.validation.field import PhoneNumberValidator


@pytest.fixture(autouse=True)
def validator() -> PhoneNumberValidator:
    return PhoneNumberValidator()


def test_phone_number_validator_returns_error_for_empty_string() -> None:
    result = validator.validate("")
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "empty"
    assert result.issues[0].diagnostics == "Phone number cannot be empty"


def test_phone_number_validator_returns_error_for_non_string() -> None:
    result = validator.validate(1234567890)
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "not_string"
    assert result.issues[0].diagnostics == "Phone number must be a string"


def test_phone_number_validator_returns_error_for_invalid_length() -> None:
    result = validator.validate("012345")
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "invalid_length"
    assert result.issues[0].diagnostics == "Phone number length is invalid"


def test_phone_number_validator_returns_error_for_invalid_format() -> None:
    result = validator.validate("017890123D5")
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "invalid_format"
    assert result.issues[0].diagnostics == "Phone number is invalid"


def test_phone_number_validator_returns_valid_for_correct_number() -> None:
    result = validator.validate("07123456789")
    assert result.sanitised == "07123456789"
    assert len(result.issues) == 0


def test_phone_number_validator_trims_and_converts_correct_number() -> None:
    result = validator.validate(" +44 7123 456 789 ")
    assert result.sanitised == "07123456789"
    assert len(result.issues) == 0
