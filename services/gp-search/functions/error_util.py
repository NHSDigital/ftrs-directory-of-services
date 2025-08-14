from typing import Any, Dict, Type

from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from functions.organization_query_params import (
    InvalidIdentifierSystem,
    InvalidRevincludeError,
    ODSCodeInvalidFormatError,
)

INVALID_SEARCH_DATA_CODING: dict[str, list] = {
    "coding": [
        {
            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode",
            "version": "1.0.0",
            "code": "INVALID_SEARCH_DATA",
            "display": "Invalid search data",
        }
    ]
}

VALUE_ERROR_MAPPINGS: dict[Type[ValueError], dict] = {
    InvalidIdentifierSystem: {"code": "code-invalid", "severity": "error"},
    ODSCodeInvalidFormatError: {"code": "value", "severity": "error"},
    InvalidRevincludeError: {"code": "value", "severity": "error"},
}


def create_resource_internal_server_error() -> OperationOutcome:
    return OperationOutcome.model_validate(
        {
            "issue": [
                _create_issue("structure", "fatal", diagnostics="Internal server error")
            ]
        }
    )


def create_validation_error_operation_outcome(
    exception: ValidationError,
) -> OperationOutcome:
    return OperationOutcome.model_validate(
        {"issue": [_create_issue_from_error(error) for error in exception.errors()]}
    )


def _create_issue_from_error(error: ErrorDetails) -> Dict[str, Any]:
    if error.get("type") == "value_error":
        if custom_error := error.get("ctx", {}).get("error"):
            return _handle_custom_error(custom_error)

    if error.get("type") == "missing":
        return _create_issue(
            "required",
            "error",
            details=INVALID_SEARCH_DATA_CODING,
            diagnostics=f"Missing required search parameter '{error.get('loc')[0]}'",
        )

    return _create_issue("structure", "fatal", diagnostics="Internal server error")


def _handle_custom_error(custom_error: ValueError) -> dict:
    if error_config := VALUE_ERROR_MAPPINGS.get(type(custom_error)):
        return _create_issue(
            error_config["code"],
            error_config["severity"],
            details=INVALID_SEARCH_DATA_CODING,
            diagnostics=str(custom_error),
        )
    return _create_issue("structure", "fatal", diagnostics="Internal server error")


def _create_issue(
    code: str,
    severity: str,
    details: dict | None = None,
    diagnostics: str | None = None,
) -> dict:
    issue: dict = {"severity": severity, "code": code}
    if details:
        issue["details"] = details
    if diagnostics:
        issue["diagnostics"] = diagnostics
    return issue
