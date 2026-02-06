import pytest

from service_migration.validation.field.base import (
    FieldValidationResult,
    FieldValidator,
)
from service_migration.validation.types import ValidationIssue


class TestFieldValidationResult:
    """Tests for FieldValidationResult model."""

    def test_create_field_validation_result(self) -> None:
        """Test creating FieldValidationResult with all fields."""
        result = FieldValidationResult[str](
            original="original_value",
            sanitised="sanitised_value",
            issues=[],
        )

        assert result.original == "original_value"
        assert result.sanitised == "sanitised_value"
        assert result.issues == []

    def test_field_validation_result_with_none_values(self) -> None:
        """Test FieldValidationResult with None values using Optional type."""
        result = FieldValidationResult[str | None](
            original=None,
            sanitised=None,
            issues=[],
        )

        assert result.original is None
        assert result.sanitised is None

    def test_field_validation_result_with_issues(self) -> None:
        """Test FieldValidationResult with validation issues."""
        issues = [
            ValidationIssue(
                severity="error",
                code="test_error",
                diagnostics="Test error message",
                expression=["field_name"],
            ),
        ]

        result = FieldValidationResult[str | None](
            original="bad_value",
            sanitised=None,
            issues=issues,
        )

        assert len(result.issues) == 1
        assert result.issues[0].code == "test_error"
        assert result.issues[0].severity == "error"

    def test_field_validation_result_with_int_type(self) -> None:
        """Test FieldValidationResult with integer type."""
        result = FieldValidationResult[int](
            original=100,
            sanitised=200,
            issues=[],
        )

        assert result.original == 100
        assert result.sanitised == 200

    def test_field_validation_result_model_dump_json(self) -> None:
        """Test FieldValidationResult serialization to JSON."""
        result = FieldValidationResult[str](
            original="original",
            sanitised="sanitised",
            issues=[
                ValidationIssue(
                    severity="warning",
                    code="field_warning",
                    diagnostics="Warning message",
                ),
            ],
        )

        dumped = result.model_dump(mode="json")

        assert dumped["original"] == "original"
        assert dumped["sanitised"] == "sanitised"
        assert len(dumped["issues"]) == 1
        assert dumped["issues"][0]["code"] == "field_warning"


class ConcreteFieldValidator(FieldValidator[str]):
    """Concrete implementation of FieldValidator for testing."""

    def validate(self, data: str) -> FieldValidationResult[str]:
        """Simple validation that checks if data is non-empty."""
        if not data:
            self.add_issue(
                severity="error",
                code="empty_value",
                diagnostics="Value cannot be empty",
                value=data,
            )
            return FieldValidationResult(
                original=data,
                sanitised=None,
                issues=self.issues,
            )

        return FieldValidationResult(
            original=data,
            sanitised=data.strip(),
            issues=self.issues,
        )


class TestFieldValidator:
    """Tests for FieldValidator abstract base class."""

    def test_create_field_validator_without_expression(self) -> None:
        """Test creating FieldValidator without expression."""
        validator = ConcreteFieldValidator()

        assert validator.expression is None
        assert validator.issues == []

    def test_create_field_validator_with_expression(self) -> None:
        """Test creating FieldValidator with expression."""
        validator = ConcreteFieldValidator(expression="test_field")

        assert validator.expression == "test_field"
        assert validator.issues == []

    def test_add_issue_with_expression_from_init(self) -> None:
        """Test add_issue uses expression from __init__."""
        validator = ConcreteFieldValidator(expression="default_field")
        validator.add_issue(
            severity="error",
            code="test_code",
            diagnostics="Test message",
        )

        assert len(validator.issues) == 1
        assert validator.issues[0].expression == ["default_field"]

    def test_add_issue_with_custom_expression(self) -> None:
        """Test add_issue with custom expression overrides default."""
        validator = ConcreteFieldValidator(expression="default_field")
        validator.add_issue(
            severity="error",
            code="test_code",
            diagnostics="Test message",
            expression="custom_field",
        )

        assert len(validator.issues) == 1
        assert validator.issues[0].expression == ["custom_field"]

    def test_add_issue_with_value(self) -> None:
        """Test add_issue with value parameter."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="warning",
            code="value_warning",
            diagnostics="Warning about value",
            value="problematic_value",
        )

        assert len(validator.issues) == 1
        assert validator.issues[0].value == "problematic_value"

    def test_add_issue_without_expression(self) -> None:
        """Test add_issue without any expression."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="error",
            code="test_code",
            diagnostics="Test message",
        )

        assert len(validator.issues) == 1
        assert validator.issues[0].expression is None

    def test_add_multiple_issues(self) -> None:
        """Test adding multiple issues to validator."""
        validator = ConcreteFieldValidator(expression="field")
        validator.add_issue(
            severity="error",
            code="error_1",
            diagnostics="First error",
        )
        validator.add_issue(
            severity="warning",
            code="warning_1",
            diagnostics="First warning",
        )
        validator.add_issue(
            severity="information",
            code="info_1",
            diagnostics="Information",
        )

        assert len(validator.issues) == 3
        assert validator.issues[0].code == "error_1"
        assert validator.issues[1].code == "warning_1"
        assert validator.issues[2].code == "info_1"

    def test_is_valid_with_no_issues(self) -> None:
        """Test is_valid returns True when no issues."""
        validator = ConcreteFieldValidator()

        assert validator.is_valid is True

    def test_is_valid_with_warning_issues(self) -> None:
        """Test is_valid returns True when only warnings."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="warning",
            code="warning",
            diagnostics="Warning message",
        )

        assert validator.is_valid is True

    def test_is_valid_with_information_issues(self) -> None:
        """Test is_valid returns True when only information issues."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="information",
            code="info",
            diagnostics="Info message",
        )

        assert validator.is_valid is True

    def test_is_valid_with_error_issues(self) -> None:
        """Test is_valid returns False when error issues present."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="error",
            code="error",
            diagnostics="Error message",
        )

        assert validator.is_valid is False

    def test_is_valid_with_fatal_issues(self) -> None:
        """Test is_valid returns False when fatal issues present."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="fatal",
            code="fatal",
            diagnostics="Fatal message",
        )

        assert validator.is_valid is False

    def test_is_valid_with_mixed_issues(self) -> None:
        """Test is_valid returns False when mix includes error."""
        validator = ConcreteFieldValidator()
        validator.add_issue(
            severity="warning",
            code="warning",
            diagnostics="Warning",
        )
        validator.add_issue(
            severity="error",
            code="error",
            diagnostics="Error",
        )

        assert validator.is_valid is False

    def test_validate_method_success(self) -> None:
        """Test concrete validate method with valid data."""
        validator = ConcreteFieldValidator(expression="test_field")
        result = validator.validate("  valid data  ")

        assert result.original == "  valid data  "
        assert result.sanitised == "valid data"
        assert len(result.issues) == 0

    def test_validate_method_failure(self) -> None:
        """Test concrete validate method with invalid data."""
        validator = ConcreteFieldValidator(expression="test_field")
        result = validator.validate("")

        assert result.original == ""
        assert result.sanitised is None
        assert len(result.issues) == 1
        assert result.issues[0].code == "empty_value"

    def test_issues_persist_across_validations(self) -> None:
        """Test that issues list persists across multiple validations."""
        validator = ConcreteFieldValidator()

        # First validation fails
        validator.validate("")
        assert len(validator.issues) == 1

        # Issues accumulate (this is the actual behavior)
        validator.validate("")
        assert len(validator.issues) == 2

    def test_all_severity_levels(self) -> None:
        """Test adding issues with all severity levels."""
        validator = ConcreteFieldValidator()

        severities = ["fatal", "error", "warning", "information", "success"]
        for i, severity in enumerate(severities):
            validator.add_issue(
                severity=severity,  # type: ignore
                code=f"code_{i}",
                diagnostics=f"Message {i}",
            )

        assert len(validator.issues) == 5
        for i, severity in enumerate(severities):
            assert validator.issues[i].severity == severity
