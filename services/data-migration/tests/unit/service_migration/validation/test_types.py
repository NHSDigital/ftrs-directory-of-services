from service_migration.validation.types import (
    ValidationIssue,
    ValidationResult,
)


class TestValidationIssueSeverity:
    """Tests for ValidationIssueSeverity type."""

    def test_valid_severity_fatal(self) -> None:
        """Test that 'fatal' is a valid severity."""
        issue = ValidationIssue(
            severity="fatal",
            code="test_code",
            diagnostics="Test message",
        )
        assert issue.severity == "fatal"

    def test_valid_severity_error(self) -> None:
        """Test that 'error' is a valid severity."""
        issue = ValidationIssue(
            severity="error",
            code="test_code",
            diagnostics="Test message",
        )
        assert issue.severity == "error"

    def test_valid_severity_warning(self) -> None:
        """Test that 'warning' is a valid severity."""
        issue = ValidationIssue(
            severity="warning",
            code="test_code",
            diagnostics="Test message",
        )
        assert issue.severity == "warning"

    def test_valid_severity_information(self) -> None:
        """Test that 'information' is a valid severity."""
        issue = ValidationIssue(
            severity="information",
            code="test_code",
            diagnostics="Test message",
        )
        assert issue.severity == "information"

    def test_valid_severity_success(self) -> None:
        """Test that 'success' is a valid severity."""
        issue = ValidationIssue(
            severity="success",
            code="test_code",
            diagnostics="Test message",
        )
        assert issue.severity == "success"


class TestValidationIssue:
    """Tests for ValidationIssue model."""

    def test_create_validation_issue_minimal(self) -> None:
        """Test creating ValidationIssue with required fields only."""
        issue = ValidationIssue(
            severity="error",
            code="test_code",
            diagnostics="Test diagnostic message",
        )

        assert issue.severity == "error"
        assert issue.code == "test_code"
        assert issue.diagnostics == "Test diagnostic message"
        assert issue.value is None
        assert issue.expression is None

    def test_create_validation_issue_with_all_fields(self) -> None:
        """Test creating ValidationIssue with all fields."""
        issue = ValidationIssue(
            value="invalid_value",
            severity="warning",
            code="field_warning",
            diagnostics="This field has a warning",
            expression=["field1", "field2"],
        )

        assert issue.value == "invalid_value"
        assert issue.severity == "warning"
        assert issue.code == "field_warning"
        assert issue.diagnostics == "This field has a warning"
        assert issue.expression == ["field1", "field2"]

    def test_validation_issue_with_none_value(self) -> None:
        """Test that value can be explicitly set to None."""
        issue = ValidationIssue(
            value=None,
            severity="error",
            code="test_code",
            diagnostics="Test message",
        )

        assert issue.value is None

    def test_validation_issue_with_various_value_types(self) -> None:
        """Test that value can be various types."""
        # String value
        issue_str = ValidationIssue(
            value="test_string",
            severity="error",
            code="test",
            diagnostics="msg",
        )
        assert issue_str.value == "test_string"

        # Integer value
        issue_int = ValidationIssue(
            value=12345,
            severity="error",
            code="test",
            diagnostics="msg",
        )
        assert issue_int.value == 12345

        # Dict value
        issue_dict = ValidationIssue(
            value={"key": "value"},
            severity="error",
            code="test",
            diagnostics="msg",
        )
        assert issue_dict.value == {"key": "value"}

    def test_validation_issue_model_dump_json(self) -> None:
        """Test ValidationIssue serialization to JSON."""
        issue = ValidationIssue(
            value="test",
            severity="fatal",
            code="critical_error",
            diagnostics="A critical error occurred",
            expression=["field_name"],
        )

        dumped = issue.model_dump(mode="json")

        assert dumped["value"] == "test"
        assert dumped["severity"] == "fatal"
        assert dumped["code"] == "critical_error"
        assert dumped["diagnostics"] == "A critical error occurred"
        assert dumped["expression"] == ["field_name"]

    def test_validation_issue_with_empty_expression_list(self) -> None:
        """Test ValidationIssue with empty expression list."""
        issue = ValidationIssue(
            severity="information",
            code="info_code",
            diagnostics="Info message",
            expression=[],
        )

        assert issue.expression == []


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_create_validation_result(self) -> None:
        """Test creating ValidationResult with required fields."""
        result = ValidationResult[str](
            origin_record_id=12345,
            issues=[],
            sanitised="sanitised_value",
        )

        assert result.origin_record_id == 12345
        assert result.issues == []
        assert result.sanitised == "sanitised_value"

    def test_validation_result_with_issues(self) -> None:
        """Test ValidationResult with issues list."""
        issues = [
            ValidationIssue(
                severity="error",
                code="error_1",
                diagnostics="First error",
            ),
            ValidationIssue(
                severity="warning",
                code="warning_1",
                diagnostics="First warning",
            ),
        ]

        result = ValidationResult[str](
            origin_record_id=1,
            issues=issues,
            sanitised="value",
        )

        assert len(result.issues) == 2
        assert result.issues[0].code == "error_1"
        assert result.issues[1].code == "warning_1"

    def test_is_valid_with_no_issues(self) -> None:
        """Test is_valid returns True when no issues."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[],
            sanitised="value",
        )

        assert result.is_valid is True

    def test_is_valid_with_warning_issues(self) -> None:
        """Test is_valid returns True when only warnings."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="warning",
                    code="warn",
                    diagnostics="Warning message",
                ),
            ],
            sanitised="value",
        )

        assert result.is_valid is True

    def test_is_valid_with_information_issues(self) -> None:
        """Test is_valid returns True when only information issues."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="information",
                    code="info",
                    diagnostics="Info message",
                ),
            ],
            sanitised="value",
        )

        assert result.is_valid is True

    def test_is_valid_with_success_issues(self) -> None:
        """Test is_valid returns True when only success issues."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="success",
                    code="success",
                    diagnostics="Success message",
                ),
            ],
            sanitised="value",
        )

        assert result.is_valid is True

    def test_is_valid_with_error_issues(self) -> None:
        """Test is_valid returns False when error issues present."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="error",
                    code="error",
                    diagnostics="Error message",
                ),
            ],
            sanitised="value",
        )

        assert result.is_valid is False

    def test_is_valid_with_fatal_issues(self) -> None:
        """Test is_valid returns False when fatal issues present."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="fatal",
                    code="fatal",
                    diagnostics="Fatal message",
                ),
            ],
            sanitised="value",
        )

        assert result.is_valid is False

    def test_is_valid_with_mixed_issues(self) -> None:
        """Test is_valid returns False when mix of issues including error."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="warning",
                    code="warning",
                    diagnostics="Warning",
                ),
                ValidationIssue(
                    severity="error",
                    code="error",
                    diagnostics="Error",
                ),
            ],
            sanitised="value",
        )

        assert result.is_valid is False

    def test_should_continue_with_no_issues(self) -> None:
        """Test should_continue returns True when no issues."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[],
            sanitised="value",
        )

        assert result.should_continue is True

    def test_should_continue_with_error_issues(self) -> None:
        """Test should_continue returns True when only error issues (not fatal)."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="error",
                    code="error",
                    diagnostics="Error message",
                ),
            ],
            sanitised="value",
        )

        assert result.should_continue is True

    def test_should_continue_with_fatal_issues(self) -> None:
        """Test should_continue returns False when fatal issues present."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="fatal",
                    code="fatal",
                    diagnostics="Fatal message",
                ),
            ],
            sanitised="value",
        )

        assert result.should_continue is False

    def test_should_continue_with_warnings_and_errors(self) -> None:
        """Test should_continue returns True when only warnings and errors."""
        result = ValidationResult[str](
            origin_record_id=1,
            issues=[
                ValidationIssue(
                    severity="warning",
                    code="warning",
                    diagnostics="Warning",
                ),
                ValidationIssue(
                    severity="error",
                    code="error",
                    diagnostics="Error",
                ),
            ],
            sanitised="value",
        )

        assert result.should_continue is True

    def test_validation_result_model_dump_json(self) -> None:
        """Test ValidationResult serialization to JSON."""
        result = ValidationResult[str](
            origin_record_id=999,
            issues=[
                ValidationIssue(
                    severity="warning",
                    code="test_warning",
                    diagnostics="Test warning message",
                ),
            ],
            sanitised="sanitised_string",
        )

        dumped = result.model_dump(mode="json")

        assert dumped["origin_record_id"] == 999
        assert len(dumped["issues"]) == 1
        assert dumped["issues"][0]["code"] == "test_warning"
        assert dumped["sanitised"] == "sanitised_string"

    def test_validation_result_with_dict_sanitised(self) -> None:
        """Test ValidationResult with dict as sanitised value."""
        result = ValidationResult[dict](
            origin_record_id=1,
            issues=[],
            sanitised={"key": "value", "nested": {"inner": 123}},
        )

        assert result.sanitised == {"key": "value", "nested": {"inner": 123}}
        assert result.is_valid is True
