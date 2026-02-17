from collections.abc import Callable

from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import BaseModel, ValidationError

from functions.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)
from functions.error_util import (
    INVALID_SEARCH_DATA_CODING,
    REC_BAD_REQUEST_CODING,
    _create_issue,
    create_resource_internal_server_error,
    create_validation_error_operation_outcome,
)
from functions.organization_headers import OrganizationHeaders
from functions.organization_query_params import OrganizationQueryParams


def _get_validation_error(
    model_build: Callable[[], BaseModel],
) -> ValidationError:
    try:
        model_build()
    except ValidationError as e:
        return e
    raise AssertionError("Expected a ValidationError but model built successfully")  # noqa: TRY003


REQUIRED_HEADERS = {
    "Authorization": "Bearer abcdefg",
    "NHSD-Request-ID": "123456789",
    "Version": "1",
}


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
        validation_error = _get_validation_error(
            lambda: OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC",
                _revinclude=REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
            )
        )
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
        validation_error = _get_validation_error(
            lambda: OrganizationQueryParams(
                identifier="wrongSystem|ABC12345",
                _revinclude=REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
            )
        )

        # Act
        result = create_validation_error_operation_outcome(validation_error)

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "code-invalid"
        assert (
            result.issue[0].diagnostics
            == f"Invalid identifier system 'wrongSystem' - expected '{ODS_ORG_CODE_IDENTIFIER_SYSTEM}'"
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_invalid_rev_include(self):
        # Arrange - Invalid _revinclude value
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC12345",
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
            == f"The request is missing the '_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}' parameter, which is required to include linked Endpoint resources."
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_missing_required_field(self):
        # Arrange - Missing required _revinclude parameter
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC12345"
            )
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
            == "Missing required query parameter(s): '_revinclude'"
        )
        assert result.issue[0].details.model_dump() == INVALID_SEARCH_DATA_CODING

    def test_create_validation_error_multiple_issues(self):
        # Arrange - ODS code too short and Invalid _revinclude value
        validation_error = None
        try:
            OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC",
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
            == f"The request is missing the '_revinclude={REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION}' parameter, which is required to include linked Endpoint resources."
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
        assert result.issue[0].diagnostics == "Invalid input"

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
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "invalid"
        assert result.issue[0].diagnostics == "Invalid input"

    def test_create_invalid_header_operation_outcome(self):
        # Arrange - non-allowed headers
        headers = {
            "X-NHSD-Z": "foo",
            "Random": "bar",
        } | REQUIRED_HEADERS

        validation_error = _get_validation_error(
            lambda: OrganizationHeaders.model_validate(headers)
        )

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "value"
        assert issue.details.model_dump() == REC_BAD_REQUEST_CODING
        assert issue.diagnostics == "Unexpected header(s): x-nhsd-z, random."

    def test_create_invalid_header_operation_outcome_single_header(self):
        # Test with single header
        headers = {
            "X-Custom-Header": "foo",
        } | REQUIRED_HEADERS

        validation_error = _get_validation_error(
            lambda: OrganizationHeaders.model_validate(headers)
        )

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert "x-custom-header" in result.issue[0].diagnostics

    def test_create_invalid_version_operation_outcome(self):
        headers = REQUIRED_HEADERS.copy()
        headers["Version"] = "2"

        validation_error = _get_validation_error(
            lambda: OrganizationHeaders.model_validate(headers)
        )

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "value"
        assert issue.details.model_dump() == REC_BAD_REQUEST_CODING
        assert (
            issue.diagnostics
            == "Invalid version found in supplied headers: version must be '1'"
        )

    def test_create_missing_mandatory_header_operation_outcome(self):
        headers = {"nhsd-request-id": "foo"}

        validation_error = _get_validation_error(
            lambda: OrganizationHeaders.model_validate(headers)
        )

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "required"
        assert issue.details.model_dump() == REC_BAD_REQUEST_CODING
        assert (
            issue.diagnostics
            == "Missing required header(s): 'authorization', 'version'"
        )

    def test_create_missing_mandatory_header_operation_outcome_empty_list(self):
        headers = {}

        validation_error = _get_validation_error(
            lambda: OrganizationHeaders.model_validate(headers)
        )

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "required"
        assert issue.details.model_dump() == REC_BAD_REQUEST_CODING
        assert (
            issue.diagnostics
            == "Missing required header(s): 'authorization', 'version', 'nhsd-request-id'"
        )

    def test_multiple_validation_errors(self):
        # Test handling of multiple validation errors at once
        validation_error = _get_validation_error(
            lambda: OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC",  # Too short
                _revinclude="Wrong:value",  # Wrong revinclude
            )
        )

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

    def test_create_validation_error_unexpected_query_param(self) -> None:
        validation_error = _get_validation_error(
            lambda: OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC12345",
                _revinclude=REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
                foo="bar",
            )
        )

        result = create_validation_error_operation_outcome(validation_error)

        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1

        issue = result.issue[0]
        assert issue.severity == "error"
        assert issue.code == "value"

        diagnostics = issue.diagnostics or ""
        assert "Unexpected query parameter" in diagnostics
        assert "foo" in diagnostics
        assert "identifier" in diagnostics
        assert "_revinclude" in diagnostics
