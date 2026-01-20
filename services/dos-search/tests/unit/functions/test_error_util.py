from __future__ import annotations

from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError

from functions.libraries.error_util import (
    INVALID_SEARCH_DATA_CODING,
    REC_BAD_REQUEST_CODING,
    create_invalid_header_operation_outcome,
    create_resource_internal_server_error,
    create_validation_error_operation_outcome,
)
from functions.libraries.organization_query_params import OrganizationQueryParams


class TestErrorUtil:
    def test_create_resource_internal_server_error(self) -> None:
        # Act
        result = create_resource_internal_server_error()

        # Assert
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        assert result.issue[0].severity == "fatal"
        assert result.issue[0].code == "exception"
        assert result.issue[0].diagnostics == "Internal server error"
        assert result.issue[0].details is None

    def test_create_validation_error_invalid_ods_code_format(self) -> None:
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

    def test_create_validation_error_invalid_identifier_system(self) -> None:
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

    def test_create_validation_error_invalid_rev_include(self) -> None:
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

    def test_create_validation_error_missing_required_field(self) -> None:
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

    def test_create_validation_error_multiple_issues(self) -> None:
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

    def test_create_validation_error_unknown_error_type(self) -> None:
        # Use a valid Pydantic error type to exercise fallback (not 'value_error' or 'missing')
        err = ValidationError.from_exception_data(
            "ValidationError",
            [
                dict(
                    type="string_type",
                    loc=("identifier",),
                    msg="Input should be a valid string",
                    input=None,
                )
            ],
        )
        result = create_validation_error_operation_outcome(err)
        assert isinstance(result, OperationOutcome)
        assert len(result.issue) == 1
        # Updated fallback expectations: client error, not internal fatal
        assert result.issue[0].severity == "error"
        assert result.issue[0].code == "invalid"
        assert result.issue[0].diagnostics == "Input should be a valid string"

    def test_create_validation_error_unmapped_value_error(self) -> None:
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

    def test_create_invalid_header_operation_outcome(self) -> None:
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
