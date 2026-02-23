import pytest
from ftrs_common.fhir.operation_outcome import (
    FHIR_OPERATION_OUTCOME_CODES,
    HTTP_ERROR,
    OPERATION_OUTCOME_SYSTEM,
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from pydantic import ValidationError


@pytest.mark.parametrize(
    "code,diagnostics,severity,expected_value",
    [
        (
            "invalid",
            "The provided resource is invalid.",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "UNPROCESSABLE_ENTITY",
                                    "display": "Message was not malformed but deemed unprocessable by the server.",
                                }
                            ],
                            "text": "The provided resource is invalid.",
                        }
                    }
                ]
            },
        ),
        (
            "not-found",
            "The Server was unable to find the specified resource.",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "NOT_FOUND",
                                    "display": "The Server was unable to find the specified resource.",
                                }
                            ],
                            "text": "The Server was unable to find the specified resource.",
                        }
                    }
                ]
            },
        ),
        (
            "exception",
            "The Server has encountered an error processing the request.",
            "fatal",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "SERVER_ERROR",
                                    "display": "The Server has encountered an error processing the request.",
                                }
                            ],
                            "text": "The Server has encountered an error processing the request.",
                        }
                    }
                ]
            },
        ),
        (
            "structure",
            "The Server was unable to process the request.",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "BAD_REQUEST",
                                    "display": "The Server was unable to process the request.",
                                }
                            ],
                            "text": "The Server was unable to process the request.",
                        }
                    }
                ]
            },
        ),
        (
            "required",
            "A resource is required",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "MSG_RESOURCE_REQUIRED",
                                    "display": "A resource is required",
                                }
                            ],
                            "text": "A resource is required",
                        }
                    }
                ]
            },
        ),
        (
            "value",
            "Parameter content is invalid",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "MSG_PARAM_INVALID",
                                    "display": "Parameter content is invalid",
                                }
                            ],
                            "text": "Parameter content is invalid",
                        }
                    }
                ]
            },
        ),
        (
            "processing",
            "The Server has encountered an error processing the request.",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "MSG_ERROR_PARSING",
                                    "display": "The Server has encountered an error processing the request.",
                                }
                            ],
                            "text": "The Server has encountered an error processing the request.",
                        }
                    }
                ]
            },
        ),
        (
            "duplicate",
            "The Server identified a conflict.",
            "error",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": HTTP_ERROR,
                                    "code": "CONFLICT",
                                    "display": "The Server identified a conflict.",
                                }
                            ],
                            "text": "The Server identified a conflict.",
                        }
                    }
                ]
            },
        ),
        (
            "informational",
            "Existing resource updated",
            "information",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": OPERATION_OUTCOME_SYSTEM,
                                    "code": "MSG_UPDATED",
                                    "display": "Existing resource updated",
                                }
                            ],
                            "text": "Existing resource updated",
                        }
                    }
                ]
            },
        ),
        (
            "success",
            "Existing resource updated",
            "information",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": OPERATION_OUTCOME_SYSTEM,
                                    "code": "MSG_UPDATED",
                                    "display": "Existing resource updated",
                                }
                            ],
                            "text": "Existing resource updated",
                        }
                    }
                ]
            },
        ),
        (
            "not-updated",
            "no changes made to org",
            "information",
            {
                "issue": [
                    {
                        "details": {
                            "coding": [
                                {
                                    "system": OPERATION_OUTCOME_SYSTEM,
                                    "code": "MSG_NOT_UPDATED",
                                    "display": "Existing resource not updated",
                                }
                            ],
                            "text": "no changes made to org",
                        }
                    }
                ]
            },
        ),
    ],
)
def test_operation_outcome_build_parametrized(
    code: str, diagnostics: str, severity: str, expected_value: dict
) -> None:
    outcome = OperationOutcomeHandler.build(
        diagnostics=diagnostics,
        code=code,
        severity=severity,
    )
    assert outcome["issue"][0]["diagnostics"] == diagnostics
    assert outcome["issue"][0]["code"] == code
    assert outcome["issue"][0]["severity"] == severity
    assert (
        outcome["issue"][0]["details"]["coding"][0]["system"]
        == expected_value["issue"][0]["details"]["coding"][0]["system"]
    )
    assert (
        outcome["issue"][0]["details"]["coding"][0]["code"]
        == expected_value["issue"][0]["details"]["coding"][0]["code"]
    )
    assert (
        outcome["issue"][0]["details"]["coding"][0]["display"]
        == expected_value["issue"][0]["details"]["coding"][0]["display"]
    )
    assert (
        outcome["issue"][0]["details"]["text"]
        == expected_value["issue"][0]["details"]["text"]
    )


def test_operation_outcome_exception_message() -> None:
    outcome = {"issue": [{"diagnostics": "Something went wrong"}]}
    exc = OperationOutcomeException(outcome)
    assert exc.outcome == outcome
    assert str(exc) == "Something went wrong"


def test_operation_outcome_exception_default_message() -> None:
    outcome = {"issue": [{}]}
    exc = OperationOutcomeException(outcome)
    assert str(exc) == "FHIR OperationOutcome error"


def test_operation_outcome_handler_build_basic() -> None:
    diagnostics = "Test diagnostics"
    outcome = OperationOutcomeHandler.build(diagnostics)
    assert isinstance(outcome, dict)
    assert outcome["issue"][0]["diagnostics"] == diagnostics
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["severity"] == "error"
    assert "details" in outcome["issue"][0]
    assert "coding" in outcome["issue"][0]["details"]
    assert outcome["issue"][0]["details"]["coding"][0]["system"] == HTTP_ERROR
    assert outcome["issue"][0]["details"]["coding"][0]["code"] == "UNPROCESSABLE_ENTITY"
    assert (
        outcome["issue"][0]["details"]["coding"][0]["display"]
        == "Message was not malformed but deemed unprocessable by the server."
    )
    assert outcome["issue"][0]["details"]["text"] == diagnostics


def test_operation_outcome_handler_build_with_details_and_issues() -> None:
    diagnostics = "Test diagnostics"
    details = {"text": "More info"}
    issues = [{"severity": "warning", "code": "processing", "diagnostics": "Warn"}]
    outcome = OperationOutcomeHandler.build(diagnostics, details=details, issues=issues)
    assert outcome["issue"][0]["severity"] == "warning"
    assert outcome["issue"][0]["diagnostics"] == "Warn"


def test_operation_outcome_handler_build_with_custom_code() -> None:
    diagnostics: str = "Resource not found"
    outcome = OperationOutcomeHandler.build(
        diagnostics, code="not-found", severity="error"
    )
    assert outcome["issue"][0]["code"] == "not-found"
    assert outcome["issue"][0]["details"]["coding"][0]["code"] == "NOT_FOUND"
    assert (
        outcome["issue"][0]["details"]["coding"][0]["display"]
        == "The Server was unable to find the specified resource."
    )


def test_operation_outcome_handler_build_with_unknown_code() -> None:
    diagnostics: str = "Unknown error"
    outcome = OperationOutcomeHandler.build(diagnostics, code="unknown-code")
    assert outcome["issue"][0]["details"]["coding"][0]["code"] == "SERVER_ERROR"
    assert (
        outcome["issue"][0]["details"]["coding"][0]["display"]
        == "The Server has encountered an error processing the request."
    )


def test_operation_outcome_handler_build_with_details_text() -> None:
    diagnostics: str = "Detailed diagnostics"
    details_text: str = "Human readable text"
    outcome = OperationOutcomeHandler.build(diagnostics, details_text=details_text)
    assert outcome["issue"][0]["diagnostics"] == diagnostics
    assert outcome["issue"][0]["details"]["text"] == details_text


def test_operation_outcome_handler_build_with_expression() -> None:
    diagnostics: str = "Invalid field"
    expression: list[str] = ["Organization.identifier[0].value"]
    outcome = OperationOutcomeHandler.build(diagnostics, expression=expression)
    assert outcome["issue"][0]["expression"] == expression


def test_operation_outcome_handler_build_with_custom_details() -> None:
    diagnostics: str = "Test diagnostics"
    custom_details: dict = {
        "coding": [
            {
                "system": "https://custom.system",
                "code": "CUSTOM_CODE",
                "display": "Custom Display",
            }
        ],
        "text": "Custom text",
    }
    outcome = OperationOutcomeHandler.build(diagnostics, details=custom_details)
    assert outcome["issue"][0]["details"] == custom_details


def test_operation_outcome_handler_build_with_issues() -> None:
    diagnostics: str = "Test diagnostics"
    details: dict = {"text": "More info"}
    issues: list = [
        {
            "severity": "warning",
            "code": "processing",
            "diagnostics": "Warn",
            "details": {"text": "Warning details"},
        }
    ]
    outcome = OperationOutcomeHandler.build(diagnostics, details=details, issues=issues)
    assert outcome["issue"][0]["severity"] == "warning"
    assert outcome["issue"][0]["diagnostics"] == "Warn"


def test_operation_outcome_handler_from_exception() -> None:
    exc = Exception("Boom!")
    outcome = OperationOutcomeHandler.from_exception(exc)
    assert outcome["issue"][0]["diagnostics"] == "Boom!"
    assert outcome["issue"][0]["code"] == "exception"
    assert outcome["issue"][0]["severity"] == "fatal"
    assert outcome["issue"][0]["details"]["coding"][0]["system"] == HTTP_ERROR
    assert outcome["issue"][0]["details"]["coding"][0]["code"] == "SERVER_ERROR"
    assert (
        outcome["issue"][0]["details"]["coding"][0]["display"]
        == "The Server has encountered an error processing the request."
    )
    assert "An unexpected error occurred" in outcome["issue"][0]["details"]["text"]


def test_operation_outcome_handler_from_validation_error() -> None:
    dummy_model_path: str = "tests.fhir.test_operation_outcome.DummyModel"

    error = ValidationError.from_exception_data(
        dummy_model_path,
        [
            {
                "type": "value_error",
                "loc": ("foo",),
                "msg": "Fake error",
                "input": "bad_value",
                "ctx": {"error": ValueError("Fake error")},
            }
        ],
    )
    outcome = OperationOutcomeHandler.from_validation_error(error)
    assert outcome["issue"][0]["diagnostics"] == "Validation failed for resource."
    assert outcome["issue"][0]["code"] == "invalid"
    assert outcome["issue"][0]["severity"] == "error"
    assert outcome["issue"][0]["details"]["coding"][0]["system"] == HTTP_ERROR
    assert outcome["issue"][0]["details"]["coding"][0]["code"] == "UNPROCESSABLE_ENTITY"
    assert (
        outcome["issue"][0]["details"]["coding"][0]["display"]
        == "Message was not malformed but deemed unprocessable by the server."
    )


def test_fhir_operation_outcome_codes_mapping() -> None:
    """Test that all expected codes are mapped correctly."""
    expected_mappings: dict[str, tuple[str, str]] = {
        "invalid": (
            "UNPROCESSABLE_ENTITY",
            "Message was not malformed but deemed unprocessable by the server.",
            HTTP_ERROR,
        ),
        "not-found": (
            "NOT_FOUND",
            "The Server was unable to find the specified resource.",
            HTTP_ERROR,
        ),
        "exception": (
            "SERVER_ERROR",
            "The Server has encountered an error processing the request.",
            HTTP_ERROR,
        ),
        "structure": (
            "BAD_REQUEST",
            "The Server was unable to process the request.",
            HTTP_ERROR,
        ),
        "required": ("MSG_RESOURCE_REQUIRED", "A resource is required", HTTP_ERROR),
        "value": ("MSG_PARAM_INVALID", "Parameter content is invalid", HTTP_ERROR),
        "processing": (
            "MSG_ERROR_PARSING",
            "The Server has encountered an error processing the request.",
            HTTP_ERROR,
        ),
        "duplicate": ("CONFLICT", "The Server identified a conflict.", HTTP_ERROR),
        "informational": (
            "MSG_UPDATED",
            "Existing resource updated",
            OPERATION_OUTCOME_SYSTEM,
        ),
        "success": (
            "MSG_UPDATED",
            "Existing resource updated",
            OPERATION_OUTCOME_SYSTEM,
        ),
        "not-updated": (
            "MSG_NOT_UPDATED",
            "Existing resource not updated",
            OPERATION_OUTCOME_SYSTEM,
        ),
    }
    for code, expected in expected_mappings.items():
        assert FHIR_OPERATION_OUTCOME_CODES[code] == expected


def test_build_details_helper() -> None:
    """Test the _build_details helper method."""
    details = OperationOutcomeHandler._build_details("invalid", "Test text")
    assert details["coding"][0]["system"] == HTTP_ERROR
    assert details["coding"][0]["code"] == "UNPROCESSABLE_ENTITY"
    assert (
        details["coding"][0]["display"]
        == "Message was not malformed but deemed unprocessable by the server."
    )
    assert details["text"] == "Test text"
