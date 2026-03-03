from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Type

from fhir.resources.R4B.operationoutcome import OperationOutcome
from pydantic import ValidationError
from pydantic_core import ErrorDetails

from functions.healthcare_service_query_params import (
    HealthcareServiceQueryParams,
    HsInvalidIdentifierSystem,
    HsODSCodeInvalidFormatError,
)
from functions.organization_headers import (
    NHSD_REQUEST_ID,
    X_REQUEST_ID,
    InvalidVersionError,
    OrganizationHeaders,
)
from functions.organization_query_params import (
    InvalidIdentifierSystem,
    InvalidRevincludeError,
    ODSCodeInvalidFormatError,
    OrganizationQueryParams,
)

FRIENDLY_NAME_HEADERS = "header"
FRIENDLY_NAME_QUERY_PARAMETERS = "query parameter"


@dataclass
class ErrorDetail:
    field: str
    value: Any
    custom_error: ValueError | None


@dataclass
class ErrorGroup:
    error_type: str
    friendly_name: str
    error_details: list[ErrorDetail]
    model_name: str = ""


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

REC_BAD_REQUEST_CODING: dict[str, list] = {
    "coding": [
        {
            "system": "https://fhir.nhs.uk/CodeSystem/http-error-codes",
            "version": "1",
            "code": "REC_BAD_REQUEST",
            "display": "400: The Receiver was unable to process the request.",
        }
    ]
}

VALUE_ERROR_MAPPINGS: dict[Type[ValueError], dict[str, str]] = {
    InvalidIdentifierSystem: {"code": "code-invalid", "severity": "error"},
    ODSCodeInvalidFormatError: {"code": "value", "severity": "error"},
    InvalidRevincludeError: {"code": "value", "severity": "error"},
    # HealthcareService query params error types
    HsInvalidIdentifierSystem: {"code": "code-invalid", "severity": "error"},
    HsODSCodeInvalidFormatError: {"code": "value", "severity": "error"},
    InvalidVersionError: {"code": "value", "severity": "error"},
}

FRIENDLY_MODEL_NAME_MAP: dict[str, str] = {
    OrganizationQueryParams.__name__: FRIENDLY_NAME_QUERY_PARAMETERS,
    OrganizationHeaders.__name__: FRIENDLY_NAME_HEADERS,
    HealthcareServiceQueryParams.__name__: FRIENDLY_NAME_QUERY_PARAMETERS,
}

PROXY_HEADER_BY_INTERNAL_HEADER_MAP: dict[str, str] = {
    NHSD_REQUEST_ID: X_REQUEST_ID,
}

HEALTHCARE_SERVICE_ALIAS_MAP: dict[str, str] = {
    field_name: field_info.alias
    for field_name, field_info in HealthcareServiceQueryParams.model_fields.items()
    if field_info.alias and field_info.alias != field_name
}


def create_resource_internal_server_error() -> OperationOutcome:
    return OperationOutcome.model_validate(
        {
            "issue": [
                _create_issue("exception", "fatal", diagnostics="Internal server error")
            ]
        }
    )


def create_resource_service_unavailable_error() -> OperationOutcome:
    return OperationOutcome.model_validate(
        {
            "issue": [
                _create_issue(
                    "exception",
                    "fatal",
                    diagnostics="Service Unavailable: Healthcare Service search endpoint is currently disabled",
                )
            ]
        }
    )


def create_validation_error_operation_outcome(
    exception: ValidationError,
) -> OperationOutcome:
    error_groups = _extract_validation_error_error_details_by_type(exception)

    issues = [
        issue
        for error_group in error_groups
        for issue in _create_issues_from_error(error_group)
    ]

    return OperationOutcome.model_validate({"issue": issues})


def _get_allowed_query_params(model_name: str) -> list[str]:
    """Get required query parameter aliases for the given model."""
    if model_name == OrganizationQueryParams.__name__:
        return OrganizationQueryParams.get_required_query_params()
    if model_name == HealthcareServiceQueryParams.__name__:
        return HealthcareServiceQueryParams.get_required_query_params()
    return []


def _create_issues_from_error(error_group: ErrorGroup) -> list[dict[str, Any]]:
    issues = []

    if error_group.error_type == "extra_forbidden":
        unexpected = ", ".join(
            [error_detail.field for error_detail in error_group.error_details]
        )
        diagnostics = f"Unexpected {error_group.friendly_name}(s): {unexpected}."
        if error_group.friendly_name == FRIENDLY_NAME_QUERY_PARAMETERS:
            allowed = _get_allowed_query_params(error_group.model_name)
            if len(allowed) == 1:
                diagnostics += f" Only '{allowed[0]}' is allowed."
            else:
                joined = " and ".join(f"'{f}'" for f in allowed)
                diagnostics += f" Only {joined} are allowed."
        issues.append(
            _create_issue(
                "value",
                "error",
                details=_get_details(error_group),
                diagnostics=diagnostics,
            )
        )

    elif error_group.error_type == "value_error":
        issues.extend(
            issue
            for error_field in error_group.error_details
            if (custom_error := error_field.custom_error)
            and (issue := _handle_custom_error(custom_error, error_group))
        )

    elif error_group.error_type == "missing":
        fields = ", ".join(
            f"'{error_detail.field}'" for error_detail in error_group.error_details
        )
        issues.append(
            _create_issue(
                "required",
                "error",
                details=_get_details(error_group),
                diagnostics=f"Missing required {error_group.friendly_name}(s): {fields}",
            )
        )

    # Any other pydantic error type: treat as generic client invalid input (400)
    if not issues:
        issues.append(
            _create_issue(
                "invalid",
                "error",
                details=_get_details(error_group),
                diagnostics=f"Invalid {error_group.friendly_name}",
            )
        )

    return issues


def _handle_custom_error(
    custom_error: ValueError, error_group: ErrorGroup
) -> dict | None:
    if error_config := VALUE_ERROR_MAPPINGS.get(type(custom_error)):
        return _create_issue(
            code=error_config["code"],
            severity=error_config["severity"],
            details=_get_details(error_group),
            diagnostics=str(custom_error),
        )

    return None


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


def _extract_validation_error_error_details_by_type(
    exception: ValidationError,
) -> list[ErrorGroup]:
    title = exception.title
    friendly_name = FRIENDLY_MODEL_NAME_MAP.get(title, "input")
    error_details_by_type = defaultdict(list)

    for error in exception.errors():
        error_type = error.get("type", "unknown")
        field_name = _extract_field_name(error, friendly_name)
        custom_error = (
            error.get("ctx", {}).get("error") if error_type == "value_error" else None
        )

        error_details_by_type[error_type].append(
            ErrorDetail(
                field=field_name, value=error.get("input"), custom_error=custom_error
            )
        )

    return [
        ErrorGroup(
            error_type=error_type,
            friendly_name=friendly_name,
            error_details=errors,
            model_name=title,
        )
        for error_type, errors in error_details_by_type.items()
    ]


def _extract_field_name(error: ErrorDetails, friendly_name: str) -> int | str:
    field_name = error.get("loc", ("unknown",))[0]

    if friendly_name == FRIENDLY_NAME_HEADERS:
        field_name = PROXY_HEADER_BY_INTERNAL_HEADER_MAP.get(field_name, field_name)
    elif friendly_name == FRIENDLY_NAME_QUERY_PARAMETERS:
        field_name = HEALTHCARE_SERVICE_ALIAS_MAP.get(field_name, field_name)

    return field_name


def _get_details(error_group: ErrorGroup) -> dict[str, list]:
    if error_group.friendly_name == FRIENDLY_NAME_QUERY_PARAMETERS:
        return INVALID_SEARCH_DATA_CODING
    else:
        return REC_BAD_REQUEST_CODING
