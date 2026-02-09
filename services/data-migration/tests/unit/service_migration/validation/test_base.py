import pytest
from ftrs_common.logger import Logger
from ftrs_data_layer.domain.legacy import Service

from service_migration.validation.base import Validator
from service_migration.validation.field import FieldValidationResult
from service_migration.validation.service import ServiceValidator
from service_migration.validation.types import ValidationResult


class ConcreteValidator(Validator[dict]):
    """Concrete implementation of Validator for testing."""

    def validate(self, data: dict) -> ValidationResult:
        """Simple validation implementation."""
        return ValidationResult[dict](
            origin_record_id=data.get("id", 0),
            issues=[],
            sanitised=data,
        )


@pytest.fixture
def mock_logger() -> Logger:
    """Provide a mock logger for testing."""
    return Logger.get(service="test-validator")


class TestValidator:
    """Tests for Validator abstract base class."""

    def test_create_validator_with_logger(self, mock_logger: Logger) -> None:
        """Test creating Validator with logger."""
        validator = ConcreteValidator(logger=mock_logger)

        assert validator.logger is not None

    def test_validator_creates_default_logger_when_none(self) -> None:
        """Test Validator creates default logger when None passed."""
        validator = ConcreteValidator(logger=None)

        assert validator.logger is not None

    def test_validate_email_classmethod(self) -> None:
        """Test validate_email class method with valid email."""
        result = Validator.validate_email("test@nhs.net")

        assert isinstance(result, FieldValidationResult)
        assert result.sanitised == "test@nhs.net"
        assert len(result.issues) == 0

    def test_validate_email_with_custom_expression(self) -> None:
        """Test validate_email with custom expression."""
        result = Validator.validate_email(
            "invalid-email",
            expression="custom_email_field",
        )

        assert isinstance(result, FieldValidationResult)
        # Expression should be set in the issues
        if result.issues:
            assert result.issues[0].expression == ["custom_email_field"]

    def test_validate_email_with_invalid_email(self) -> None:
        """Test validate_email with invalid email."""
        result = Validator.validate_email("not-an-email")

        assert result.sanitised is None
        assert len(result.issues) > 0

    def test_validate_phone_number_classmethod(self) -> None:
        """Test validate_phone_number class method with valid phone."""
        result = Validator.validate_phone_number("07123456789")

        assert isinstance(result, FieldValidationResult)
        assert result.sanitised == "07123456789"
        assert len(result.issues) == 0

    def test_validate_phone_number_with_custom_expression(self) -> None:
        """Test validate_phone_number with custom expression."""
        result = Validator.validate_phone_number(
            "invalid",
            expression="custom_phone_field",
        )

        assert isinstance(result, FieldValidationResult)
        # Expression should be set in the issues
        if result.issues:
            assert result.issues[0].expression == ["custom_phone_field"]

    def test_validate_phone_number_with_invalid_number(self) -> None:
        """Test validate_phone_number with invalid number."""
        result = Validator.validate_phone_number("123")

        assert result.sanitised is None
        assert len(result.issues) > 0


@pytest.fixture
def valid_service() -> Service:
    """Provide a valid service for testing."""
    return Service(
        id=12345,
        uid="test-uid-12345",
        name="Test Service",
        publicname="Test Service",
        address="123 Main Street",
        town="Southampton",
        postcode="SO1 1AA",
        email="test@nhs.net",
        publicphone="01234567890",
        nonpublicphone="01234567891",
        typeid=100,
        statusid=1,
    )


class TestServiceValidator:
    """Tests for ServiceValidator class."""

    def test_create_service_validator(self, mock_logger: Logger) -> None:
        """Test creating ServiceValidator with logger."""
        validator = ServiceValidator(logger=mock_logger)

        assert validator.logger is not None

    def test_validate_returns_validation_result(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate returns ValidationResult."""
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        assert isinstance(result, ValidationResult)
        assert result.origin_record_id == valid_service.id

    def test_validate_with_valid_service(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with all valid fields."""
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        assert result.is_valid is True
        assert result.should_continue is True

    def test_validate_sanitises_email(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate sanitises email field."""
        valid_service.email = "test@nhs.net"
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        assert result.sanitised.email == "test@nhs.net"

    def test_validate_with_invalid_email(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with invalid email adds issues."""
        valid_service.email = "not-an-email"
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should have email validation issue
        email_issues = [
            i
            for i in result.issues
            if "email" in i.code.lower()
            or (i.expression and "email" in str(i.expression).lower())
        ]
        assert len(email_issues) > 0

    def test_validate_sanitises_publicphone(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate sanitises publicphone field."""
        valid_service.publicphone = " +44 7123 456 789 "
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        assert result.sanitised.publicphone == "07123456789"

    def test_validate_with_invalid_publicphone(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with invalid publicphone adds issues."""
        valid_service.publicphone = "123"
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should have phone validation issue
        phone_issues = [
            i
            for i in result.issues
            if "phone" in i.code.lower() or "length" in i.code.lower()
        ]
        assert len(phone_issues) > 0

    def test_validate_sanitises_nonpublicphone(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate sanitises nonpublicphone field."""
        valid_service.nonpublicphone = " 020 7946 0958 "
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        assert result.sanitised.nonpublicphone == "02079460958"

    def test_validate_with_invalid_nonpublicphone(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with invalid nonpublicphone adds issues."""
        valid_service.nonpublicphone = "abc"
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should have nonpublicphone validation issue
        assert len(result.issues) > 0

    def test_validate_with_none_email(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with None email."""
        valid_service.email = None
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should handle None email gracefully
        assert result is not None

    def test_validate_with_none_publicphone(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with None publicphone."""
        valid_service.publicphone = None
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should handle None phone gracefully
        assert result is not None

    def test_validate_with_none_nonpublicphone(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate with None nonpublicphone."""
        valid_service.nonpublicphone = None
        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should handle None phone gracefully
        assert result is not None

    def test_validate_accumulates_issues(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate accumulates issues from multiple fields."""
        valid_service.email = "bad-email"
        valid_service.publicphone = "123"
        valid_service.nonpublicphone = "abc"

        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        # Should have multiple issues
        assert len(result.issues) >= 2

    def test_validate_preserves_origin_record_id(
        self, mock_logger: Logger, valid_service: Service
    ) -> None:
        """Test validate preserves origin_record_id from service."""
        expected_id = 99999
        valid_service.id = expected_id

        validator = ServiceValidator(logger=mock_logger)
        result = validator.validate(valid_service)

        assert result.origin_record_id == expected_id
