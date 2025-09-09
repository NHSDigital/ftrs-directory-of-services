import pytest

from pipeline.validation.field import EmailValidator


@pytest.fixture(autouse=True)
def email_validator() -> EmailValidator:
    return EmailValidator()


def test_valid_email() -> None:
    email = "test.user@nhs.net"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised == email
    assert len(result.issues) == 0


def test_invalid_email_not_string() -> None:
    email = 12345
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "email_not_string"


def test_invalid_email_length() -> None:
    email = "a" * 255 + "@nhs.net"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "invalid_length"


def test_invalid_email_format() -> None:
    email = "invalid-email-format"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "invalid_format"


def test_invalid_non_nhs_email() -> None:
    email = "test.user@gmail.com"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "not_nhs_email"


def test_valid_nhs_email_with_subdomain() -> None:
    email = "test.user@subdomain.nhs.net"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised == email
    assert len(result.issues) == 0
