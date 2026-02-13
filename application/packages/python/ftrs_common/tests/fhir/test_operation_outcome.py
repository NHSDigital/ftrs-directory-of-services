from ftrs_common.fhir.operation_outcome import (
    FHIR_OPERATION_OUTCOME_CODES,
    OPERATION_OUTCOME_SYSTEM,
    OperationOutcomeException,
    OperationOutcomeHandler,
)
from pydantic import ValidationError


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
    assert (
        outcome["issue"][0]["details"]["coding"][0]["system"]
        == OPERATION_OUTCOME_SYSTEM
    )
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
    assert (
        outcome["issue"][0]["details"]["coding"][0]["system"]
        == OPERATION_OUTCOME_SYSTEM
    )
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
    assert (
        outcome["issue"][0]["details"]["coding"][0]["system"]
        == OPERATION_OUTCOME_SYSTEM
    )
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
        ),
        "not-found": (
            "NOT_FOUND",
            "The Server was unable to find the specified resource.",
        ),
        "exception": (
            "SERVER_ERROR",
            "The Server has encountered an error processing the request.",
        ),
        "structure": ("BAD_REQUEST", "The Server was unable to process the request."),
        "required": ("MSG_RESOURCE_REQUIRED", "A resource is required"),
        "value": ("MSG_PARAM_INVALID", "Parameter content is invalid"),
        "processing": (
            "MSG_ERROR_PARSING",
            "The Server has encountered an error processing the request.",
        ),
        "duplicate": ("CONFLICT", "The Server identified a conflict."),
        "informational": ("MSG_UPDATED", "Existing resource updated"),
        "success": ("MSG_UPDATED", "Existing resource updated"),
    }
    for code, expected in expected_mappings.items():
        assert FHIR_OPERATION_OUTCOME_CODES[code] == expected


def test_build_details_helper() -> None:
    """Test the _build_details helper method."""
    details = OperationOutcomeHandler._build_details("invalid", "Test text")
    assert details["coding"][0]["system"] == OPERATION_OUTCOME_SYSTEM
    assert details["coding"][0]["code"] == "UNPROCESSABLE_ENTITY"
    assert (
        details["coding"][0]["display"]
        == "Message was not malformed but deemed unprocessable by the server."
    )
    assert details["text"] == "Test text"
