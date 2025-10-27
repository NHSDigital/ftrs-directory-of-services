import pytest

from service_migration.validation.field import EmailValidator


@pytest.fixture
def email_validator() -> EmailValidator:
    return EmailValidator()


def test_valid_email(email_validator: EmailValidator) -> None:
    email = "test.user@nhs.net"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised == email
    assert len(result.issues) == 0


def test_invalid_email_not_string(email_validator: EmailValidator) -> None:
    email = 12345
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "email_not_string"


def test_invalid_email_length(email_validator: EmailValidator) -> None:
    email = "a" * 255 + "@nhs.net"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "invalid_length"


def test_invalid_email_format(email_validator: EmailValidator) -> None:
    email = "invalid-email-format"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "invalid_format"


def test_invalid_non_nhs_email(email_validator: EmailValidator) -> None:
    email = "test.user@gmail.com"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised is None
    assert len(result.issues) == 1
    assert result.issues[0].code == "not_nhs_email"


def test_valid_nhs_email_with_subdomain(email_validator: EmailValidator) -> None:
    email = "test.user@subdomain.nhs.net"
    result = email_validator.validate(email)
    assert result is not None
    assert result.sanitised == email
    assert len(result.issues) == 0
