from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.error_util import (
    INVALID_SEARCH_DATA_CODING,
    REC_BAD_REQUEST_CODING,
    _create_issue,
    create_invalid_header_operation_outcome,
    create_resource_internal_server_error,
    create_validation_error_operation_outcome,
)
from functions.organization_query_params import OrganizationQueryParams


class TestErrorUtil:
    def test_create_resource_internal_server_error(self):
        # Act
        result = create_resource_internal_server_error()

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "fatal"
        assert result.issue[0].code == "exception"
        assert result.issue[0].diagnostics == "Internal server error"
        assert result.issue[0].details is None

    def test_create_validation_error_invalid_ods_code_format(self):
        # Arrange - ODS code too short
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier="odsOrganisationCode|ABC",
                _revinclude="Endpoint:organization",
            )
        except ValidationError as e:
            validation_error = e

        # Act
        result = create_validation_error_operation_outcome(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "value"
        assert (
            result.issue[0].diagnostics
            == "Invalid identifier value: ODS code 'ABC' must follow format ^[A-Za-z0-9]{5,12}$"
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_invalid_identifier_system(self):
        # Arrange - Wrong identifier system
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier="wrongSystem|ABC12345", _revinclude="Endpoint:organization"
            )
        except ValidationError as e:
            validation_error = e

        # Act
        result = create_validation_error_operation_outcome(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "code-invalid"
        assert (
            result.issue[0].diagnostics
            == "Invalid identifier system 'wrongSystem' - expected 'odsOrganisationCode'"
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_invalid_rev_include(self):
        # Arrange - Invalid _revinclude value
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier="odsOrganisationCode|ABC12345",
                _revinclude="Invalid:value",
            )
        except ValidationError as e:
            validation_error = e

        # Act
        result = create_validation_error_operation_outcome(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "value"
        assert (
            result.issue[0].diagnostics
            == "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_missing_required_field(self):
        # Arrange - Missing required _revinclude parameter
        validation_error = None
        try:
            OrganizationQueryParams(identifier="odsOrganisationCode|ABC12345")
        except ValidationError as e:
            validation_error = e

        # Act
        result = create_validation_error_operation_outcome(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "required"
        assert (
            result.issue[0].diagnostics
            == "Missing required search parameter '_revinclude'"
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_multiple_issues(self):
        # Arrange - ODS code too short and Invalid _revinclude value
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier="odsOrganisationCode|ABC",
                _revinclude="Invalid:value",
            )
        except ValidationError as e:
            validation_error = e

        # Act
        result = create_validation_error_operation_outcome(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 2

        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "value"
        assert (
            result.issue[0].diagnostics
            == "Invalid identifier value: ODS code 'ABC' must follow format ^[A-Za-z0-9]{5,12}$"
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

        assert result.issue[1].severity == "error"
        assert result.issue[1].code == "value"
        assert (
            result.issue[1].diagnostics
            == "The request is missing the '_revinclude=Endpoint:organization' parameter, which is required to include linked Endpoint resources."
        )
        assert result.issue[1].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_unknown_error_type(self):
        # Use a valid Pydantic error type to exercise fallback (not 'value_error' or 'missing')
        err = ValidationError.from_exception_data(
            "ValidationError",
            [
                {
                    "type": "string_type",
                    "loc": ("identifier",),
                    "msg": "Input should be a valid string",
                    "input": None,
                }
            ],
        )
        result = create_validation_error_operation_outcome(err)
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        # Updated fallback expectations: client error, not internal fatal
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "invalid"
        assert result.issue[0].diagnostics == "Input should be a valid string"

    def test_create_validation_error_unmapped_value_error(self):
        # Simulate a value_error with an unmapped custom error class
        class UnknownCustomError(ValueError):
            pass

        err = ValidationError.from_exception_data(
            "ValidationError",
            [
                {
                    "type": "value_error",
                    "loc": ("identifier",),
                    "msg": "value error",
                    "input": None,
                    "ctx": {"error": UnknownCustomError("boom")},
                }
            ],
        )
        result = create_validation_error_operation_outcome(err)
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        # Updated fallback expectations: client error, not internal fatal
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "invalid"
        assert result.issue[0].diagnostics == "boom"

    def test_create_invalid_header_operation_outcome(self):
        headers = ["X-NHSD-Z", "Authorization"]

        result = create_invalid_header_operation_outcome(headers)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "value"
        assert issue.details.model_dump() == REC_BAD_REQUEST_CODING
        assert (
            issue.diagnostics
            == "Invalid request headers supplied: authorization, x-nhsd-z"
        )

    def test_create_invalid_header_operation_outcome_empty_list(self):
        # Test with empty list of headers
        result = create_invalid_header_operation_outcome([])

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "value"
        assert issue.diagnostics == "Invalid request headers supplied"

    def test_create_invalid_header_operation_outcome_single_header(self):
        # Test with single header
        headers = ["X-Custom-Header"]

        result = create_invalid_header_operation_outcome(headers)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert "x-custom-header" in result.issue[0].diagnostics

    def test_create_invalid_header_operation_outcome_sorts_headers(self):
        # Test that headers are sorted alphabetically
        headers = ["Z-Header", "A-Header", "M-Header"]

        result = create_invalid_header_operation_outcome(headers)

        diagnostics = result.issue[0].diagnostics
        assert (
            diagnostics
            == "Invalid request headers supplied: a-header, m-header, z-header"
        )

    def test_multiple_validation_errors(self):
        # Test handling of multiple validation errors at once
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier="odsOrganisationCode|ABC",  # Too short
                _revinclude="Wrong:value",  # Wrong revinclude
            )
        except ValidationError as e:
            validation_error = e

        result = create_validation_error_operation_outcome(validation_error)
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 2  # Should have 2 issues

    def test_create_issue_with_all_params(self):
        # Test _create_issue function through public API
        issue = _create_issue(
            "test-code",
            "warning",
            details={"test": "details"},
            diagnostics="Test diagnostics",
        )

        assert issue["code"] == "test-code"
        assert issue["severity"] == "warning"
        assert issue["details"] == {"test": "details"}
        assert issue["diagnostics"] == "Test diagnostics"

    def test_create_issue_without_optional_params(self):
        # Test _create_issue without optional parameters
        issue = _create_issue("test-code", "error")

        assert issue["code"] == "test-code"
        assert issue["severity"] == "error"
        assert "details" not in issue
        assert "diagnostics" not in issue

    def test_create_issue_with_none_diagnostics(self):
        # Test _create_issue with None diagnostics
        issue = _create_issue("test-code", "error", diagnostics=None)

        assert issue["code"] == "test-code"
        assert issue["severity"] == "error"
        assert "diagnostics" not in issue

    def test_handle_custom_error_with_empty_message(self):
        # Test custom ValueError with empty message
        class CustomValueError(ValueError):
            pass

        err = ValidationError.from_exception_data(
            "ValidationError",
            [
                {
                    "type": "value_error",
                    "loc": ("field",),
                    "msg": "value error",
                    "input": None,
                    "ctx": {"error": CustomValueError("")},
                }
            ],
        )
        result = create_validation_error_operation_outcome(err)
        assert isinstance(result, OperationOutcome)
        assert result.issue[0].diagnostics == "Invalid search parameter value"

    def test_create_validation_error_unexpected_query_param(self) -> None:
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier="odsOrganisationCode|ABC12345",
                _revinclude="Endpoint:organization",
                foo="bar",
            )
        except ValidationError as exc:
            validation_error = exc

        assert validation_error is not None

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1

        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "invalid"

        diagnostics = issue.diagnostics or ""
        assert "Unexpected query parameter" in diagnostics
        assert "foo" in diagnostics
        assert "identifier" in diagnostics
        assert "_revinclude" in diagnostics
